---
name: douyin-clone
description: 复刻抖音博主完整流程。从分析目标博主视频风格、选题规律、数据表现，到生成原创文案、AI配图、TTS配音、BGM合成、最终视频输出。当用户说"复刻博主"、"模仿抖音号"、"分析抖音博主"、"做一个类似XX的视频"时触发。
---

# 复刻抖音博主

完整流程分7个阶段，按顺序执行。每个阶段完成后向用户汇报进度。
**TTS和生图可并行执行以提高效率。**

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

**可选：深度文案分析**（需要下载+转录）
```powershell
python scripts/download_videos.py -i videos.json -o . --top 10
python scripts/transcribe.py -d . -m medium
```

## 阶段三：写文案

1. 从 data_report.md 的「推荐选题Top5」中选择，或根据分析报告确定选题
2. 按目标博主的文案结构写原创文案：
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

### 5.1 AI配图（即梦API）

**⚠️ 必须使用标准化脚本，不要自己写API调用代码！**

```powershell
# 环境变量必须是 VOLC_AK 和 VOLC_SK（不是 VOLC_ACCESSKEY！）
python D:\video-analysis\scripts\jimeng_gen.py prompts.json -o images/
```

**即梦API关键参数（子代理必读，多次出错的地方）：**

| 参数 | ✅ 正确 | ❌ 常见错误 |
|------|---------|------------|
| req_key | `jimeng_t2i_v40` | `jimeng_high_aes_general_v21_L` |
| task_id位置 | `resp['data']['task_id']` | `resp['task_id']` |
| status位置 | `r['data']['status']` | `r['status']`（永远为空！） |
| image_urls位置 | `r['data']['image_urls']` | `r['image_urls']` |
| 环境变量 | `VOLC_AK` / `VOLC_SK` | `VOLC_ACCESSKEY` |
| 必要参数 | `logo_info: {add_logo: False}` | `negative_prompt, seed, scale, ddim_steps` |

**所有响应数据都在 `data` 字段里，不在顶层！**

排查详情见：`memory/jimeng-api-fix.md`
标准脚本：`D:\video-analysis\scripts\jimeng_gen.py`

### 5.2 TTS配音（与5.1并行）

**本地脚本：**
```powershell
python scripts/generate_tts.py script.md -o narration.mp3
```

- `scripts/generate_tts.py` — 从script.md提取纯文本，edge-tts生成音频
- **默认声音**：`zh-CN-YunxiNeural`（固定使用，除非用户要求更换）

### 5.3 BGM

- **默认BGM**：Dance For Me Wallis
- **本地路径**：`D:\video-analysis\bgm\dance_for_me_wallis.mp3`
- 首次使用时下载并存到上述路径，之后直接从本地调用
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

**步骤3：烧录字幕**
```bash
# 先从raw_video提取音频→FunASR生成SRT→再烧录
ffmpeg -y -i raw_video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 extracted_audio.wav
# 用FunASR Paraformer生成SRT（见上方代码）
ffmpeg -y -i raw_video.mp4 -vf "subtitles='subs.srt':force_style='...'" -c:v libx264 -preset slow -crf 18 -c:a copy -movflags +faststart final.mp4
```

### 字幕烧录（必须步骤）

视频必须烧录白色字幕，样式参考奇异史：

**字幕生成流程：**
1. 从合成好的视频（含BGM+配音）中提取音频
2. 用**FunASR Paraformer-zh**对提取的音频生成SRT字幕（**不要用Whisper！** Paraformer中文错别字率远低于Whisper，详见 memory/asr-comparison.md）
3. 用FFmpeg subtitles滤镜烧录到视频上

**ASR模型选择（重要！）：**
- ✅ **FunASR Paraformer-zh**（首选）：中文错别字率最低，自带标点和VAD，显存仅1-2GB
- ✅ **FunASR SenseVoice-Small**（备选）：速度最快，准确率接近Paraformer
- ❌ **Whisper small/medium**（禁用）：中文专有名词错误率高（如"砒霜"→"披霜"），无标点

**FunASR字幕生成代码：**
```python
from funasr import AutoModel
import re

# 初始化（首次会下载模型约2GB）
asr_model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc",
)

# 生成带时间戳的结果
result = asr_model.generate(input="extracted_audio.wav", return_raw_text=False)

# 转为SRT格式
def to_srt(result):
    srt_lines = []
    for i, seg in enumerate(result[0]["sentence_info"], 1):
        start_ms = seg["start"]
        end_ms = seg["end"]
        text = seg["text"]
        start_t = f"{start_ms//3600000:02d}:{(start_ms%3600000)//60000:02d}:{(start_ms%60000)//1000:02d},{start_ms%1000:03d}"
        end_t = f"{end_ms//3600000:02d}:{(end_ms%3600000)//60000:02d}:{(end_ms%60000)//1000:02d},{end_ms%1000:03d}"
        srt_lines.append(f"{i}\n{start_t} --> {end_t}\n{text}\n")
    return "\n".join(srt_lines)
```

**字幕样式参数（ASS force_style）：**
```
FontName=Microsoft YaHei
FontSize=19
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
- 每条字幕**只显示一行**，不允许换行（≤15字为佳）
- 字体大小和位置参考奇异史原作：白色粗体微软雅黑，黑色描边，贴画面底部
- **字幕必须从最终视频音频生成**，不能从原始TTS音频生成（BGM混合后时间轴可能偏移）
- **ASR用FunASR Paraformer-zh**（不用Whisper），语言自动识别中文

**FFmpeg烧录命令：**
```bash
ffmpeg -y -i input_video.mp4 \
  -vf "subtitles='path/to/subtitles.srt':force_style='FontName=Microsoft YaHei,FontSize=19,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=1,Shadow=0,Bold=1,Alignment=2,MarginV=3'" \
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
- **画风模板缓存**：`style_template.json` 存博主视觉风格，后续同博主视频直接复用
- **BGM本地缓存**：`D:\video-analysis\bgm\` 下载一次永久复用
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
│   └── style_template.json      # 画风模板缓存
└── output\
    └── {主题}\                  # 视频制作输出
        ├── script.md            # 文案脚本
        ├── prompts.json         # 场景提示词
        ├── images\              # 场景图
        ├── narration.mp3        # TTS配音
        └── final.mp4            # 最终视频
```
