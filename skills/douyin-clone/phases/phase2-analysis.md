<!-- 本文件是 douyin-clone 技能的子文件，完整流程见 ../SKILL.md -->

## 全局上下文（必读）
- **目标**：复刻目标博主风格，制作同风格原创视频
- **风格**：本阶段产出 style_template.json（画风/配色/字幕/语气）
- **质量红线**：风格必须匹配、字幕必须同步、图≥25张
- **上游输出**：阶段一的 `video_data.json`、抽帧关键帧、Whisper转录
- **下游输入**：本阶段产出 `analysis_report.md`（分析报告）、`style_template.json`（风格模板）、选题列表供阶段三使用

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

#### 步骤5：风格识别自动校验

**风格识别容易出错（比如把插画误判为火柴人），一旦错了后面全盘皆输。**

1. 把步骤4的风格分析结果整理成具体特征表（不要用单一标签）：
   ```
   - 线条：粗线条/细线条/无线条
   - 人物：写实/卡通/Q版/简笔/3D渲染
   - 上色：平涂/渐变/水彩/无填色
   - 背景：纯色/场景/留白
   - 质感：精致/粗犷/极简/手绘感
   - 色调：暖色/冷色/黑白/高饱和
   ```
   **禁止用"火柴人""简笔画"等模糊标签一笔带过！必须逐维度描述。**

2. 用识别出的风格生成**1张测试图**

3. AI自动对比测试图与原视频参考帧，检查6个维度是否一致

4. 把风格特征表 + 测试图 + 参考帧一起发给用户（仅通知，不阻塞流程）

5. 如果AI自检发现明显偏差（≥2个维度不一致），调整提示词重新生成测试图，最多重试2次

#### 步骤6：分析文案结构
从转录文本中提取文案结构模板：

| 结构元素 | 提取内容 |
|---------|---------|
| **开头hook类型** | 反问式/共鸣式/悬念式/数据冲击式/反常识式 |
| **正文节奏** | 论点-论据交替/递进深入/故事线/对比反转 |
| **结尾套路** | 金句收尾/引导互动/情感升华/悬念钩子 |
| **语气特点** | 口语化程度、人称视角、情绪基调 |
| **节奏特征** | 句子长短交替规律、停顿位置 |

#### 步骤7：保存分析结果

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
