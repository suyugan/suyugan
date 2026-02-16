---
name: douyin-clone
description: 复刻抖音博主完整流程。从分析目标博主视频风格、选题规律、数据表现，到生成原创文案、AI配图、TTS配音、BGM合成、最终视频输出。当用户说"复刻博主"、"模仿抖音号"、"分析抖音博主"、"做一个类似XX的视频"时触发。
---

# 复刻抖音博主

完整流程分7个阶段，按顺序执行。每个阶段完成后向用户汇报进度。
**TTS和生图可并行执行以提高效率。**

## ⚠️ 子代理Spawn规则

**即梦生图必须用标准spawn模板，不允许子代理自己写API调用代码！**

### 即梦生图子代理spawn模板（直接复制使用）：
```
sessions_spawn({
  label: "{主题}-即梦生图",
  task: `即梦批量生图任务。所有输出用中文。

工作目录：D:\\video-analysis\\output\\{主题}\\
读取 prompts.json 获取所有场景prompt。

【生图流程 - 严格按此执行，不要自己写JS/API代码！】

1. browser tabs (profile="openclaw", target="host") 找到 jimeng.jianying.com 的 targetId

2. 对每个场景循环：
   a) 生成提交JS：
      chcp 65001
      python D:\\video-analysis\\scripts\\jimeng_fetch_gen.py --action generate --prompt "场景prompt" --ratio "16:9" --json
      → 拿到 {"js": "...", "submit_id": "xxx"}

   b) browser evaluate执行提交JS（targeid=即梦tab的targetId）

   c) 等3秒

   d) 生成轮询JS：
      python D:\\video-analysis\\scripts\\jimeng_fetch_gen.py --action poll --submit-id "submit_id" --json

   e) 间隔5秒轮询直到status=done（超时120秒）

   f) curl下载第一张图到 images/scene_XX.webp

3. 每5个场景发一次进度更新
4. 完成后汇报生成了多少张图

脚本已内置sign签名算法，不需要自己算sign。
如果中文乱码先执行 chcp 65001。`
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
| **真人出镜** | 封面有真人，vlog/口播类标签 | ⚠️ 建议转为配图模式复刻 |
| **实拍** | 封面为实景照片，生活/旅行/美食类标签 | 根据具体情况选择配图或混剪流程 |

3. **真人出镜类特殊处理**：
   - 自动输出建议：「该博主为真人出镜类型，建议转为配图口播模式复刻」
   - 原因：AI无法生成一致的真人形象，强行复刻会导致人物不统一、辨识度低
   - 用户确认后，按配图口播流程执行

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

---

## 阶段二：AI分析出报告

**需要token的部分：** 读取 data_report.md（+ 可选的转录文本），由AI生成完整分析报告，包括：
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

文案写完后，AI自动完成：

1. **拆分片段**：按内容逻辑将文案拆成若干片段，每个片段对应一个画面场景。**⚠️ 数量严禁固定为10个！必须根据文案实际内容结构决定，可能是5个、8个、12个或其他任意数量。不要凑数，不要硬拆，每个片段必须有独立的画面意义。**
2. **生成提示词**：为每个片段生成即梦图片提示词，画面要精准匹配该片段的文案内容
3. **复用画风模板**：如果 `style_template.json` 存在，读取 `style_positive` 和 `style_negative`，每个场景提示词 = 场景描述 + style_positive。**必须拼接风格模板，不能只写场景描述！**
4. **输出 prompts.json**：

```json
{
  "scenes": [
    {
      "scene_num": 1,
      "text": "对应的文案片段内容...",
      "prompt": "帮我生成图片：...\n背景：...\n风格：...\n氛围：...\n构图：...。比例 X:X。"
    }
  ]
}
```

**提示词格式**（必须严格按此结构）：
```
{场景主体描述，人物外貌/动作/表情/服装，背景环境}，{style_positive从style_template.json读取}
```

**拼接规则**：
- 前半段 = 场景内容描述（每个场景不同）
- 后半段 = style_positive（所有场景相同，从模板读取）
- 用中文逗号连接
- style_negative 作为反向提示词传给即梦API（如API支持）

**要求**：
- 每个prompt必须与该片段文案内容强关联，不能泛泛而谈
- 画面风格保持统一（同一套视觉语言）
- **图片尺寸**：从视频元数据获取实际画面宽高，避免变形
- 保存到 `D:\video-analysis\output\{主题}\prompts.json`

## 阶段五：生成素材（TTS和生图并行）

⚡ **TTS配音和即梦生图可以同时执行，不需要串行等待。**

### 5.1 AI配图（即梦无感方案 — 逆向签名算法）

**⚠️ 使用即梦网页版内部API（Fetch方式），不走官方API！无需API key，通过browser evaluate在已登录的即梦网页中直接调用。**

**⚠️⚠️⚠️ 子代理必读：必须使用下面的标准脚本，严禁自己写JS/API调用代码！脚本已内置sign签名算法（MD5逆向），自己写会因为缺少签名报1002错误！**

**前置条件：** openclaw浏览器中即梦网页版（jimeng.jianying.com）已登录。

**标准脚本路径：**
- 单张生成JS：`D:\video-analysis\scripts\jimeng_fetch_gen.py`
- 批量生成：`D:\video-analysis\scripts\jimeng_batch_fetch.py`

**逐步调用流程（子代理必须严格按此执行）：**

```
步骤1：获取即梦tab
  browser({ action: "tabs", profile: "openclaw", target: "host" })
  → 找到 url 包含 jimeng.jianying.com 的tab，记下 targetId

步骤2：读取 prompts.json
  读取所有场景的 prompt 文本

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
      → 输出JSON：{"js": "..."}

  3e. 间隔5秒轮询，直到返回 status=done：
      browser({ action: "act", ..., request: { kind: "evaluate", fn: "<轮询js>" } })
      → 返回 {"status":"done","urls":["url1","url2",...]} 时完成
      → 超时120秒放弃该场景

  3f. 下载第一张图片：
      curl -o images/scene_XX.webp "<urls[0]>"

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

**本地脚本：**
```powershell
python scripts/generate_tts.py script.md -o narration.mp3
```

- `scripts/generate_tts.py` — 从script.md提取纯文本，edge-tts生成音频
- **默认声音**：`zh-CN-YunxiNeural`（固定使用，除非用户要求更换）

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
ffmpeg -y -i narration.mp3 -i bgm.mp3 -filter_complex "[0:a]volume=1.0[voice];[1:a]volume=0.25,afade=t=in:st=0:d=2[music];[voice][music]amix=inputs=2:duration=first[a]" -map "[a]" -c:a aac -b:a 192k mixed_audio.m4a
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

**字幕生成代码（方案二：原始文案+ASR时间戳）：**
```python
import re
from funasr import AutoModel

# 1. 原始文案按句拆分（去标点）
def split_sentences(script_text):
    """按句号、问号、感叹号等拆分，去掉所有标点"""
    sentences = re.split(r'[。！？\n]+', script_text)
    sentences = [re.sub(r'[，、；：""''……——《》（）\(\)「」【】]', '', s).strip() for s in sentences]
    return [s for s in sentences if s]

# 2. ASR获取时间戳
asr_model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc",
)
result = asr_model.generate(input="extracted_audio.wav")

# 3. 提取ASR时间戳（丢弃ASR文字）
asr_segments = result[0]["sentence_info"]
timestamps = [(seg["start"], seg["end"]) for seg in asr_segments]

# 4. 原始文案 + 时间戳配对生成SRT
original_sentences = split_sentences(script_text)

def to_srt(sentences, timestamps):
    srt_lines = []
    # 如果句子数和时间戳数不一致，按较少的来配对
    count = min(len(sentences), len(timestamps))
    for i in range(count):
        start_ms, end_ms = timestamps[i]
        text = sentences[i]
        start_t = f"{start_ms//3600000:02d}:{(start_ms%3600000)//60000:02d}:{(start_ms%60000)//1000:02d},{start_ms%1000:03d}"
        end_t = f"{end_ms//3600000:02d}:{(end_ms%3600000)//60000:02d}:{(end_ms%60000)//1000:02d},{end_ms%1000:03d}"
        srt_lines.append(f"{i+1}\n{start_t} --> {end_t}\n{text}\n")
    return "\n".join(srt_lines)

with open("subs.srt", "w", encoding="utf-8") as f:
    f.write(to_srt(original_sentences, timestamps))
```

**热词增强**（提升时间戳对齐精度）：
```python
result = asr_model.generate(
    input="extracted_audio.wav",
    hotword="三氧化二砷 砒霜 鹤顶红 见血封喉"  # 按视频内容填写
)
```

**字幕样式参数（ASS force_style）：**
```
FontName=DouyinSans Bold
FontSize=13
PrimaryColour=&H00FFFFFF  (白色)
OutlineColour=&H00000000  (黑色描边)
BorderStyle=1
Outline=1
Shadow=0
Bold=1
Alignment=2  (底部居中)
MarginV=3    (紧贴底部)
```

**关键规则：**
- 每条字幕**严格只一行，不允许换行**（≤15字为佳）
- **不要标点**——文案拆分时就去掉所有中文标点
- 字体使用**DouyinSans Bold（抖音体）**，FontSize=13
- **字幕必须从最终视频音频生成时间戳**，不能从原始TTS音频（BGM混合后时间轴可能偏移）
- ASR只用于获取时间戳，文字内容用原始文案（零错别字）

**FFmpeg烧录命令：**
```bash
ffmpeg -y -i input_video.mp4 \
  -vf "subtitles='path/to/subtitles.srt':force_style='FontName=DouyinSans Bold,FontSize=13,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,Shadow=0,Bold=1,Alignment=2,MarginV=3'" \
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
# BGM 音量降低到 20-30%，人声为主
ffmpeg -i video_only.mp4 -i tts_audio.m4a -i bgm.mp3 \
    -filter_complex "[1:a]volume=1.0[voice];[2:a]volume=0.25[music];[voice][music]amix=inputs=2:duration=first[a]" \
    -map 0:v -map "[a]" -c:v copy -c:a aac -movflags +faststart final.mp4
```

### 6. 关键脚本路径
- 图片生成：`D:\video-analysis\output\银针试毒v4\gen_all.py`
- 视频合成：`D:\video-analysis\output\银针试毒v4\compose.py`
- 拼接+压缩：`D:\video-analysis\output\银针试毒v4\merge_v5.py`
- 腾讯云备份：`/home/ubuntu/scripts/jimeng/`

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

### 缓存复用
- **博主数据缓存**：videos.json增量更新，不重复抓取
- **画风模板缓存**：`style_template.json` 存博主视觉风格+内容类型，后续同博主视频直接复用
- **Few-shot文案缓存**：`copywriting_examples.json` 存博主典型文案片段，同博主不重复提取
- **TTS声音固定**：zh-CN-YunxiNeural，不需要每次选择

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
