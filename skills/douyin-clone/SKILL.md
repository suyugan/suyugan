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
```

**为什么这样拆：**
- 每个子代理只干一段活，token不会爆
- 子代理2（TTS）和子代理3（生图）可以并行，节省时间
- 生图用单独子代理串行跑（即梦单账号限制，多个并行会冲突）

**主会话协调逻辑：**
1. spawn子代理1 → 等完成
2. 同时spawn子代理2和子代理3 → 等两个都完成
3. spawn子代理4 → 等完成 → 交付

### 即梦生图子代理spawn模板：
```
sessions_spawn({
  label: "{主题}-视频制作",
  runTimeoutSeconds: 3600,
  task: `复刻「{博主名}」风格，制作主题「{主题}」的抖音视频。所有输出用中文。

必须先读取技能文档：skills/douyin-clone/SKILL.md，严格按流程执行。

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

【字幕烧录】
- 方案二：原始文案去标点 + FunASR时间戳对齐（丢弃ASR文字）
- 字体/大小/位置参考对标视频，从style_template.json读取

【视频完成后】
1. 上传到腾讯云：paramiko sftp到106.55.158.137，路径 /home/ubuntu/www/videos/{主题}.mp4
2. 发送高清链接：http://bm.weiixxin.com/videos/{主题}.mp4`
})
```

---

## 阶段一：抓取数据

**本地脚本（不需要下载视频）：**
```powershell
# 1. 抓取视频列表元数据
python scripts/fetch_videos.py "博主主页链接或sec_uid" -o D:\video-analysis\{博主名}

# 2. 数据统计（纯数据，不含AI分析）
python scripts/analyze_data.py -i D:\video-analysis\{博主名}\videos.json -o D:\video-analysis\{博主名}\data_report.md
```

- `scripts/fetch_videos.py` — 批量获取所有视频元数据（标题/点赞/评论/收藏/分享/时长/标签/BGM/视频宽高），保存 videos.json
- `scripts/analyze_data.py` — 纯数据统计 + **推荐选题Top5**（基于高赞/高收藏率关键词组合），输出 data_report.md

**博主数据缓存**：videos.json只抓一次，后续同博主的新视频只做增量更新（对比已有视频ID，只抓新的）。

**说明**：分析阶段只需要元数据，不需要下载视频。仅在后续需要深度文案风格分析时，才选择性下载+转录少量代表性视频。

## 阶段1.5：账号类型自动识别

**在抓取数据之后、AI分析之前，自动判断博主的内容类型。**

**流程**：
1. 读取 `videos.json`，分析以下特征：
   - **时长分布**：口播类通常1-3分钟，混剪类3-10分钟，实拍类时长不定
   - **标签关键词**：提取高频标签，匹配类型特征词（如"vlog""实拍""剪辑""口播"等）
   - **封面风格**：用AI视觉能力抽样分析3-5张封面图（是否有真人、是否为插画/配图、是否为实景）
   - **视频宽高比**：竖屏9:16居多→口播/实拍概率高，横屏→混剪概率高

2. **自动分类为以下四种类型之一**：

| 类型 | 特征 | 后续流程 |
|------|------|---------|
| **配图口播** | 封面为插画/图片，无真人出镜，1-3分钟 | 标准流程（阶段二~七） |
| **混剪** | 多素材拼接，3-10分钟，封面为影视/纪录片截图 | 走混剪流程 |
| **真人出镜** | 封面有真人，vlog/口播类标签 | 自动转为配图口播模式（抄内容风格，不抄真人） |
| **实拍** | 封面为实景照片，生活/旅行/美食类标签 | 自动转为配图口播模式 |
| **视频模式** | 博主使用AI视频/动态画面，非静态配图 | 走阶段5.1b即梦视频生成流程 |
| **动画模式** | 博主使用火柴人/简笔画/线条动画/MG动画风格 | 走阶段5.1c Remotion动画生成流程 |

3. **真人出镜/实拍类自动转换**：
   - **不需要询问用户，直接自动转为配图口播模式**
   - 复刻的是内容风格（文案结构、选题方向、叙事节奏），不是真人形象
   - 配图风格：根据视频内容主题自动选择合适的AI插画风格（如历史题材用古风绘画、情感题材用治愈插画等）
   - 转换时告知用户一句：「该博主为真人出镜，已自动转为AI配图模式，复刻内容风格」

4. **写入 style_template.json**：
```json
{
  "content_type": "配图口播",
  "content_type_confidence": 0.85,
  "content_type_reason": "封面均为插画风格，无真人出镜，平均时长2分钟，高频标签含'心理''情感'",
  ...其他已有字段...
}
```

5. **后续阶段根据 content_type 自动走对应分支**：
   - `配图口播` → 标准阶段二~七
   - `混剪` → 混剪视频复刻流程
   - `真人出镜` → 提示用户确认后走配图口播流程
   - `实拍` → 提示用户选择配图或混剪
   - `视频模式` → 阶段5.1b即梦视频生成 + ffmpeg拼接
   - `动画模式` → 阶段5.1c Remotion动画生成流程

---

## 阶段二：AI分析出报告（含视频抽帧深度风格分析）

### 📹 视频抽帧深度风格分析（阶段二核心升级）

**不再只从封面图分析风格！改为下载目标视频，逐帧分析画面，提取深度视觉风格模板。**

**流程：**

#### 步骤1：下载目标视频
**⚠️ 缓存检查：如果 `D:\video-analysis\{博主名}\ref_video.mp4` 已存在，跳过下载！**
```powershell
# 选取博主点赞Top3的代表性视频（或快速复刻模式下的单个目标视频）
$body = '{"url":"抖音视频链接"}'
$data = Invoke-RestMethod -Uri "http://localhost:18810/api/hybrid/video_data" -Method POST -ContentType "application/json" -Body $body

# 从返回数据中提取无水印视频URL并下载
$videoUrl = $data.data.video.play_addr.url_list[0]
Invoke-WebRequest -Uri $videoUrl -OutFile "D:\video-analysis\{博主名}\ref_video.mp4"
```

#### 步骤2：ffmpeg抽帧
**⚠️ 缓存检查：如果 `D:\video-analysis\{博主名}\frames\` 目录已存在且有文件，跳过抽帧！**
```powershell
# 创建帧目录
New-Item -ItemType Directory -Force -Path "D:\video-analysis\{博主名}\frames"

# 短视频（≤3分钟）：每5秒抽一帧
ffmpeg -i ref_video.mp4 -vf "fps=1/5" "D:\video-analysis\{博主名}\frames\frame_%03d.jpg"

# 长视频（>3分钟）：每10秒抽一帧
ffmpeg -i ref_video.mp4 -vf "fps=1/10" "D:\video-analysis\{博主名}\frames\frame_%03d.jpg"
```

#### 步骤3：提取音频 + FunASR转录
**⚠️ 缓存检查：如果 `ref_transcript.txt` 已存在，跳过转录！如果 `ref_audio.wav` 已存在，跳过音频提取！**
```powershell
# 提取音频（16kHz单声道WAV，FunASR要求）
ffmpeg -i ref_video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 "D:\video-analysis\{博主名}\ref_audio.wav"

# FunASR转录（Paraformer-zh，带VAD和标点）
python -c "from funasr import AutoModel; m=AutoModel(model='paraformer-zh',vad_model='fsmn-vad',punc_model='ct-punc'); r=m.generate(input='D:\\video-analysis\\{博主名}\\ref_audio.wav'); print(r[0]['text'])"
```
- 转录结果保存到 `D:\video-analysis\{博主名}\ref_transcript.txt`

#### 步骤4：AI逐帧分析画面，提取统一视觉风格模板
用AI视觉能力（Claude/Gemini）读取所有抽帧图片，逐帧分析并提取统一的视觉风格：

**分析维度：**
| 维度 | 分析内容 |
|------|---------|
| **画风** | 写实/插画/漫画/扁平/水彩/3D等，线条粗细、轮廓处理 |
| **色调** | 主色调、配色方案、饱和度、明度倾向 |
| **构图** | 居中/三分法/对称/留白位置、主体占比 |
| **光影** | 光源方向、明暗对比度、阴影处理方式 |
| **质感** | 颗粒感/平滑/纸质/数字感、纹理特征 |
| **文字排版** | 字体风格、大小比例、位置布局、颜色搭配 |

**提取要求：**
- 逐帧分析后**取交集**，提取所有帧**共同的**视觉特征作为统一风格模板
- 忽略个别帧的特殊场景差异，提取底层一致的风格DNA
- 生成 `style_positive`（正向风格提示词）和 `style_negative`（反向提示词）

#### 步骤5：分析文案结构
从转录文本中提取文案结构模板：

| 结构元素 | 提取内容 |
|---------|---------|
| **开头hook类型** | 反问式/共鸣式/悬念式/数据冲击式/反常识式 |
| **正文节奏** | 论点-论据交替/递进深入/故事线/对比反转 |
| **结尾套路** | 金句收尾/引导互动/情感升华/悬念钩子 |
| **语气特点** | 口语化程度、人称视角、情绪基调 |
| **节奏特征** | 句子长短交替规律、停顿位置 |

#### 步骤6：保存分析结果

**转录结果存为few-shot样本**：
```powershell
# 将转录文本直接存为 copywriting_examples.json（与现有格式兼容）
# 从转录中提取开头（前3秒对应文字）、正文代表段、结尾（最后一句）
```

**所有风格信息写入 style_template.json**：
```json
{
  "content_type": "配图口播",
  "art_style": "暗色调数字绘画，日式写实剧画风格",
  "color_tone": "深墨绿黑灰为主色调，微弱暖黄点缀",
  "composition": "居中构图，人物主体占画面60%",
  "lighting": "戏剧性电影光影，强烈明暗对比",
  "texture": "粗犷钢笔线条，密集排线阴影",
  "text_layout": "无画面内文字，字幕在底部",
  "subtitle_style": {
    "font_name": "DouyinSans Bold",
    "font_size": 15,
    "primary_colour": "&H00FFFFFF",
    "outline_colour": "&H00000000",
    "border_style": 1,
    "outline": 1,
    "shadow": 0,
    "bold": 1,
    "alignment": 2,
    "margin_v": 3
  },
  "atmosphere": "黑暗、悬疑、历史感",
  "aspect_ratio": "9:16",
  "video_size": [1080, 1920],
  "style_positive": "（从逐帧分析提取的完整正向风格提示词）",
  "style_negative": "（从逐帧分析提取的反向提示词）",
  "copywriting_structure": {
    "hook_type": "反常识疑问",
    "body_rhythm": "论点-史料佐证-递进",
    "ending_pattern": "金句收尾+引导互动",
    "tone": "叙事者视角，沉稳权威，口语化",
    "avg_sentence_length": 15
  },
  "source_video": "分析来源视频链接",
  "extracted_at": "2026-02-16"
}
```

---

**需要token的部分：** 读取 data_report.md + 抽帧分析结果 + 转录文本，由AI生成完整分析报告，包括：
- 博主风格特征、人设定位
- 选题规律与爆款共性
- 文案风格与语气特点
- **画风模板**（提取视觉风格描述，存为模板供后续复用）
- 复刻建议（选题/文案模板/视觉风格/发布策略）

报告模板见 `references/report-template.md`

**画风模板缓存**：分析完后，将该博主的画风描述保存到 `D:\video-analysis\{博主名}\style_template.json`：
```json
{
  "art_style": "日式漫画、黑白线稿+平涂",
  "color_tone": "深蓝色调、冷光、低饱和",
  "atmosphere": "孤独、治愈、故事感",
  "aspect_ratio": "9:16",
  "video_size": [1080, 1920],
  "style_positive": "（从配图视觉分析提取的正向风格提示词）",
  "style_negative": "（从配图视觉分析提取的反向提示词）"
}
```
后续同博主的视频直接调用此模板，AI只需填场景描述，不用每次从零写完整prompt。

### 🎨 视觉风格模板提取（关键步骤）

**目的**：从对标博主的实际配图中提取可复用的视觉风格提示词，确保生成的所有场景图风格统一且贴近原博主。

**流程**：
1. **选取参考图**：从博主视频中截取2-3张代表性配图（选画风最典型的）
2. **视觉分析提取风格**：用AI视觉能力（Claude/Gemini）分析参考图，只提取纯视觉风格，不提取具体场景内容：
   - 色彩方案（主色调、配色规则）
   - 画风/技法（线稿、扁平、水彩等）
   - 质感/纹理
   - 光影处理方式
   - 构图风格特征
   - 整体氛围/情绪基调
3. **生成 style_positive 和 style_negative**：
   - `style_positive`：一段可直接拼接在场景描述后面的通用风格提示词
   - `style_negative`：反向提示词，排除不需要的风格元素
4. **写入 style_template.json** 缓存

**示例**（心理叨叨兽）：
```json
{
  "style_positive": "深蓝色单色调插画，蓝色monochrome配色...",
  "style_negative": "彩色，暖色调..."
}
```

**示例**（奇异史 — 已验证可用，必须用完整版！简化版效果差很多）：
```json
{
  "style_positive": "暗色调数字绘画，低饱和度但保留自然肤色和服饰色彩，深墨绿黑灰为主色调，微弱暖黄琥珀色烛光点缀，日式青年漫画写实剧画风格，粗犷钢笔线条，密集排线阴影，强烈明暗对比chiaroscuro，人物面部细节精准写实，戏剧性电影光影，黑暗背景，9:16竖版构图",
  "style_negative": "纯黑白，完全单色，灰度图，高饱和度鲜艳色彩，外国人，西方人，金发，蓝眼，卡通Q版，3D渲染，低质量，模糊，水印，文字签名，变形，简笔画"
}
```

**⚠️ 此步骤必须在生成提示词之前完成，不能跳过！没有风格模板就没有视觉一致性。**

### 📝 Few-shot文案样本提取（阶段二附属步骤）

**目的**：从博主的高赞视频中提取典型文案片段，供阶段三写文案时作为few-shot示例，让AI精准模仿博主的语气、句式和节奏。

**流程**：
1. 从 `videos.json` 中筛选点赞量Top5的视频
2. 如果这些视频已有转录文本，从中提取**3-5段最典型的文案片段**：
   - 优先选取：每个视频的**开头**（前3秒钩子）和**结尾**（金句收尾）
   - 片段长度：每段50-150字
3. 保存为 `D:\video-analysis\{博主名}\copywriting_examples.json`：
```json
{
  "blogger": "博主名",
  "extracted_at": "2026-02-16",
  "examples": [
    {
      "video_title": "视频标题",
      "likes": 50000,
      "position": "opening",
      "text": "你有没有发现，那些越是讨好别人的人，越是活得卑微？"
    },
    {
      "video_title": "视频标题",
      "likes": 50000,
      "position": "ending",
      "text": "记住，你的善良要带点锋芒，否则就是软弱。"
    }
  ]
}
```
4. **缓存复用**：如果 `copywriting_examples.json` 已存在，跳过提取，直接复用。同博主不重复提取。

**可选：深度文案分析**（需要下载+转录）
```powershell
python scripts/download_videos.py -i videos.json -o . --top 10
python scripts/transcribe.py -d . -m medium
```

## 阶段2.5：推送选题给用户选择

**分析报告完成后，必须先把推荐选题发给用户选择，不要自己决定选题！**

1. 从 data_report.md 提取「推荐选题Top5」
2. 用 `message` 工具发送给用户，格式：
```
📋 奇异史账号分析完成！推荐选题：

1️⃣ 古代一两银子值多少钱
2️⃣ 古代刽子手的真实生活
3️⃣ ...
4️⃣ ...
5️⃣ ...

回复数字选择，或者告诉我你想做的选题。
```
3. **等待用户回复后再进入阶段三**

---

## 阶段三：写文案

1. 根据用户选择的选题，或用户自定义的选题
2. **加载Few-shot文案样本**：如果 `D:\video-analysis\{博主名}\copywriting_examples.json` 存在，将其中的examples作为few-shot示例放入prompt，让AI模仿博主具体的语气、句式、节奏。Prompt结构：
   ```
   以下是该博主的典型文案风格示例：
   【示例1-开头】"你有没有发现..."
   【示例2-结尾】"记住，你的善良..."
   ...
   请模仿上述风格，围绕"{选题}"写一篇原创文案。
   ```
3. 按目标博主的文案结构写原创文案：
   - **开头**（前3秒）：痛点共鸣/反直觉疑问，抓注意力
   - **正文**：痛点 → 原因分析 → 深层解读 → 解决方案
   - **结尾**：金句收尾 + 引导互动
3. 文案长度参考博主平均时长（口播约 250字/分钟）
4. 保存到 `D:\video-analysis\output\{主题}\script.md`

## 阶段四：拆分场景 + 生成提示词

文案写完后，AI自动完成。**⚠️ 根据 content_type 走不同的拆分逻辑！**

---

### 4A. 配图模式/视频模式的场景拆分

> 适用于：配图口播、真人出镜、实拍、视频模式

1. **拆分片段**：按内容逻辑将文案拆成若干片段，每个片段对应一个画面场景。**⚠️ 数量严禁固定为10个！必须根据文案实际内容结构决定，可能是5个、8个、12个或其他任意数量。不要凑数，不要硬拆，每个片段必须有独立的画面意义。**
   - **最低25个场景**：2-3分钟的视频至少25个场景，参考视频通常每3-5秒切换画面
   - 同一段话可以拆成多个不同视角的场景（特写/中景/远景/细节）
   - 每5-8秒换一个画面，避免一张图撑太久导致观感单调
2. **生成提示词**：为每个片段生成即梦图片提示词，画面要精准匹配该片段的文案内容
3. **复用画风模板**：如果 `style_template.json` 存在，读取 `style_positive` 和 `style_negative`，每个场景提示词 = 场景描述 + style_positive。**必须拼接风格模板，不能只写场景描述！**
4. **输出 prompts.json**：

---

### 4B. 动画模式的段落拆分

> 适用于：content_type 为「动画模式」（火柴人、简笔画、线条动画、MG动画）

**⚠️ 动画模式不需要逐张生图！Remotion是连续渲染的，画面自然流动过渡，不需要切成碎片。**

1. **按文案逻辑拆成5-8个大段落**：每个段落是一个完整的叙事单元（一个观点、一个场景、一段情绪），段落内部动画连续流动，段落之间做转场。
   - 不要按句子拆，要按"意思完整的段落"拆
   - 每个段落15-30秒，内部可以有多个动作/画面变化，但它们是连续过渡的，不是硬切
   - 段落之间用转场衔接（淡入淡出/滑动/场景切换）

2. **为每个段落写动画描述**（不是图片提示词！）：描述这个段落内动画如何运动、变化、过渡
   - 重点描述：人物动作序列、场景元素变化、镜头移动、情绪节奏
   - 这是给Remotion写代码的依据，不是给AI生图的prompt

3. **输出 prompts.json**（动画模式格式）：

```json
{
  "mode": "animation",
  "sections": [
    {
      "section_num": 1,
      "text": "对应的文案段落（可包含多句话）",
      "duration_sec": 20,
      "animation_desc": "火柴人站在画面中央，双手自然下垂→缓慢抬头看天→周围渐渐出现灰色人影从四面围过来→火柴人双手抱头缓慢蹲下→人影越来越密",
      "key_actions": ["抬头", "人影出现", "抱头", "蹲下"],
      "emotion": "压抑→焦虑",
      "transition_to_next": "背景渐暗，人影消散"
    },
    {
      "section_num": 2,
      "text": "...",
      "duration_sec": 18,
      "animation_desc": "...",
      "key_actions": ["..."],
      "emotion": "...",
      "transition_to_next": "..."
    }
  ]
}
```

4. **保存到** `D:\video-analysis\output\{主题}\prompts.json`

> **然后直接跳到阶段5.1c Remotion动画生成，不经过阶段4.5和阶段5.1的即梦生图流程。**

---

### 以下为配图/视频模式的 prompts.json 格式：

```json
{
  "scenes": [
    {
      "scene_num": 1,
      "text": "对应的文案片段内容...",
      "prompt": "帮我生成图片：...\n背景：...\n风格：...\n氛围：...\n构图：...。比例 X:X。",
      "video_mode": "t2v",
      "video_mode_reason": "大场景航拍，无需精确控制"
    },
    {
      "scene_num": 2,
      "text": "对应的文案片段内容...",
      "prompt": "...",
      "video_mode": "i2v",
      "video_mode_reason": "需要精确的人物表情特写"
    }
  ]
}
```

> **video_mode 字段说明**（仅当 content_type 为「视频模式」时需要）：
> - `"t2v"`：纯文生视频，直接用prompt生成视频
> - `"i2v"`：图生视频，先生图再用图作为首帧生成视频
> - `video_mode_reason`：选择该模式的理由，便于调试和人工审核
> - 如果 content_type 不是视频模式（即配图口播），此字段可省略

**提示词格式**（必须严格按此结构）：
```
{场景主体描述，人物外貌/动作/表情/服装，背景环境}，{style_positive从style_template.json读取}
```

**拼接规则**：
- 前半段 = 场景内容描述（每个场景不同）
- 后半段 = style_positive（所有场景相同，从模板读取）
- 用中文逗号连接
- style_negative 作为反向提示词传给即梦API（如API支持）

**⚠️ 色彩层次要求（不能只写单色调！）**：
- 参考视频通常有丰富的色彩细节：自然肤色、暖光点缀、阴影渐变
- 提示词里必须加明确的色彩指令，如「保留自然肤色和服饰淡彩，暖黄色灯光点缀高光区域，线条有粗细变化，阴影有层次渐变」
- 不能只说「白色线条蓝色背景」这种粗暴描述
- 可用参考视频关键帧做img2img/风格参考（如即梦支持图生图），而不是纯文本描述风格

**⚠️ 场景数量要求（必须足够密！）**：
- 参考视频通常每3-5秒切换一个画面，2分半的视频≈30-50个场景
- **我们至少要做到25个场景以上**，不能一句话配一张图撑太久
- 同一段话可以拆成多个视角——比如「你总觉得自己不够好」可拆成：人物低头特写、镜子里倒影、周围人的目光，三个场景讲一句话
- 文案拆分更细，每5-8秒换一个画面，避免观感单调

**⚠️ 场景脚本表（批量生图前必须先写！）**：
正式生图前，先写一个场景对照表存到 `scene_table.md`：
```
| 序号 | 时间段 | 文案片段 | 画面描述 | 参考帧编号 | 视角/构图 |
|------|--------|---------|---------|-----------|----------|
| 1 | 0:00-0:03 | 你有没有发现... | 人物蜷缩在狭小空间 | frame_001 | 俯拍全身 |
| 2 | 0:03-0:06 | 你对所有人都好... | 人物微笑递出礼物 | frame_002 | 中景正面 |
| 3 | 0:06-0:08 | 最后过得最惨的是你 | 人物独自坐在角落 | frame_003 | 远景侧面 |
```
- 每个画面都要有对标参考帧（从对标视频抽帧中选最接近的）
- 同一段文案如果超过5秒，必须拆成多个不同视角的场景

**要求**：
- 每个prompt必须与该片段文案内容强关联，不能泛泛而谈
- 画面风格保持统一（同一套视觉语言）
- **图片尺寸**：从视频元数据获取实际画面宽高，避免变形
- 保存到 `D:\video-analysis\output\{主题}\prompts.json`

## 阶段4.5：提示词对比优化（关键步骤）

> **⚠️ 动画模式跳过此阶段！** 动画模式在阶段4B完成后直接进入阶段5.1c Remotion动画生成。

**生成提示词后，不要直接进入批量生图！先用2-3个代表性场景做风格样片测试。**

### 风格样片流程（必须步骤！）

1. **选取2-3个代表性场景**：从prompts.json中选画面差异最大的场景（如一个人物特写、一个全景、一个情绪场景）

2. **首轮生图**：用初始提示词通过即梦生成测试图

3. **对比分析**：用AI视觉能力同时读取**原视频帧**和**生成图**，逐维度对比：
   - 画风匹配度（线条、技法是否一致）
   - **色彩层次**（是否有肤色、暖光、阴影渐变，还是只有单调的线条+底色）
   - 色调匹配度（主色调、饱和度、明暗是否接近）
   - 构图匹配度（主体位置、留白比例）
   - 氛围匹配度（情绪、光影感觉）
   - 质感匹配度（纹理、颗粒感）

4. **针对性优化提示词**：根据对比结果调整提示词
   - 色彩太单调 → 加「保留自然肤色和服饰淡彩，暖黄色灯光点缀高光区域」
   - 色调偏暖 → 加"冷色调，低饱和"等修正词
   - 线条太光滑 → 加"粗犷笔触，密集排线，铜版画质感"
   - 氛围不够暗 → 加"黑暗背景，强烈明暗对比，chiaroscuro"
   - 构图不对 → 调整主体描述和比例说明

5. **二轮生图验证**：用优化后的提示词重新生成，再次对比
   - 如果满意 → 更新 `style_positive`，进入批量生图
   - 如果仍有差距 → 最多再迭代1轮（共3轮封顶）

6. **更新模板**：将优化后的最终版提示词回写到 `style_template.json` 的 `style_positive` 和 `style_negative`

### 输出
- 优化过程记录到 `D:\video-analysis\{博主名}\prompt_optimization_log.json`：
```json
{
  "iterations": [
    {
      "round": 1,
      "test_scenes": [1, 5],
      "original_style_positive": "...",
      "comparison_notes": "色调偏暖，线条过于光滑，缺少排线阴影",
      "adjustments": ["加入'密集排线阴影'", "加入'低饱和冷色调'"],
      "updated_style_positive": "..."
    },
    {
      "round": 2,
      "comparison_notes": "色调和线条匹配度大幅提升，构图OK",
      "result": "pass"
    }
  ],
  "final_style_positive": "...",
  "final_style_negative": "..."
}
```

**⚠️ 此步骤最多消耗4-6张即梦生图额度，但能显著提升后续全部场景的画风一致性，值得投入！**

---

## 阶段五：生成素材（TTS和生图并行）

⚡ **TTS配音和即梦生图可以同时执行，不需要串行等待。**

### 5.1 AI配图（即梦无感方案 — 逆向签名算法）

**⚠️ 使用即梦网页版内部API（Fetch方式），不走官方API！无需API key，通过browser evaluate在已登录的即梦网页中直接调用。**

**⚠️⚠️⚠️ 子代理必读：必须使用下面的标准脚本，严禁自己写JS/API调用代码！脚本已内置sign签名算法（MD5逆向），自己写会因为缺少签名报1002错误！**

**前置条件：** openclaw浏览器中即梦网页版（jimeng.jianying.com）已登录。

**标准脚本路径：**
- 单张生成JS：`D:\video-analysis\scripts\jimeng_fetch_gen.py`
- 批量生成：`D:\video-analysis\scripts\jimeng_batch_fetch.py`

**⚠️ 优先使用并发模式生图！串行太慢，容易撞子代理时间墙。**

**方案A：并发模式（推荐，10张图3-4分钟）**

核心思路：一次性提交所有generate请求（间隔2秒），收集submit_id，然后批量轮询，所有图的生成时间重叠。

```
步骤1：获取即梦tab
  browser({ action: "tabs", profile: "openclaw", target: "host" })
  → 找到 url 包含 jimeng.jianying.com 的tab，记下 targetId

步骤2：初始化MD5签名函数
  读取 jimeng_fetch_gen.py 中的 SIGN_JS_HELPER
  browser evaluate 执行，确保 window.__jimeng_md5 可用

步骤3：读取 prompts.json，获取所有场景的prompt

步骤4：构建并发提交JS
  在browser evaluate中执行一个大JS，功能：
  a) 定义 __jimengGen(prompt, submitId) 函数（调用generate API）
  b) 定义 __jimengPoll(submitIds) 函数（批量查询多个submit_id）
  c) 快速连续提交所有场景的generate请求（每个间隔2秒用setTimeout错开）
  d) 收集所有submit_id到 window.__batchSubmitIds
  e) 提交完毕后自动开始轮询，每5秒批量查一次所有id状态
  f) 结果存在 window.__batchResults = { sceneNum: {status, url}, ... }
  g) 全部完成后 window.__batchDone = true

步骤5：每10秒用browser evaluate检查 window.__batchDone 和 window.__batchResults

步骤6：全部done后，从results中获取图片URL，逐个下载保存为 scene_XX.webp
  Invoke-WebRequest -Uri $url -OutFile "images/scene_XX.webp"
```

**并发数控制**：3-5个同时提交，间隔2秒，避免触发即梦限流。
**超时**：单张图轮询超时120秒，整批超时300秒。
**断点续传**：跳过images/目录中已存在的scene_XX.webp文件。

**并发辅助脚本**：`D:\video-analysis\scripts\jimeng_batch_concurrent.py`
```powershell
# 生成执行计划（含所有场景的generate JS和submit_id）
python D:\video-analysis\scripts\jimeng_batch_concurrent.py --prompts-file prompts.json --scenes 1-22 --ratio 16:9 --output-dir images --action plan

# 生成批量轮询JS（一次查多个submit_id）
python D:\video-analysis\scripts\jimeng_batch_concurrent.py --action poll-js --submit-ids "id1,id2,id3"
```

**方案B：串行模式（备用，当并发被限流时降级使用）**

```
步骤1-2：同上

步骤3：逐个场景生图（循环）
  对每个场景：

  3a. 生成提交JS代码：
      python D:\video-analysis\scripts\jimeng_fetch_gen.py --action generate --prompt "场景prompt文本" --ratio "16:9" --json
      → 输出JSON：{"js": "...", "submit_id": "xxx-xxx"}

  3b. 在即梦页面执行提交JS：
      browser({ action: "act", profile: "openclaw", target: "host", targeid: "<即梦targetId>",
        request: { kind: "evaluate", fn: "<上一步拿到的js>" } })

  3c. 等待3秒（提交间隔）

  3d. 生成轮询JS代码：
      python D:\video-analysis\scripts\jimeng_fetch_gen.py --action poll --submit-id "<submit_id>" --json

  3e. 间隔5秒轮询，直到返回 status=done，超时120秒

  3f. 下载第一张图片：
      Invoke-WebRequest -Uri "<urls[0]>" -OutFile "images/scene_XX.webp"

  3g. 每5个场景发一次进度更新
```

**⚠️ 如果Python脚本输出的JS中中文是乱码（Windows编码问题），用以下方法解决：**
```powershell
# 方法1：设置UTF-8编码后再执行
chcp 65001
python D:\video-analysis\scripts\jimeng_fetch_gen.py ...

# 方法2：用Python直接读取输出
python -c "import subprocess,json; r=subprocess.run(['python','D:\\video-analysis\\scripts\\jimeng_fetch_gen.py','--action','generate','--prompt','xxx','--ratio','16:9','--json'],capture_output=True,text=True,encoding='utf-8'); print(r.stdout)"
```

**比例参数映射：**

| 比例 | image_ratio | 宽x高 |
|------|------------|--------|
| 1:1  | 1 | 2048x2048 |
| 3:4  | 3 | 1536x2048 |
| 4:3  | 4 | 2048x1536 |
| 9:16 | 5 | 1440x2560 |
| 16:9 | 6 | 2560x1440 |

**⚠️ 抖音视频一律生成横屏图 16:9（image_ratio=6, 2560x1440）**

**注意事项：**
- 脚本已内置sign签名算法（MD5逆向），不需要自己算sign
- 频率控制：每次生图间隔2-3秒
- 轮询间隔：5秒一次，超时120秒
- 模型：`high_aes_general_v41`（高质量通用）
- 每次生成4张图，取第一张下载
- 详细文档见 `skills/jimeng-fetch/SKILL.md`

**📸 图片预览（必须步骤，不影响继续生图）：**
生图过程中，每完成5张图就随机挑2-3张发送给用户预览，让用户看到生图效果。发送方式：
```
message({ action: "send", message: "🎨 即梦生图进度 X/Y，预览几张：", media: "D:\\video-analysis\\output\\{主题}\\images\\scene_XX.webp" })
```
- 预览不阻塞生图流程，发完继续下一张
- 如果用户反馈风格不对，暂停生图等指示

### 5.1b AI视频生成（即梦视频模式 — 当 content_type 为「视频模式」或混剪时可选）

**当 style_template.json 中 content_type 为「视频模式」时，改用即梦视频生成替代静态图片。**

#### 双模式自动选择规则

每个场景根据内容自动选择生成方式：

**模式A：纯文生视频（text-to-video, t2v）**
适用场景：
- 大场景/风景/航拍（如"古代皇宫全景"、"战场远景"）
- 抽象概念/特效（如"时间流逝"、"数据可视化"）
- 动物/自然场景（如"猫在草地奔跑"）
流程：直接用文字提示词生成5秒视频

**模式B：图生视频（image-to-video, i2v）**
适用场景：
- 需要精确人物形象/表情的场景
- 需要特定构图/画面元素精确控制的场景
- 需要与前后场景保持人物一致性的场景
流程：先用即梦生图（已有流程5.1）→ 用生成的图作为首帧 → 即梦图生视频

**自动选择逻辑：**
AI在拆分场景时（阶段四），为每个场景标注 `video_mode: "t2v"` 或 `"i2v"`，写入prompts.json（见阶段四的prompts.json格式）。

**图生视频（i2v）的API调用：**
基于现有即梦视频生成接口，图生视频的 `draft_content` 中需要额外传入首帧图片URL。在 `video_gen_inputs` 中增加image相关参数：
```json
{
  "video_gen_inputs": [
    {
      "prompt": "场景描述",
      "first_frame_image": "<首帧图片URL>",
      "generation_mode": "i2v"
    }
  ]
}
```
> ⚠️ 具体字段名（如 `first_frame_image`、`generation_mode`）待抓包确认，以上为占位说明。确认后更新 `jimeng_video_gen.py` 脚本支持 `--image` 参数。

**i2v模式执行流程：**
```
1. 读取场景的 video_mode 字段
2. 如果 video_mode == "i2v"：
   a) 先用即梦生图流程（5.1）生成该场景的静态图
   b) 用生成的图片URL作为首帧，调用即梦图生视频接口
   c) 轮询等待视频生成完成
3. 如果 video_mode == "t2v"：
   a) 直接用文字提示词调用即梦视频生成接口（现有流程）
```

**标准脚本路径：** `D:\video-analysis\scripts\jimeng_video_gen.py`

**与图片生成的区别：**
- 使用即梦视频生成API（同一个 aigc_draft/generate 端口，但 draft_content 结构不同）
- 轮询接口不同：视频用 `get_history_queue_info`（图片用 `get_history_by_ids`）
- 轮询用 `history_id`（数字ID，从提交响应获取），不是 `submit_id`
- 每个场景生成5秒视频片段，最后用 ffmpeg concat 拼接

**逐步调用流程：**
```
步骤1：获取即梦tab
  browser({ action: "tabs", profile: "openclaw", target: "host" })
  → 找到 url 包含 jimeng.jianying.com 的tab，记下 targetId

步骤2：加载MD5签名（如未加载）
  cmd /c "python D:\video-analysis\scripts\jimeng_video_gen.py --action md5 --json"
  → 取出js，browser evaluate执行

步骤3：逐个场景生成视频（循环）
  对每个场景：

  3a. 生成提交JS代码：
      cmd /c "chcp 65001 >nul & python D:\video-analysis\scripts\jimeng_video_gen.py --action generate --prompt "场景描述" --ratio "16:9" --duration 5 --resolution 720p --json"
      → 输出JSON：{"js": "...", "submit_id": "xxx"}

  3b. 在即梦页面执行提交JS：
      browser evaluate → 返回 {ret, errmsg, submit_id, history_id, data}
      ⚠️ 必须记录 history_id（数字），后续轮询用！
      如果 history_id 为空，从 data 中深层查找

  3c. 等待5秒

  3d. 生成轮询JS代码（推荐用 poll-full 一体化轮询）：
      python jimeng_video_gen.py --action poll-full --history-id "<history_id>" --json
      → 输出JS：自动查队列状态，完成后用get_history_by_ids获取视频URL

  3e. 间隔30秒轮询（视频生成较慢！），直到返回 status=done：
      → 返回 {status:"done", videos:[{video_url, cover_url, duration, width, height}]}
      → 超时300秒放弃该场景

  3f. 下载视频：
      curl -o videos/scene_XX.mp4 "<video_url>"

  3g. 每3个场景发一次进度更新
```

**所有片段生成后，ffmpeg拼接：**
```bash
# 1. 创建 concat 清单
echo "file 'videos/scene_01.mp4'" > concat_list.txt
echo "file 'videos/scene_02.mp4'" >> concat_list.txt
# ...

# 2. 拼接所有片段
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy video_only.mp4

# 3. 后续流程不变：混合TTS+BGM音频，烧录字幕
```

**注意事项：**
- 视频生成比图片慢很多（可能1-3分钟/个），轮询间隔建议30秒
- 每次生成1个视频（不像图片一次生成4张）
- 模型默认 fast（vgfm_3.0_fast），可选 standard（vgfm_3.0，更慢但质量更高）
- 视频分辨率默认720p，可选1080p

**视频模式子代理spawn模板：**
```
sessions_spawn({
  label: "{主题}-视频制作(视频模式)",
  task: `复刻「{博主名}」风格，制作主题「{主题}」的抖音视频（视频模式）。所有输出用中文。

必须先读取技能文档：skills/douyin-clone/SKILL.md，严格按流程执行。
工作目录：D:\\video-analysis\\output\\{主题}\\

该博主为视频模式，使用即梦视频生成（非图片）：
1. 读取 prompts.json，检查每个场景的 video_mode 字段
2. 根据 video_mode 选择生成方式：
   - video_mode == "t2v"：直接用文字提示词生成视频（现有流程）
   - video_mode == "i2v"：先用即梦生图（5.1流程）生成静态图 → 再用图作为首帧调用图生视频接口
3. 使用脚本：python D:\\video-analysis\\scripts\\jimeng_video_gen.py
4. 提交→记录history_id→轮询（30秒间隔）→下载视频
5. ffmpeg concat拼接所有片段
6. TTS配音 + BGM混音（与视频生成并行）
7. 字幕烧录
8. 上传腾讯云 → 交付高清链接`
})
```

### 5.1c Remotion动画生成（当 content_type 为「动画模式」时）

**当对标博主使用火柴人、简笔画、线条动画、MG动画等风格时，用Remotion以代码方式生成动画视频片段。**

**适用场景**：
- 火柴人动画（SVG骨骼+关节角度控制）
- 简笔画逐笔绘制效果
- 线条动画/白板动画
- 数据可视化动效
- 文字逐字/逐行出现动效
- Motion Graphics（MG动画）

**流程**：

#### 步骤1：分析对标视频动画风格
从对标视频抽帧中提取动画特征：
- 线条粗细、颜色、背景色
- 人物造型（火柴人/简笔画/卡通）
- 运动方式（走路/跑步/手势/表情变化）
- 转场方式（淡入淡出/滑动/擦除）
- 文字样式和出现方式

将动画风格参数写入 `style_template.json`：
```json
{
  "content_type": "动画模式",
  "animation_style": {
    "character_type": "火柴人",
    "line_color": "#FFFFFF",
    "line_width": 3,
    "bg_color": "#1a1a2e",
    "accent_color": "#e94560",
    "motion_style": "简洁流畅",
    "transition": "淡入淡出",
    "text_animation": "逐字出现"
  }
}
```

#### 步骤2：读取段落动画描述
从阶段4B生成的 `prompts.json` 读取各段落的 `animation_desc`、`key_actions`、`duration_sec`、`transition_to_next` 等字段，作为编写Remotion组件的依据。

**prompts.json已在阶段4B生成，这里直接读取使用，不需要重新拆分。**

#### 步骤3：Remotion项目生成
技能文档参考：`skills/remotion-video/SKILL.md`

```
1. 初始化Remotion项目（如不存在）：
   D:\video-analysis\output\{主题}\remotion\

2. 为每个场景创建React组件：
   src/scenes/Scene01.tsx ~ SceneXX.tsx
   
   每个组件内：
   - SVG绘制人物/场景元素
   - useCurrentFrame() + interpolate() 控制动画
   - 关键帧动画：位置、旋转、缩放、透明度
   
3. 主组件 Composition 按时间线串联所有场景

4. 渲染输出：
   npx remotion render src/index.ts Main --output video_only.mp4
```

**火柴人SVG模板**：
```tsx
// 基础火柴人组件
const StickMan = ({ x, y, headTilt, armAngle, legAngle, emotion }) => (
  <g transform={`translate(${x}, ${y})`}>
    {/* 头 */}
    <circle cx={0} cy={-60} r={15} fill="none" stroke="white" strokeWidth={3} />
    {/* 表情 */}
    {emotion === 'sad' && <>
      <line x1={-5} y1={-65} x2={-3} y2={-63} stroke="white" strokeWidth={2} />
      <line x1={5} y1={-65} x2={3} y2={-63} stroke="white" strokeWidth={2} />
      <path d="M -5,-55 Q 0,-58 5,-55" fill="none" stroke="white" strokeWidth={2} />
    </>}
    {/* 身体 */}
    <line x1={0} y1={-45} x2={0} y2={0} stroke="white" strokeWidth={3} />
    {/* 手臂 */}
    <line x1={0} y1={-35} x2={-25} y2={-35 + armAngle} stroke="white" strokeWidth={3} />
    <line x1={0} y1={-35} x2={25} y2={-35 + armAngle} stroke="white" strokeWidth={3} />
    {/* 腿 */}
    <line x1={0} y1={0} x2={-20} y2={30 + legAngle} stroke="white" strokeWidth={3} />
    <line x1={0} y1={0} x2={20} y2={30 + legAngle} stroke="white" strokeWidth={3} />
  </g>
);
```

**动画插值示例**：
```tsx
const frame = useCurrentFrame();
const fps = useVideoConfig().fps;

// 火柴人缓慢下沉
const y = interpolate(frame, [0, fps * 3], [200, 280], { extrapolateRight: 'clamp' });
// 手臂下垂
const armAngle = interpolate(frame, [0, fps * 2], [0, 20], { extrapolateRight: 'clamp' });
// 背景渐暗
const bgOpacity = interpolate(frame, [0, fps * 3], [0.3, 0.8], { extrapolateRight: 'clamp' });
```

#### 步骤4：合成完整视频
```
1. Remotion渲染动画视频（无音频）→ video_only.mp4
2. 混合TTS配音 + BGM → mixed_audio.m4a（同标准流程）
3. 合并视频+音频：
   ffmpeg -y -i video_only.mp4 -i mixed_audio.m4a -c:v copy -c:a aac -movflags +faststart raw_video.mp4
4. FunASR时间戳 + 原始文案 → subs.srt（同标准流程）
5. 烧录字幕 → final.mp4
6. 上传腾讯云 → 交付
```

**与配图模式的区别**：
| 环节 | 配图模式 | 动画模式 |
|------|---------|---------|
| 素材生成 | 即梦AI生图 | Remotion代码渲染 |
| 画面切换 | 静态图+Ken Burns | 连续动画，自然过渡 |
| 风格控制 | 提示词+style_positive | SVG/CSS代码精确控制 |
| 适合内容 | 写实插画、艺术风格 | 火柴人、简笔画、MG动画 |
| 其他环节 | 完全相同（TTS、BGM、字幕、上传） | 完全相同 |

**子代理spawn模板**：
```
sessions_spawn({
  label: "{主题}-视频制作(动画模式)",
  task: `复刻「{博主名}」风格，制作主题「{主题}」的抖音视频（动画模式）。所有输出用中文。

必须先读取技能文档：
1. skills/douyin-clone/SKILL.md — 完整复刻流程
2. skills/remotion-video/SKILL.md — Remotion渲染指南

工作目录：D:\\video-analysis\\output\\{主题}\\
Remotion项目：D:\\video-analysis\\output\\{主题}\\remotion\\

该博主为动画模式（火柴人/简笔画/线条动画），使用Remotion生成动画视频：
1. 读取 style_template.json 的 animation_style 字段
2. 读取 prompts.json 的每个场景的 animation_desc
3. 为每个场景创建React+SVG组件，用useCurrentFrame+interpolate做动画
4. Remotion渲染输出视频
5. TTS配音 + BGM混音
6. FunASR字幕同步
7. 烧录字幕
8. 上传腾讯云 → 交付高清链接`
})
```

#### 5.1.1 生成质量校验

**每张生成的图片必须经过AI视觉校验，确保质量达标后再进入合成阶段。**

**校验流程**：
1. 对每张生成的图片，用AI视觉能力（Claude/Gemini）快速检查以下三项：
   - **a) 画风一致性**：是否符合 `style_template.json` 的风格（色调、画风、氛围是否匹配）
   - **b) 内容匹配度**：画面内容是否与 `prompts.json` 中对应片段的文案内容匹配
   - **c) 缺陷检测**：是否有明显缺陷（人物变形、文字乱码、多余肢体、面部崩坏等）

2. **评分标准**：每项 Pass/Fail，三项全Pass才算合格

3. **不合格处理**：
   - 分析失败原因，自动修改prompt（如加入负向提示词、调整描述）
   - 用修改后的prompt重新生成
   - **最多重试2次**，仍不合格则保留最佳结果并标记警告

4. **校验结果记录到 `quality_log.json`**：
```json
{
  "scene_1": {
    "attempts": [
      {
        "attempt": 1,
        "style_match": true,
        "content_match": true,
        "defect_free": false,
        "defect_detail": "人物右手多一根手指",
        "result": "retry"
      },
      {
        "attempt": 2,
        "style_match": true,
        "content_match": true,
        "defect_free": true,
        "result": "pass"
      }
    ],
    "final_status": "pass",
    "final_image": "images/scene_1.png"
  }
}
```

5. **保存路径**：`D:\video-analysis\output\{主题}\quality_log.json`

### 5.2 TTS配音（与5.1并行）

**⚠️ 配音必须复刻对标博主的声音特征！不再使用固定声音！**

#### 5.2.1 声音特征分析（阶段二完成，写入style_template.json）

从对标视频的音频中分析声音特征：
```python
# 1. demucs分离出纯人声
# vocals.wav 已在5.3 BGM提取时生成

# 2. 分析声音特征
import subprocess, json

# 用ffprobe分析音频参数
result = subprocess.run([
    'ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', 'vocals.wav'
], capture_output=True, text=True)
audio_info = json.loads(result.stdout)

# 3. AI听音分析（用Claude/Gemini分析vocals.wav的前30秒）
# 分析维度：性别、年龄感、语速、音调高低、情绪基调、口音特点
```

将声音特征写入 `style_template.json`：
```json
{
  "voice_style": {
    "gender": "male",
    "age_feel": "25-35岁青年",
    "speed_wpm": 280,
    "tone": "中低音，沉稳",
    "emotion": "理性分析，偶尔愤慨",
    "accent": "标准普通话",
    "pause_style": "短句间顿挫明显",
    "volume_ratio": {
      "voice_db": -12,
      "bgm_db": -18,
      "description": "人声明显高于BGM，约6dB差距"
    }
  }
}
```

#### 5.2.2 音色克隆（GPT-SoVITS，推荐方案）

**用对标博主的人声样本克隆音色，让TTS输出接近博主原声。**

**工具选择**：
| 工具 | 克隆质量 | 所需样本 | 部署 | 推荐 |
|------|---------|---------|------|------|
| **GPT-SoVITS** | ⭐⭐⭐⭐⭐ | 5-30秒 | 本地GPU | 🏆 首选 |
| **fish-speech** | ⭐⭐⭐⭐ | 10秒 | 本地GPU | 🥈 备选 |
| **edge-tts匹配** | ⭐⭐ | 不需要 | 云端免费 | 降级方案 |

**GPT-SoVITS克隆流程**：
```python
# 前置：pip install GPT-SoVITS（或docker部署）
# 项目地址：https://github.com/RVC-Boss/GPT-SoVITS

# 步骤1：准备参考音频（从demucs分离的vocals.wav截取10-30秒清晰片段）
# 选择语速适中、无BGM残留、无杂音的片段
ffmpeg -y -ss 5 -t 20 -i vocals.wav -acodec pcm_s16le -ar 32000 -ac 1 ref_voice.wav

# 步骤2：零样本推理（zero-shot，无需训练）
# GPT-SoVITS支持few-shot推理，只需参考音频+参考文本
from GPT_SoVITS.inference import TTSInference

tts = TTSInference(
    gpt_model="pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt",
    sovits_model="pretrained_models/gsv-v2final-pretrained/s2G2333k.pth"
)

# 参考音频 + 参考文本（对标博主说的那段话）
tts.synthesize(
    text="要合成的完整文案文本",
    ref_audio="ref_voice.wav",
    ref_text="参考音频对应的文字内容",  # 从转录结果获取
    output="narration_cloned.wav",
    speed=1.0  # 语速倍率，根据voice_style.speed_wpm调整
)
```

**缓存**：克隆用的参考音频保存到 `D:\video-analysis\{博主名}\ref_voice.wav`，同博主复用。

#### 5.2.3 语速匹配

```python
# 从对标视频计算语速
ref_transcript = open("ref_transcript.txt").read()
ref_duration = 150  # 秒，从ffprobe获取
ref_char_count = len(ref_transcript.replace(" ", "").replace("\n", ""))
ref_wpm = ref_char_count / (ref_duration / 60)  # 字/分钟

# 我们的文案
our_char_count = len(script_text)
target_duration = our_char_count / ref_wpm * 60  # 目标秒数

# GPT-SoVITS: 调整speed参数
speed_ratio = target_duration / actual_tts_duration

# edge-tts降级方案: 调整rate参数
rate = f"+{int((ref_wpm/250 - 1) * 100)}%" if ref_wpm > 250 else f"{int((ref_wpm/250 - 1) * 100)}%"
```

#### 5.2.4 停顿节奏复刻

```python
# 从FunASR时间戳分析对标视频的停顿模式
timestamps = result[0]["timestamp"]
pauses = []
for i in range(1, len(timestamps)):
    gap = timestamps[i][0] - timestamps[i-1][1]
    if gap > 300:  # 超过300ms算停顿
        pauses.append({"position": i, "duration_ms": gap})

# 将停顿模式应用到我们的文案中
# 在对应位置插入SSML停顿标签（edge-tts支持）
# 或在GPT-SoVITS中通过标点和空格控制停顿
```

#### 5.2.5 音量匹配

```python
# 分析对标视频的人声/BGM音量比
import subprocess

# 测量人声响度（LUFS）
result = subprocess.run([
    'ffmpeg', '-i', 'vocals.wav', '-af', 'loudnorm=print_format=json', '-f', 'null', '-'
], capture_output=True, text=True)
# 从stderr解析input_i（integrated loudness）

# 测量BGM响度
result = subprocess.run([
    'ffmpeg', '-i', 'bgm_clean.wav', '-af', 'loudnorm=print_format=json', '-f', 'null', '-'
], capture_output=True, text=True)

# 计算差值，合成时保持相同的人声/BGM响度差
# 写入style_template.json的voice_style.volume_ratio
```

**混音时应用**：
```bash
# 用loudnorm标准化到对标音量
ffmpeg -y -i narration.wav -i bgm_clean.wav \
  -filter_complex "[0:a]loudnorm=I={voice_lufs}[voice];[1:a]loudnorm=I={bgm_lufs}[music];[voice][music]amix=inputs=2:duration=first[a]" \
  -map "[a]" -c:a aac -b:a 192k mixed_audio.m4a
```

#### 5.2.6 降级方案（无GPU或克隆失败时）

如果GPT-SoVITS不可用，用edge-tts匹配最接近的声音：
```python
# 根据voice_style选择最接近的edge-tts声音
VOICE_MAP = {
    ("male", "young", "calm"): "zh-CN-YunxiNeural",
    ("male", "young", "energetic"): "zh-CN-YunjianNeural", 
    ("male", "mature", "authoritative"): "zh-CN-YunyeNeural",
    ("female", "young", "warm"): "zh-CN-XiaoxiaoNeural",
    ("female", "young", "cheerful"): "zh-CN-XiaohanNeural",
    ("female", "mature", "professional"): "zh-CN-XiaoqiuNeural",
}
```

**优先级**：GPT-SoVITS克隆 > fish-speech克隆 > edge-tts匹配

**声音复刻缓存路径**：
```
D:\video-analysis\{博主名}\
├── vocals.wav          # demucs分离的纯人声
├── ref_voice.wav       # 克隆用参考音频片段（10-30秒）
├── ref_voice_text.txt  # 参考音频对应的文字
└── voice_style.json    # 声音特征分析结果（也写入style_template.json）
```

### 5.3 BGM（从对标博主视频提取）

**不再使用默认BGM（dance_for_me_wallis.mp3已废弃）。**

BGM必须从对标博主的热门视频中提取，流程如下：

1. **获取博主热门视频的music URL**：通过视频分析API获取博主高赞视频的 `music.play_url`
2. **下载原始音频**：保存到 `D:\video-analysis\{博主名}\bgm_raw.mp3`
3. **demucs分离人声**：去除人声，得到纯BGM（流程与混剪流程中"BGM提取与缓存"章节完全一致）
4. **缓存复用**：纯BGM保存到 `D:\video-analysis\{博主名}\bgm_clean.wav`，同博主后续视频直接复用，不重复分离

**缓存路径：**
```
D:\video-analysis\{博主名}\
├── bgm_raw.mp3        # 原始音频（从抖音API下载）
├── bgm_raw.wav        # wav 格式
├── bgm_clean.wav      # demucs 分离后的纯BGM ← 二次复用这个
└── vocals.wav         # 分离出的人声（备用）
```

**demucs分离代码**参考本文档"混剪视频复刻流程"中的"3. BGM提取与缓存"章节，完全相同的逻辑。

**⚠️ 注意事项：**
- Windows 上用 soundfile 加载音频，不要用 torchaudio.load()
- 如果 `bgm_clean.wav` 已存在，直接复用，跳过分离步骤
- 如用户指定其他BGM则按要求替换

## 阶段六：合成视频

**本地脚本：**
```powershell
python scripts/compose_video.py -i images -n narration.mp3 -b bgm.mp3 -o final.mp4
```

**⚠️ 视频质量规则：永远输出最高清晰度，crf 18，保持原始分辨率，不做压缩降质。不需要生成压缩版。**

**⚠️ FFmpeg输出必须加 `-movflags +faststart`，让视频支持浏览器流式播放，不加就是低级错误！**

**⚠️ 音频必须一整条录制，不要分段！** TTS把全部文案一次性生成一条完整音频，然后按时间点切换图片。分段拼接会导致衔接处断裂、最后一个字听不清。

**⚠️ 图片数量规则：每段文案至少配2-3张不同角度的图，总数不少于25张。11张太少！**

**⚠️ 人物一致性：如果博主讲中国古代史，所有prompt必须写明"中国古代人物"，negative必须加"外国人，西方人"。风格模板(style_positive)必须拼接到每个prompt。**

### 视频合成3步法（避免OOM，已验证）

单pass合成在2-3分钟视频时FFmpeg会OOM，必须分3步：

**步骤1：混合音频**（BGM+旁白）
```bash
ffmpeg -y -i narration.mp3 -i bgm.mp3 -filter_complex "[0:a]volume=2.0[voice];[1:a]volume=3.0,afade=t=in:st=0:d=2[music];[voice][music]amix=inputs=2:duration=first[a]" -map "[a]" -c:a aac -b:a 192k mixed_audio.m4a
```

**步骤2：合成图片+音频→原始视频**
```python
# Python脚本：按文案片段时长分配图片，每张图加Ken Burns动效
# 用ffmpeg concat协议或逐段生成再concat
# 输出 raw_video.mp4（无字幕）
```

**⚠️ 配图与文案一一对应规则（严格执行）：**
- `prompts.json` 中每个scene的 `text` 对应一段文案，该段文案被TTS读出的时间段内，必须显示**对应编号的场景图**
- **不能随机分配，不能顺序不匹配**——scene_1的图对应scene_1的文案音频时段，scene_2的图对应scene_2的文案音频时段，以此类推
- **展示时长按文案片段的字数比例分配**：每张图的展示秒数 = (该片段字数 / 总文案字数) × 总音频时长
- 示例：总文案500字，总音频120秒，scene_1文案100字 → scene_1图展示 100/500×120 = 24秒

**步骤3：烧录字幕**
```bash
# 先从raw_video提取音频→FunASR生成SRT→再烧录
ffmpeg -y -i raw_video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 extracted_audio.wav
# 用FunASR Paraformer生成SRT（见上方代码）
ffmpeg -y -i raw_video.mp4 -vf "subtitles='subs.srt':force_style='...'" -c:v libx264 -preset slow -crf 18 -c:a copy -movflags +faststart final.mp4
```

### 字幕烧录（必须步骤）

视频必须烧录白色字幕，样式参考奇异史：单行、无标点、抖音体。

**⚠️ 字幕生成核心原则：音频驱动 + 原始文案（方案二）**

不依赖ASR识别文字内容（避免错别字），只借ASR的时间对齐能力：
```
原始文案(已有) → TTS生成音频 → Whisper/FunASR只取时间戳 → 用原始文案 + 时间戳生成SRT
```

**字幕生成流程：**
1. 文案按句拆分为列表：`["句子1", "句子2", ...]`（拆分时去掉所有标点）
2. TTS生成完整音频
3. 从合成好的视频（含BGM+配音）中提取音频
4. 用**FunASR Paraformer-zh**对提取的音频生成带时间戳的结果
5. **丢弃ASR识别的文字，只保留每句的起止时间戳**
6. 将原始文案句子 + ASR时间戳一一配对，生成SRT
7. 用FFmpeg subtitles滤镜烧录到视频上

**为什么这样做：**
- TTS语速不固定，不能靠字数估算时间
- ASR（无论Whisper还是FunASR）中文识别都有错别字
- 原始文案本身就是正确的，只需要ASR提供时间对齐
- 这样字幕和声音天然同步，且零错别字

**ASR模型选择（用于时间对齐）：**

| 模型 | 时间戳精度 | 显存 | 速度 | 推荐 |
|------|-----------|------|------|------|
| **FunASR Paraformer-zh** | ⭐⭐⭐⭐⭐ | 1-2GB | RTF 0.035 | 🏆 首选 |
| **FunASR SenseVoice-Small** | ⭐⭐⭐⭐ | ~1GB | RTF 0.031 | 🥈 备选 |

**安装：**
```bash
pip install funasr modelscope torch torchaudio
```

**字幕生成代码（方案二：原始文案+ASR逐字时间戳）：**
```python
import re
from funasr import AutoModel

# 1. 原始文案去标点，保留为完整字符串
def clean_text(script_text):
    """去掉所有标点，保留纯文字"""
    text = re.sub(r'[。，、！？；：""''……——《》（）\(\)「」【】\s\n]+', '', script_text)
    return text

# 2. ASR获取逐字时间戳
asr_model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc",
)
result = asr_model.generate(input="extracted_audio.wav")

# 3. 提取逐字时间戳（关键！用timestamp字段而不是sentence_info）
# result[0]["timestamp"] 返回 [[start_ms, end_ms], [start_ms, end_ms], ...]
# 每个元素对应一个字的起止时间
char_timestamps = result[0]["timestamp"]  # 逐字时间戳列表
asr_text = result[0]["text"]  # ASR识别的文字（仅用于对齐，不用于显示）

# 4. 原始文案去标点
original_text = clean_text(script_text)

# 5. 先按句分段，再对长句二次切分≤15字
def split_to_sentences(script_text):
    """先按句号/问号/感叹号/换行分句，再去标点"""
    sentences = re.split(r'[。！？\n]+', script_text)
    result = []
    for s in sentences:
        s = re.sub(r'[，、；：""''……——《》（）\(\)「」【】\s]', '', s).strip()
        if s:
            result.append(s)
    return result

def smart_split_sentence(text, max_len=15):
    """对单个句子按≤15字切分，保持完整句意。
    优先用AI切分（语义完整），退化用虚词切分。"""
    if len(text) <= max_len:
        return [text]
    # 方案A：用AI切分（推荐，语义最自然）
    # 在调用时传入AI prompt：
    # "把以下句子拆成每段≤15字的片段，每段必须有完整句意，直接输出片段列表，用换行分隔：{text}"
    # 方案B：退化方案，按虚词切分
    chunks = []
    while len(text) > max_len:
        cut = max_len
        for i in range(min(max_len, len(text)) - 1, max(max_len - 5, 0), -1):
            if text[i] in '的了吗呢吧是在有和但而就也都要会能把被让给':
                cut = i + 1
                break
        chunks.append(text[:cut])
        text = text[cut:]
    if text:
        chunks.append(text)
    return chunks

# 推荐：用AI批量切分所有长句
# prompt示例：
# """把以下每个句子拆成≤15字的片段，每个片段必须有完整句意。
# 输出格式：每个原句的片段用 | 分隔，句子之间用换行分隔。
# 
# 1. 古代影视剧里动不动就掏出几十两上百两银子买东西
# 2. 可你知道吗在真实的古代绝大多数的老百姓一辈子都没见过银子长什么样
# ..."""
# AI输出：
# 古代影视剧里|动不动就掏出|几十两上百两银子买东西
# 可你知道吗|在真实的古代|绝大多数的老百姓|一辈子都没见过|银子长什么样

# 先按句分段，再切分长句
sentences = split_to_sentences(script_text)
chunks = []
for sent in sentences:
    chunks.extend(smart_split_sentence(sent))

# 6. 逐字时间戳与文案切片对齐生成SRT
def to_srt_with_char_timestamps(chunks, char_timestamps):
    srt_lines = []
    char_idx = 0  # 当前消耗到第几个字的时间戳
    
    for i, chunk in enumerate(chunks):
        chunk_len = len(chunk)
        if char_idx >= len(char_timestamps):
            break
        
        # 该切片对应的时间范围：第一个字的start → 最后一个字的end
        start_ms = char_timestamps[char_idx][0]
        end_idx = min(char_idx + chunk_len - 1, len(char_timestamps) - 1)
        end_ms = char_timestamps[end_idx][1]
        
        start_t = f"{start_ms//3600000:02d}:{(start_ms%3600000)//60000:02d}:{(start_ms%60000)//1000:02d},{start_ms%1000:03d}"
        end_t = f"{end_ms//3600000:02d}:{(end_ms%3600000)//60000:02d}:{(end_ms%60000)//1000:02d},{end_ms%1000:03d}"
        
        srt_lines.append(f"{i+1}\n{start_t} --> {end_t}\n{chunk}\n")
        char_idx += chunk_len
    
    return "\n".join(srt_lines)

with open("subs.srt", "w", encoding="utf-8") as f:
    f.write(to_srt_with_char_timestamps(chunks, char_timestamps))
```

**⚠️ 关键点：**
- 用 `result[0]["timestamp"]` 获取逐字时间戳（不是 `sentence_info`！）
- 逐字时间戳精度很高（±0.1秒），切成多短的片段都能精确对齐
- 原始文案总字数 ≈ ASR识别字数，一一对应消耗时间戳
- 如果字数不完全匹配（ASR多识别/少识别了几个字），按比例微调对齐

**热词增强**（提升时间戳对齐精度）：
```python
result = asr_model.generate(
    input="extracted_audio.wav",
    hotword="三氧化二砷 砒霜 鹤顶红 见血封喉"  # 按视频内容填写
)
```

**字幕样式参数（ASS force_style）：**

**⚠️ 字体安装检查（每次合成前必须执行）：**
```powershell
# 检查抖音体是否已安装
if (!(Test-Path "C:\Windows\Fonts\DouyinSansBold.ttf")) {
    # 下载抖音体（从抖音官网Sans页面获取）
    # 方法1：browser自动化下载
    # 方法2：如果之前下载过，从备份路径复制
    # 方法3：直接用curl下载（需要有效URL）
    
    # 安装字体（复制到Fonts目录即可）
    Copy-Item "DouyinSansBold.ttf" "C:\Windows\Fonts\DouyinSansBold.ttf"
}
```
如果系统没有抖音体，子代理必须先安装再烧录字幕，**不能用微软雅黑替代**！

**⚠️ 字体打包方案（推荐，不依赖系统安装）：**
将抖音美好体（DouyinSansBold.ttf）打包到项目目录 `D:\video-analysis\fonts\DouyinSansBold.ttf`，FFmpeg烧字幕时用 `fontsdir` 或 ASS字幕里用绝对路径引用，不依赖系统Fonts目录：
```bash
# 方案1：FFmpeg subtitles滤镜指定fontsdir
ffmpeg -y -i input.mp4 -vf "subtitles='subs.srt':fontsdir='D\\:/video-analysis/fonts':force_style='FontName=DouyinSans Bold,...'" ...

# 方案2：Remotion方案，CSS @font-face引用本地文件
@font-face { font-family: 'DouyinSans'; src: url('./fonts/DouyinSansBold.ttf'); }
```
这样无论在哪台机器上都能正确使用字体，不会回退到系统默认字体。

**⚠️ 字幕字体、大小、位置必须参考对标视频！不要用固定值！**

**字幕参数提取流程（阶段二分析时完成）：**
1. 从对标视频抽帧中找到有字幕的帧
2. AI分析字幕的：字体风格、大小（相对画面比例）、颜色、描边、位置（底部/中部/上部）、距底边距离
3. 将提取的字幕参数写入 `style_template.json`：
```json
{
  "subtitle_style": {
    "font_name": "DouyinSans Bold",
    "font_size": 15,
    "primary_colour": "&H00FFFFFF",
    "outline_colour": "&H00000000",
    "border_style": 1,
    "outline": 1,
    "shadow": 0,
    "bold": 1,
    "alignment": 2,
    "margin_v": 3,
    "notes": "从对标视频帧分析提取的参数"
  }
}
```
4. 合成时从 `style_template.json` 读取字幕参数，不硬编码

**默认值（仅在无法分析对标视频字幕时使用）：**
```
FontName=DouyinSans Bold
FontSize=15
PrimaryColour=&H00FFFFFF  (白色)
OutlineColour=&H00000000  (黑色描边)
BorderStyle=1, Outline=1, Shadow=0, Bold=1
Alignment=2  (底部居中)
MarginV=3    (紧贴底部)
```

**关键规则：**
- 每条字幕**严格只一行，不允许换行**（≤15字为佳）
- **不要标点**——文案拆分时就去掉所有中文标点
- 字体、大小、位置**以对标视频为准**，不自作主张
- **字幕必须从最终视频音频生成时间戳**，不能从原始TTS音频（BGM混合后时间轴可能偏移）
- ASR只用于获取时间戳，文字内容用原始文案（零错别字）

**FFmpeg烧录命令（参数从style_template.json读取）：**
```bash
ffmpeg -y -i input_video.mp4 \
  -vf "subtitles='path/to/subtitles.srt':force_style='FontName={font_name},FontSize={font_size},PrimaryColour={primary_colour},OutlineColour={outline_colour},BorderStyle={border_style},Outline={outline},Shadow={shadow},Bold={bold},Alignment={alignment},MarginV={margin_v}'" \
  -c:v libx264 -preset slow -crf 18 \
  -c:a copy \
  -movflags +faststart \
  output_with_subs.mp4
```

**⚠️ Windows路径注意：SRT路径中的反斜杠要替换为正斜杠，冒号要转义为 `\:`**

### 图片动效

分析目标博主视频中图片的运动方式（下载Top3视频逐帧观察），复刻相同的动效。常见动效：

- **Ken Burns（缓慢缩放+平移）**：最常见，静态图缓慢放大或从左到右平移
- **渐变切换（淡入淡出）**：场景切换时淡入淡出
- **滑动切换**：下一张图从右侧/底部滑入
- **轻微呼吸感**：图片缓慢放大再缩小，循环
- **局部动态**：文字逐字出现、光效闪烁等

**ffmpeg实现**：
```bash
# Ken Burns 缓慢放大
zoompan=z='min(zoom+0.0005,1.3)':d=900:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'

# 淡入淡出转场
xfade=transition=fade:duration=0.5:offset=30
```

**要求**：观察博主视频实际动效类型并还原。复杂动画可用Pillow帧序列或Remotion实现。

### 章节进度条

**使用抖音平台自带的章节功能**，不要用ffmpeg叠加到视频画面上。章节条显示在视频画面外部（上方），是抖音原生UI。

在发布时，通过创作者平台的「视频章节」功能填入章节信息：
- 从文案结构提取章节标题和对应时间点
- 在发布页面「扩展信息 → 视频章节」中添加
- 抖音会自动生成进度条，显示在视频画面外面

## 混剪视频复刻流程（对标账号为视频混剪风格时）

当对标博主不是配图模式而是混剪视频时，使用以下流程：

### 1. 下载原视频并分析
```python
# 通过视频分析API下载
import requests
r = requests.get('http://localhost:18810/api/hybrid/video_data', 
    params={'url': '抖音视频链接'}, timeout=30)
data = r.json()['data']
video_url = data['video']['play_addr']['url_list'][0]
music_url = data['music']['play_url']['url_list'][0]
# 下载视频和BGM
```

### 2. 逐镜头拆解
```bash
# ffmpeg 按场景切换点抽帧
ffmpeg -i video.mp4 -vf "select=gt(scene,0.3)" -vsync vfr frames/scene_%04d.png
```
- AI 分析每帧：场景内容、镜头类型（特写/全景/航拍）、运动方式、时长
- 输出镜头清单 JSON：每个镜头的时间点、内容描述、运镜方式

### 3. BGM提取与缓存

**首次制作视频时提取BGM，保存后二次复用：**

```python
# 步骤1：从抖音API获取原始音频
music_url = data['music']['play_url']['url_list'][0]
# 下载保存到 D:\video-analysis\{博主名}\bgm_raw.mp3

# 步骤2：ffmpeg 转 wav
# ffmpeg -y -i bgm_raw.mp3 -ar 44100 -ac 2 bgm_raw.wav

# 步骤3：demucs 分离人声和BGM
import soundfile as sf, torch
from demucs.pretrained import get_model
from demucs.apply import apply_model

model = get_model('htdemucs')
model.eval()
data, sr = sf.read('bgm_raw.wav')
wav = torch.from_numpy(data.T).float()

# resample if needed (model.samplerate = 44100)
if sr != model.samplerate:
    ratio = model.samplerate / sr
    new_len = int(wav.shape[1] * ratio)
    wav = torch.nn.functional.interpolate(
        wav.unsqueeze(0), size=new_len, mode='linear', align_corners=False
    ).squeeze(0)
    sr = model.samplerate

ref = wav.mean(0)
wav_n = (wav - ref.mean()) / ref.std()
sources = apply_model(model, wav_n[None], device='cpu', progress=True)[0]
sources = sources * ref.std() + ref.mean()

names = model.sources  # ['drums', 'bass', 'other', 'vocals']
vi = names.index('vocals')
bgm = sum(sources[i] for i in range(len(names)) if i != vi)
sf.write('bgm_clean.wav', bgm.numpy().T, sr)  # 纯BGM
sf.write('vocals.wav', sources[vi].numpy().T, sr)  # 纯人声（备用）
```

**⚠️ 注意事项：**
- Windows 上 torchaudio 新版有 torchcodec 兼容问题，**用 soundfile 加载音频**，不要用 torchaudio.load()
- 8分钟音频 CPU 分离约需2分钟
- `pip install demucs soundfile` （demucs 会自动装 torch）

**缓存路径：**
```
D:\video-analysis\{博主名}\
├── bgm_raw.mp3        # 原始音频
├── bgm_raw.wav        # wav 格式
├── bgm_clean.wav      # demucs 分离后的纯BGM ← 二次复用这个
└── vocals.wav         # 分离出的人声（备用）
```

**二次使用时直接读取 bgm_clean.wav，不需要重新分离。**

### 4. 素材替换策略
根据原视频镜头清单，逐个替换素材：

| 原素材类型 | 替换方案 |
|-----------|---------|
| 历史剧片段 | 即梦生成同场景图/视频 |
| 纪录片画面 | Pexels/Pixabay免费素材 |
| 航拍/风景 | AI生成或素材库搜索 |
| 人物特写 | 即梦生成角色图 |
| 文字/数据 | Remotion 或 HTML截图生成 |

```python
# 即梦生成视频片段（如支持）
form = {
    'req_key': 'jimeng_video',  # 视频生成
    'prompt': '场景描述 + style_positive',
    ...
}

# 即梦生成图片 + Ken Burns 动效模拟视频
# 用已验证的 gen_all.py 模板
```

### 5. 按原节奏合成
- 保持原视频每个镜头的时长和切换节奏
- 新素材替换原画面，BGM和节奏不变
- 人声用TTS重新配音（一整条录制，不分段！）

```python
# 合成：图片/视频素材 + TTS音频 + BGM混合
# BGM混音参数：旁白volume=2.0，BGM volume=3.0
ffmpeg -i video_only.mp4 -i tts_audio.m4a -i bgm.mp3 \
    -filter_complex "[1:a]volume=2.0[voice];[2:a]volume=3.0[music];[voice][music]amix=inputs=2:duration=first[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -movflags +faststart final.mp4
```

### 6. 关键脚本路径
- 图片生成：`D:\video-analysis\output\银针试毒v4\gen_all.py`
- 视频合成：`D:\video-analysis\output\银针试毒v4\compose.py`
- 拼接+压缩：`D:\video-analysis\output\银针试毒v4\merge_v5.py`
- 腾讯云备份：`/home/ubuntu/scripts/jimeng/`

---

## 阶段6.5：生成高清视频链接（必须步骤）

**视频合成完成后，必须上传到腾讯云生成可预览的高清链接！**

**流程：**
1. 用Python paramiko上传 final.mp4 到腾讯云：
```python
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 密码从TOOLS.md读取（SSH到服务器查 /home/ubuntu/.credentials/accounts.md）
ssh.connect('106.55.158.137', username='ubuntu', password='密码')
sftp = ssh.open_sftp()
# 确保目录存在
try: sftp.mkdir('/home/ubuntu/www/videos/')
except: pass
sftp.put('D:\\video-analysis\\output\\{主题}\\final.mp4', f'/home/ubuntu/videos/{主题}.mp4')
```

2. Nginx已配置 `/videos/` 路径（如未配置需添加）：
```nginx
location /videos/ {
    alias /home/ubuntu/www/videos/;
    types { video/mp4 mp4; }
}
```

3. **发送链接给用户**：
```
🎬 视频已生成！高清预览：
http://bm.weiixxin.com/videos/{主题}.mp4
时长：X分X秒 | 分辨率：2560×1440
```

---

## 阶段6.8：复刻质量评估（必须步骤）

**视频合成完成后、交付给用户前，必须对复刻效果进行自评打分。**

### 评估流程

1. **准备对比素材**：
   - 从对标视频抽取3-5帧代表性画面
   - 从生成视频抽取对应时间点的画面
   - 读取对标视频转录文本 + 生成文案

2. **逐项打分（满分100分）**：

| 维度 | 权重 | 评分标准 |
|------|------|---------|
| **画风还原度** | 25分 | 色调、线条、质感、氛围是否与对标一致 |
| **文案风格** | 20分 | 语气、节奏、结构是否模仿到位 |
| **场景数量与节奏** | 15分 | 画面切换频率是否接近对标（不能太少太慢） |
| **字幕还原** | 10分 | 字体、大小、位置、颜色是否与对标一致 |
| **配音质量** | 10分 | TTS自然度、语速是否合适 |
| **BGM匹配** | 10分 | BGM风格是否合适、混音比例是否舒服 |
| **分辨率/画质** | 5分 | 分辨率与对标一致、画面清晰无模糊 |
| **整体观感** | 5分 | 作为独立作品的完成度和专业感 |

3. **输出评估报告**：
```
📊 复刻质量评估：XX/100

✅ 优点：
- xxx
- xxx

❌ 不足：
- xxx（扣X分）
- xxx（扣X分）

💡 改进建议：
- xxx
- xxx
```

4. **交付规则**：
   - **不论多少分都交付**，附上评估报告
   - **<70分时额外标注**：自动分析最大扣分项，给出具体改进建议，让用户决定是否要求修复

---

## 阶段七：发布

通过浏览器自动化发布到抖音：
1. 打开 `https://creator.douyin.com`
2. 上传视频文件
3. 填写标题、标签、描述
4. 选择封面
5. 发布

---

## 效率优化机制

### 并行执行
- 阶段五中 TTS配音 和 即梦生图 **同时执行**
- spawn多个子代理分别处理，不串行等待

### 缓存复用（同博主二次复刻全部跳过已有步骤）
- **博主数据缓存**：`videos.json` 增量更新，不重复抓取
- **参考视频缓存**：`ref_video.mp4` 已存在则跳过下载
- **抽帧缓存**：`frames/` 目录有文件则跳过抽帧
- **转录缓存**：`ref_transcript.txt` 已存在则跳过转录
- **画风模板缓存**：`style_template.json` 存博主视觉风格+字幕参数+内容类型，后续同博主视频直接复用
- **提示词优化缓存**：`prompt_optimization_log.json` 存在则直接用 `final_style_positive`，跳过阶段4.5
- **Few-shot文案缓存**：`copywriting_examples.json` 存博主典型文案片段，同博主不重复提取
- **BGM缓存**：`bgm_clean.wav` 已存在则跳过demucs分离
- **TTS声音固定**：zh-CN-YunxiNeural，不需要每次选择

**原则：同博主目录下已有的产出物一律复用，只生成本次视频特有的内容（文案、配图、合成）。**

### 减少token消耗
- analyze_data.py 输出结构化数据 + 推荐选题Top5，AI只做观点总结
- 画风模板缓存后，AI写prompt只需填场景描述，不用每次写完整风格描述
- 本地脚本处理：抓取/下载/转录/统计/TTS/生图/合成 全部本地执行

### 批量流水线
支持一次指定多个选题，pipeline并行生成多个视频：
```
选题1 → [文案→拆场景→生素材→合成] 
选题2 → [文案→拆场景→生素材→合成]  （并行）
选题3 → [文案→拆场景→生素材→合成]
```

---

## 输出文件结构

```
D:\video-analysis\
├── bgm\                         # BGM缓存
│   └── dance_for_me_wallis.mp3
├── {博主名}\                    # 博主数据（可复用）
│   ├── videos.json              # 视频元数据
│   ├── data_report.md           # 数据统计
│   ├── analysis_report.md       # AI分析报告
│   ├── style_template.json      # 画风模板缓存（含content_type）
│   ├── copywriting_examples.json # Few-shot文案样本缓存
│   ├── bgm_raw.mp3              # 博主视频原始音频
│   └── bgm_clean.wav            # demucs分离后的纯BGM（复用）
└── output\
    └── {主题}\                  # 视频制作输出
        ├── script.md            # 文案脚本
        ├── prompts.json         # 场景提示词
        ├── images\              # 场景图
        ├── quality_log.json     # 生图质量校验日志
        ├── narration.mp3        # TTS配音
        └── final.mp4            # 最终视频
```


