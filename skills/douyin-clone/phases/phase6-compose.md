<!-- 本文件是 douyin-clone 技能的子文件，完整流程见 ../SKILL.md -->

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


