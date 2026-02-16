# Subtitle ASR Skill

中文语音识别与字幕生成。用 FunASR Paraformer-zh 替代 Whisper，中文准确率大幅提升。

**触发词**: 字幕、语音识别、ASR、转录、transcribe、subtitle

---

## 方案选择

| 模型 | 中文准确率 | 显存 | 速度 | 标点 | 推荐 |
|------|-----------|------|------|------|------|
| **FunASR Paraformer-zh** | ⭐⭐⭐⭐⭐ | 1-2GB | RTF 0.035 | ✅ | 🏆 首选 |
| **FunASR SenseVoice-Small** | ⭐⭐⭐⭐⭐ | ~1GB | RTF 0.031 | ✅ | 🥈 备选（带情感标签） |
| **Whisper small** | ⭐⭐⭐ | 2GB | RTF ~0.17 | ❌ | ❌ 中文不推荐 |
| **Whisper large-v3** | ⭐⭐⭐⭐ | 10GB | 慢 | ✅ | ❌ 显存太大 |

### 实测对比（银针试毒60秒旁白）

- **Whisper small**: 7处错别字，无标点（披霜→砒霜、鹤鼎红→鹤顶红、剑血蜂猴→见血封喉…）
- **Paraformer-zh**: 2处小错，有标点，中文专有名词全对
- **SenseVoice-Small**: 3处小错，有标点，额外输出情感/语种标签

---

## 安装

```bash
pip install funasr modelscope torch torchaudio
```

> ⚠️ FunASR 1.3.1 的 `load_pretrained_model.py` line 44 有 `copy.deepcopy` 会导致内存翻倍，内存紧张时需手动去掉。

---

## 使用方法

### 方案1：Paraformer-zh（首选）

```python
from funasr import AutoModel

# 初始化（首次下载模型约2GB：主模型+VAD+标点）
asr_model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc",
    # spk_model="cam++",  # 可选：说话人分离
)

def transcribe(audio_path: str) -> str:
    """转录音频，返回带标点的中文文本"""
    result = asr_model.generate(input=audio_path)
    return result[0]["text"]

# 带时间戳的转录（用于字幕）
def transcribe_with_timestamps(audio_path: str) -> list:
    """返回带时间戳的分段结果，可直接生成SRT"""
    result = asr_model.generate(input=audio_path)
    return result[0]  # 包含 timestamp 字段
```

### 方案2：SenseVoice-Small（备选，带情感识别）

```python
from funasr import AutoModel

model = AutoModel(model="iic/SenseVoiceSmall", trust_remote_code=True)
result = model.generate(input="audio.wav", language="zh", use_itn=True)
# 输出可能含标签如 <|ANGRY|>，需后处理去除
text = result[0]["text"]
```

### 方案3：Whisper + LLM纠错（兜底，最小改动）

```python
# 保留现有Whisper small，用LLM修正错别字
prompt = f"请修正以下语音识别文本中的错别字，只改错字不改内容：\n{whisper_output}"
```

---

## 生成SRT字幕文件

```python
def generate_srt(result, output_path: str):
    """从FunASR结果生成SRT字幕文件"""
    sentences = result[0].get("sentence_info", result[0].get("timestamp", []))
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(sentences, 1):
            start = seg.get("start", seg[0]) if isinstance(seg, list) else seg["start"]
            end = seg.get("end", seg[1]) if isinstance(seg, list) else seg["end"]
            text = seg.get("text", "") if isinstance(seg, dict) else ""
            f.write(f"{i}\n")
            f.write(f"{ms_to_srt(start)} --> {ms_to_srt(end)}\n")
            f.write(f"{text}\n\n")

def ms_to_srt(ms: int) -> str:
    """毫秒转SRT时间格式"""
    h = ms // 3600000
    m = (ms % 3600000) // 60000
    s = (ms % 60000) // 1000
    ms_r = ms % 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms_r:03d}"
```

---

## Docker服务端部署（支持并发）

```bash
docker pull registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-online-cpu-0.1.12
```

---

## 云端API备选

| 服务商 | 准确率 | 免费额度 |
|--------|--------|---------|
| 讯飞 | ⭐⭐⭐⭐⭐ | 5万次/年 |
| 阿里云 | ⭐⭐⭐⭐⭐ | 按时长计费（底层就是Paraformer） |
| 百度 | ⭐⭐⭐⭐ | 较多 |
| 腾讯 | ⭐⭐⭐⭐ | 15小时/月 |

---

## 集成到视频分析流程

替换现有 Whisper 调用：

```python
# 旧：whisper
# import whisper
# model = whisper.load_model("small")
# result = model.transcribe(audio_path, language="zh")

# 新：FunASR Paraformer
from funasr import AutoModel
asr_model = AutoModel(model="paraformer-zh", vad_model="fsmn-vad", punc_model="ct-punc")
result = asr_model.generate(input=audio_path)
text = result[0]["text"]
```

---

## 热词增强

FunASR 支持热词定制，提升专业术语识别率：

```python
result = asr_model.generate(
    input="audio.wav",
    hotword="三氧化二砷 砒霜 鹤顶红 见血封喉"
)
```
