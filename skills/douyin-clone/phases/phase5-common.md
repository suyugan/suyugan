<!-- 本文件是 douyin-clone 技能的子文件，完整流程见 ../SKILL.md -->
<!-- phase5-common: TTS配音 + BGM提取 + 质量校验（所有模式共用） -->

## 阶段五：生成素材（通用部分）

⚡ **TTS配音和生图/视频/动画可以同时执行，不需要串行等待。**

素材生成根据 content_type 分三条路：
- 配图口播 → `phase5a-jimeng-image.md`
- 视频模式 → `phase5b-jimeng-video.md`
- 动画模式 → `phase5c-remotion.md`

以下是三条路共用的 TTS、BGM 和质量校验流程。

---

### 5.1.1 生成质量校验

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

---

### 5.2 TTS配音

**⚠️ 配音必须复刻对标博主的声音特征！不再使用固定声音！**

#### 5.2.1 声音特征分析（阶段二完成，写入style_template.json）

从对标视频的音频中分析声音特征：
```python
# 1. demucs分离出纯人声（vocals.wav 已在5.3 BGM提取时生成）
# 2. 用ffprobe分析音频参数
# 3. AI听音分析（性别、年龄感、语速、音调高低、情绪基调、口音特点）
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
    "volume_ratio": { "voice_db": -12, "bgm_db": -18 }
  }
}
```

#### 5.2.2 音色克隆（GPT-SoVITS，推荐方案）

| 工具 | 克隆质量 | 所需样本 | 推荐 |
|------|---------|---------|------|
| **GPT-SoVITS** | ⭐⭐⭐⭐⭐ | 5-30秒 | 🏆 首选 |
| **fish-speech** | ⭐⭐⭐⭐ | 10秒 | 🥈 备选 |
| **edge-tts匹配** | ⭐⭐ | 不需要 | 降级方案 |

```python
# 步骤1：准备参考音频
ffmpeg -y -ss 5 -t 20 -i vocals.wav -acodec pcm_s16le -ar 32000 -ac 1 ref_voice.wav

# 步骤2：零样本推理
from GPT_SoVITS.inference import TTSInference
tts = TTSInference(
    gpt_model="pretrained_models/gsv-v2final-pretrained/s1bert25hz-5kh-longer-epoch=12-step=369668.ckpt",
    sovits_model="pretrained_models/gsv-v2final-pretrained/s2G2333k.pth"
)
tts.synthesize(
    text="要合成的完整文案文本",
    ref_audio="ref_voice.wav",
    ref_text="参考音频对应的文字内容",
    output="narration_cloned.wav",
    speed=1.0
)
```

**缓存**：参考音频保存到 `D:\video-analysis\{博主名}\ref_voice.wav`，同博主复用。

#### 5.2.3 语速匹配
```python
ref_wpm = ref_char_count / (ref_duration / 60)  # 从对标视频计算
speed_ratio = target_duration / actual_tts_duration  # GPT-SoVITS调speed
rate = f"+{int((ref_wpm/250 - 1) * 100)}%"  # edge-tts调rate
```

#### 5.2.4 降级方案（无GPU时）
```python
VOICE_MAP = {
    ("male", "young", "calm"): "zh-CN-YunxiNeural",
    ("male", "young", "energetic"): "zh-CN-YunjianNeural",
    ("male", "mature", "authoritative"): "zh-CN-YunyeNeural",
    ("female", "young", "warm"): "zh-CN-XiaoxiaoNeural",
    ("female", "young", "cheerful"): "zh-CN-XiaohanNeural",
}
```

优先级：GPT-SoVITS克隆 > fish-speech克隆 > edge-tts匹配

---

### 5.3 BGM（从对标博主视频提取）

**不再使用默认BGM。必须从对标博主的热门视频中提取。**

1. 获取博主热门视频的 `music.play_url`
2. 下载到 `D:\video-analysis\{博主名}\bgm_raw.mp3`
3. demucs分离人声 → 纯BGM `bgm_clean.wav`
4. 缓存复用：同博主后续视频直接用 `bgm_clean.wav`

**缓存路径：**
```
D:\video-analysis\{博主名}\
├── bgm_raw.mp3      # 原始音频
├── bgm_clean.wav    # 纯BGM ← 复用这个
└── vocals.wav       # 分离出的人声
```

⚠️ Windows用soundfile加载音频，不要用torchaudio.load()
```python
# Windows上demucs的正确音频加载方式
# pip install soundfile
# demucs会自动检测并用soundfile替代torchaudio
# 如果仍报错，设置环境变量：
# $env:TORCHAUDIO_BACKEND="soundfile"
```
⚠️ bgm_clean.wav已存在则跳过分离

---

### 混音参数
- 旁白 volume=2.0，BGM volume=3.0（即0.75相对比例）
```bash
ffmpeg -y -i narration.wav -i bgm_clean.wav \
  -filter_complex "[0:a]loudnorm=I={voice_lufs}[voice];[1:a]loudnorm=I={bgm_lufs}[music];[voice][music]amix=inputs=2:duration=first[a]" \
  -map "[a]" -c:a aac -b:a 192k mixed_audio.m4a
```
