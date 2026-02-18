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

## ⚠️ 主会话指挥官模式（Commander Pattern）

**核心原则：主会话掌控全局，子代理只做窄任务。**

主会话负责：
- 读skill文件、做决策、控制phase切换
- 检查每个phase的产出质量
- 决定下一步做什么

子代理负责：
- 执行具体的、命令级别的窄任务
- 不做决策、不读skill、不自由发挥
- 出错立即报告，不尝试替代方案

### 主会话执行流程

```
主会话读 SKILL.md + config.json，开始逐phase推进：

Phase 1-2: 数据获取 + 分析
  主会话读 phase1-data.md + phase2-analysis.md
  spawn子代理A: "用API下载视频{url}到{dir}，ffmpeg抽帧fps=1/5，提取音频，FunASR转录。完成后报告。"
  → 主会话收到结果，自己做AI分析（逐帧分析、风格模板提取）
  → 产出：style_template.json, analysis_report.md

Phase 3-4: 文案 + 场景拆分
  主会话读 phase3-script.md + phase4-scenes.md
  主会话自己写文案、拆场景、生成提示词（这些是决策，不spawn）
  → 产出：script.md, prompts.json

Phase 5: 素材生成（可并行）
  主会话读 phase5-common.md + 对应的phase5a/5b/5c
  
  并行spawn两个窄任务子代理：
  
  子代理B（TTS+BGM）: 
    "用TTS生成配音，文案如下：{完整文案}。
     用ffmpeg提取BGM：{具体ffmpeg命令}。
     混音：{具体ffmpeg命令，含volume参数}。
     输出到{具体路径}。完成后报告文件路径和时长。"
  
  子代理C（生图/视频）:
    "执行以下命令生成图片：
     chcp 65001; python D:\video-analysis\scripts\jimeng_batch_fetch.py --input {path}\prompts.json --output {path}\images --ratio '16:9' --summary
     完成后报告生成了多少张图、列出文件路径。
     每5张图用message推送2-3张预览到{频道}。"
  
  → 主会话等两个都完成，检查产出（图片数量≥25、音频时长合理）

Phase 6: 合成 + 质量评估 + 交付
  主会话读 phase6-compose.md
  spawn子代理D:
    "用以下ffmpeg命令合成视频：{完整的ffmpeg命令序列}
     1. 逐张生成片段：{具体命令}
     2. concat拼接：{具体命令}
     3. 合并音视频：{具体命令}
     4. FunASR字幕对齐：{具体命令}
     5. 烧录字幕：{具体ffmpeg命令}
     6. 截3帧检查（开头/中间/结尾），用message发送截图到{频道}
     7. 上传腾讯云：{具体上传命令}
     完成后报告：本地路径、在线链接、视频时长、分辨率、文件大小。"
  
  → 主会话验收：检查链接可访问、截图看字幕/风格、确认无问题后交付
```

### 子代理spawn规则

1. **不设超时**（不传runTimeoutSeconds）
2. **task里写具体命令**，不写"参考xxx文件"
3. **task里不包含决策逻辑**（if/else判断由主会话做）
4. **task里注明死规则**：出错立即用message报告，不尝试替代方案
5. **task里注明消息推送方式**：`message({ action: "send", channel: "discord", target: "channel:{频道ID}", message: "进度" })`
6. **所有输出用中文**

### 主会话检查点（每个phase完成后必检）

- [ ] 产出文件存在？内容合理？
- [ ] 子代理有没有偏离指令自由发挥？
- [ ] 质量达标再进下一phase，不达标就修正后重跑

### 前置检查（主会话在Phase 1前执行）
1. 抖音体字体：`Test-Path "C:\Windows\Fonts\DouyinSansBold.ttf"`
2. config.json存在：`Test-Path "skills/douyin-clone/config.json"`
3. 即梦浏览器tab：`browser tabs (profile="openclaw", target="host")` 确认jimeng.jianying.com已打开

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

### Phase文件索引（主会话按需读取）
- **Phase 1-2（数据+分析）**：`phases/phase1-data.md` + `phases/phase2-analysis.md`
- **Phase 3-4（文案+场景）**：`phases/phase3-script.md` + `phases/phase4-scenes.md`
- **Phase 5（素材生成）**：`phases/phase5-common.md` + 对应模式文件
  - 配图口播 → `phases/phase5a-jimeng-image.md`
  - 视频模式 → `phases/phase5b-jimeng-video.md`
  - 动画模式 → `phases/phase5c-remotion.md`
- **Phase 6（合成+交付）**：`phases/phase6-compose.md`

**子代理不读phase文件！主会话读完后，把具体命令写进子代理的task里。**
