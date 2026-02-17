---
name: douyin-clone
description: 复刻抖音博主完整流程。从分析目标博主视频风格、选题规律、数据表现，到生成原创文案、AI配图、TTS配音、BGM合成、最终视频输出。当用户说"复刻博主"、"模仿抖音号"、"分析抖音博主"、"做一个类似XX的视频"、发抖音链接+「复刻」时触发。
---

# 复刻抖音博主

## 🚀 快速复刻模式（推荐）

**输入**：一个抖音视频链接 + 「复刻」指令
**系统自动完成**：分析视频风格 → 写原创文案 → 生成配图 → TTS配音 → BGM混音 → 字幕烧录 → 合成视频 → 交付

### 触发方式
用户只需：
1. 发一个抖音视频链接
2. 说「复刻」

### 自动判断模式
- **单视频链接 + 复刻**：分析该视频的风格+内容 → 同主题/相关主题写原创文案 → 用提取的风格模板生成配图 → TTS+BGM+字幕 → 合成视频交付
- **博主主页链接 + 复刻**：分析博主多个视频 → 提取统一风格 → 推荐选题 → 用户选题后生成视频
- **单视频链接 + 「复刻这个博主」**：先从该视频找到博主 → 抓取博主多个视频 → 走博主复刻流程

### 单视频快速复刻流程
```
1. 下载视频 + 抽帧 + 提取音频 + FunASR转录
2. AI逐帧分析画面，提取视觉风格模板（画风/色调/构图/光影/质感/文字排版）
3. 分析文案结构（开头hook类型/正文节奏/结尾套路）
4. 基于同主题写原创文案（模仿该视频的文案风格）
5. 用提取的风格模板生成配图（即梦）
6. TTS配音 + BGM混音（旁白volume=2.0, BGM volume=3.0）
7. 字幕烧录
8. 合成视频 → 上传腾讯云 → 交付高清链接 + 本地路径
```

---

完整流程分7个阶段，按顺序执行。
**每个步骤完成后必须推送进度到用户频道！** 不只是阶段级别，而是每个关键子步骤都要推送，包括但不限于：下载完成、抽帧完成、转录完成、风格分析完成、文案写好、提示词生成、每批图片生成进度、TTS完成、BGM提取完成、视频合成中、字幕烧录、上传链接等。
**TTS和生图可并行执行以提高效率。**

## ⚠️ 子代理Spawn规则

**所有子代理spawn时不设超时（不传runTimeoutSeconds），让子代理跑到完成为止！**
**即梦生图必须用标准spawn模板，不允许子代理自己写API调用代码！**

### 子代理拆分策略（防token爆满）

**禁止把全流程塞进一个子代理！必须按阶段拆分：**

```
子代理1：分析+文案（阶段1-4）
  → 分析视频、提取风格、写文案、拆场景、生成提示词
  → 产出：style_template.json, script.md, prompts.json

子代理2：TTS配音 + BGM提取（阶段5.2-5.3，与子代理3并行）
  → 产出：narration.mp3, bgm_clean.wav, mixed_audio.m4a

子代理3：即梦生图（阶段5.1，与子代理2并行）
  → 只做生图这一件事，逐个场景串行
  → 单账号单tab，不能并行提交
  → 产出：images/scene_01~XX.webp

子代理4：合成+评估+交付（阶段6-6.8）
  → 等子代理2和3都完成后启动
  → 合成视频、烧字幕、质量评估、上传、交付链接
  → 产出：final.mp4 + 评估报告
  → ⚠️ 必须包含质量评估步骤！截帧检查字幕同步、图片大小、风格匹配
  → ⚠️ 每完成一个主要步骤用message推送进度并标✅（合并音视频✅、字幕生成✅、烧录字幕✅、质量评估✅、上传✅）
```

**为什么这样拆：**
- 每个子代理只干一段活，token不会爆
- 子代理2（TTS）和子代理3（生图）可以并行，节省时间
- 生图用单独子代理串行跑（即梦单账号限制，多个并行会冲突）

**主会话协调逻辑：**
1. spawn子代理1 → 等完成
2. **读 style_template.json 的 content_type，决定子代理3的类型：**
   - `content_type == "配图口播"` → spawn即梦生图子代理（读 phase5a-jimeng-image.md）
   - `content_type == "视频类"` → spawn即梦视频子代理（读 phase5b-jimeng-video.md）
   - `content_type == "动画类"` → spawn Remotion子代理（读 phase5c-remotion.md）
3. 同时spawn子代理2（TTS+BGM）和子代理3（按类型） → 等两个都完成
4. spawn子代理4 → 等完成 → 交付

### 即梦生图子代理spawn模板：
```
sessions_spawn({
  label: "{主题}-视频制作",
  runTimeoutSeconds: 3600,
  task: `复刻「{博主名}」风格，制作主题「{主题}」的抖音视频。所有输出用中文。

【第一步：读配置文件！】
先读 skills/douyin-clone/config.json，所有路径、参数、阈值从这里取，不要写死！
即梦browser参数：profile和target从config.json读取。targetId每次用 browser tabs 动态获取，禁止写死！

【核心原则：复刻=严格模仿，不是原创！】
- 画风、色调、构图、文字排版 → 严格对标原视频，不要创新
- 文案结构、节奏、口吻 → 模仿对标视频的套路，不是自由发挥
- 风格识别用具体特征维度描述（线条/人物/上色/背景/质感/色调），禁止用"火柴人"等模糊标签
- 风格识别后，生成1张测试图，AI自动与参考帧对比校验，≥2个维度不一致就调整重试（最多2次）
- 提示词开头加："严格模仿参考视频的视觉风格，不要创新，不要改风格"

然后按需读对应阶段的phase文件（不要读整个SKILL.md）。

工作目录：D:\\video-analysis\\output\\{主题}\\
博主数据目录：D:\\video-analysis\\{博主名}\\

【前置检查】
1. 检查抖音体字体是否安装：
   if (!(Test-Path "C:\\Windows\\Fonts\\DouyinSansBold.ttf")) → 必须先下载安装！
2. 检查 style_template.json 是否存在（博主数据目录）

【即梦生图流程 - 严禁自己写JS/API代码！必须用脚本！】
1. browser tabs (profile="openclaw", target="host") 找到 jimeng.jianying.com 的 targetId
2. 对每个场景：
   a) chcp 65001 && python D:\\video-analysis\\scripts\\jimeng_fetch_gen.py --action generate --prompt "prompt" --ratio "16:9" --json
   b) browser evaluate执行返回的js
   c) 等3秒
   d) python D:\\video-analysis\\scripts\\jimeng_fetch_gen.py --action poll --submit-id "xxx" --json
   e) 间隔5秒轮询直到status=done
   f) curl下载图片到 images/scene_XX.webp
3. 每5张图发2-3张预览给用户（用message工具发送图片，不阻塞生图）

【字幕烧录 - 严格按phase6-compose.md执行！】
- 方案二：原始文案去标点 + FunASR时间戳对齐（丢弃ASR文字）
- ⚠️ ASR必须对合成后的视频音频做（含BGM+配音），不能对单独的TTS音频做！
- ⚠️ 不能线性映射时间戳！必须用ASR实际识别的时间戳！
- 字体/大小/位置参考对标视频，从style_template.json读取
- 读 phases/phase6-compose.md 中的「字幕生成代码」完整执行

【质量评估 - 必须步骤！不能跳过！】
1. 截取3帧（开头/中间/结尾）检查：字幕是否显示、图片大小是否合适、风格是否匹配
2. 播放5秒检查字幕与声音是否同步
3. 检查视频时长、分辨率、文件大小是否合理
4. 用message推送评估结果截图给用户
5. 有问题必须修复后再交付，不能带病交付

【视频完成后】
1. 上传到腾讯云：paramiko sftp到106.55.158.137，路径 /home/ubuntu/www/videos/{主题}.mp4
2. 发送高清链接：http://bm.weiixxin.com/videos/{主题}.mp4`
})
```

---

---

## 📂 阶段详细文档（子代理按需读取）

完整流程拆分为独立文件，子代理只需读取对应阶段的文件：

| 阶段 | 文件 | 内容 |
|------|------|------|
| 1-1.5 | `phases/phase1-data.md` | 抓取数据 + 账号类型识别 |
| 2-2.5 | `phases/phase2-analysis.md` | AI分析报告 + 风格模板提取 + 推荐选题 |
| 3 | `phases/phase3-script.md` | 写文案 |
| 4-4.5 | `phases/phase4-scenes.md` | 拆分场景 + 生成提示词 + 风格样片 |
| 5(通用) | `phases/phase5-common.md` | TTS配音 + BGM提取 + 质量校验（所有模式共用） |
| 5a | `phases/phase5a-jimeng-image.md` | 即梦AI配图（配图口播模式） |
| 5b | `phases/phase5b-jimeng-video.md` | 即梦视频生成（视频模式） |
| 5c | `phases/phase5c-remotion.md` | Remotion动画生成（动画模式） |
| 6-7 | `phases/phase6-compose.md` | 合成视频 + 上传 + 质量评估 + 发布 |

### 子代理Spawn时的读取规则
- **所有子代理第一步**：读 `config.json` 获取路径、参数、阈值
- **子代理1（分析+文案）**：读 `phases/phase1-data.md` + `phases/phase2-analysis.md`
- **子代理2（TTS+BGM）**：读 `phases/phase5-common.md`
- **子代理3（生图/视频/动画）**：根据content_type读对应文件 + `phases/phase5-common.md`
  - 配图口播 → `phases/phase5a-jimeng-image.md`
  - 视频模式 → `phases/phase5b-jimeng-video.md`
  - 动画模式 → `phases/phase5c-remotion.md`
- **子代理4（合成+交付）**：读 `phases/phase6-compose.md`
- **不要读整个SKILL.md！只读对应的phase文件！**
