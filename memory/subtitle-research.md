# 短视频字幕生成方案调研

> 调研日期：2026-02-16
> 背景：当前使用 Whisper small 生成中文字幕，错别字多，需要更好的方案。

---

## 一、问题分析

Whisper small (244M参数) 中文识别差的原因：
- 模型太小，中文训练数据占比低
- Whisper 是多语言模型，中文不是强项
- small 模型对同音字/近音字区分能力弱
- 没有中文语言模型做后处理

---

## 二、方案对比

### 方案1：剪映（CapCut）自动字幕

**简介**：字节跳动出品，内置语音识别，中文识别质量很高（用的是字节内部ASR）。

| 项目 | 说明 |
|------|------|
| **准确率** | ⭐⭐⭐⭐⭐ 中文识别顶级，错别字极少 |
| **API/命令行** | ❌ 无官方API，无命令行工具 |
| **批量处理** | ❌ 只能在GUI中逐个操作 |
| **部署难度** | 低（装软件即可），但无法自动化 |
| **成本** | 免费（专业版部分功能收费） |
| **适合自动化** | ❌ 不适合 — 无API，无法集成到流水线 |

**结论**：质量最好但无法自动化，排除。

---

### 方案2：FunASR + Paraformer-large（⭐推荐）

**简介**：阿里达摩院开源的语音识别工具包，Paraformer-large 是其核心中文ASR模型。非自回归架构，速度快、中文准确率高。

| 项目 | 说明 |
|------|------|
| **准确率** | ⭐⭐⭐⭐⭐ 中文ASR开源最强之一，CER(字错误率) 约3-5%，远低于Whisper |
| **显存需求** | ~1-2GB（非自回归模型，很轻量） |
| **部署难度** | 低 — `pip install funasr`，几行代码即可 |
| **成本** | 完全免费开源 |
| **适合自动化** | ✅ 完美 — Python API，支持服务端部署 |
| **额外功能** | 带标点恢复、VAD、时间戳、热词定制 |

**快速使用**：
```python
from funasr import AutoModel

model = AutoModel(
    model="paraformer-zh",  # 或 "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
    vad_model="fsmn-vad",
    punc_model="ct-punc",
    spk_model="cam++",  # 可选：说话人分离
)
result = model.generate(input="audio.wav")
print(result[0]["text"])
```

**服务端部署**（支持并发）：
```bash
# Docker一键部署
docker pull registry.cn-hangzhou.aliyuncs.com/funasr_repo/funasr:funasr-runtime-sdk-online-cpu-0.1.12
```

---

### 方案3：SenseVoice（FunAudioLLM）

**简介**：阿里通义实验室2024年发布的语音理解模型，支持50+语言，中文表现优异。

| 项目 | 说明 |
|------|------|
| **准确率** | ⭐⭐⭐⭐⭐ 官方称超越Whisper，中文表现极好 |
| **速度** | 极快 — 10秒音频仅需70ms推理（比Whisper-Large快15倍） |
| **显存需求** | SenseVoice-Small: ~1GB |
| **部署难度** | 低 — 通过FunASR框架使用 |
| **成本** | 免费开源 |
| **适合自动化** | ✅ 完美 |
| **额外功能** | 情绪识别、音频事件检测（鼓掌/笑声/BGM等） |

**快速使用**：
```python
from funasr import AutoModel

model = AutoModel(model="iic/SenseVoiceSmall", trust_remote_code=True)
result = model.generate(input="audio.wav", language="zh", use_itn=True)
print(result[0]["text"])
```

---

### 方案4：Whisper large-v3

| 项目 | 说明 |
|------|------|
| **准确率** | ⭐⭐⭐⭐ 比small好很多，但中文仍不如Paraformer/SenseVoice |
| **显存需求** | ~10GB VRAM（large-v3 1.55B参数） |
| **部署难度** | 低 |
| **成本** | 免费，但需要大显存GPU |
| **适合自动化** | ⚠️ 显存限制，我们机器可能OOM |

**替代**：`whisper-large-v3-turbo` 可降低显存到 ~6GB，但中文质量提升有限。

**结论**：显存是硬伤，且中文准确率不如国产方案，不推荐。

---

### 方案5：云端语音识别API

| 服务商 | 准确率 | 价格 | 备注 |
|--------|--------|------|------|
| **讯飞** | ⭐⭐⭐⭐⭐ | 免费额度5万次/年，之后约0.033元/15秒 | 中文最强商用ASR |
| **百度** | ⭐⭐⭐⭐ | 免费额度较多 | 性价比高 |
| **腾讯** | ⭐⭐⭐⭐ | 每月15小时免费 | 质量不错 |
| **阿里云** | ⭐⭐⭐⭐⭐ | 按时长计费 | 用的就是Paraformer |

| 项目 | 说明 |
|------|------|
| **部署难度** | 极低（调API即可） |
| **适合自动化** | ✅ 适合 |
| **缺点** | 有成本、依赖网络、数据隐私 |

---

### 方案6：LLM后处理纠错（Whisper + Claude/GPT纠错）

**思路**：保留现有Whisper small，用LLM修正错别字。

```python
# 示例prompt
prompt = f"""请修正以下语音识别文本中的错别字，只改错字不改内容：
{whisper_output}"""
```

| 项目 | 说明 |
|------|------|
| **准确率提升** | ⭐⭐⭐⭐ 能修正大部分同音字错误 |
| **成本** | 每次调用LLM API费用（Claude约$0.003-0.01/次） |
| **部署难度** | 极低 |
| **适合自动化** | ✅ 适合 |
| **缺点** | 增加延迟；LLM可能"过度纠正"改变原意；专业术语可能改错 |

---

### 方案7：主流短视频创作者的做法

调研结论：
1. **大部分创作者用剪映**：自动字幕 → 手动校对 → 导出
2. **专业团队**：讯飞听见/网易见外 → 人工校对
3. **技术型创作者**：Whisper large + 手动校对
4. **批量生产团队**：云端API（讯飞/阿里）+ 自动化脚本

---

## 三、最终推荐方案

### 🏆 首选：FunASR Paraformer-large（或SenseVoice）

**理由**：
1. ✅ 完全免费开源
2. ✅ 中文识别准确率顶级（开源最强）
3. ✅ 显存需求极低（1-2GB，不会OOM）
4. ✅ 速度快（非自回归，比Whisper快5-10倍）
5. ✅ 自带标点恢复和VAD
6. ✅ pip install 即可使用，集成简单
7. ✅ 支持Docker服务端部署

### 实施步骤

```bash
# 1. 安装
pip install funasr modelscope torch torchaudio

# 2. 替换现有Whisper调用
```

```python
# 替换 whisper 为 funasr
from funasr import AutoModel

# 初始化（首次会下载模型约1GB）
asr_model = AutoModel(
    model="paraformer-zh",
    vad_model="fsmn-vad",
    punc_model="ct-punc",
)

def transcribe(audio_path: str) -> str:
    result = asr_model.generate(input=audio_path)
    return result[0]["text"]
```

### 🥈 备选：SenseVoice-Small

如果 Paraformer 效果不够好，试试 SenseVoice：
- 更新的模型（2024年发布）
- 额外支持情绪和音频事件检测
- 同样通过 FunASR 框架使用

### 🥉 兜底：Whisper small + LLM纠错

如果不想换模型，最小改动方案：
- 保留现有 Whisper small
- 输出后用 Claude API 做一轮纠错
- 成本低，效果中等

---

## 四、方案对比总表

| 方案 | 中文准确率 | 显存 | 成本 | 自动化 | 推荐度 |
|------|-----------|------|------|--------|--------|
| **FunASR Paraformer** | ⭐⭐⭐⭐⭐ | 1-2GB | 免费 | ✅ | 🏆 首选 |
| **SenseVoice** | ⭐⭐⭐⭐⭐ | ~1GB | 免费 | ✅ | 🥈 备选 |
| **Whisper+LLM纠错** | ⭐⭐⭐⭐ | 2GB+API | 低 | ✅ | 🥉 兜底 |
| **讯飞API** | ⭐⭐⭐⭐⭐ | 0 | 中 | ✅ | 适合大量 |
| **Whisper large-v3** | ⭐⭐⭐⭐ | 10GB | 免费 | ⚠️OOM | ❌ |
| **剪映** | ⭐⭐⭐⭐⭐ | - | 免费 | ❌ | ❌ |

---

## 五、下一步行动

1. `pip install funasr` 安装FunASR
2. 用同一段音频对比 Whisper small vs Paraformer vs SenseVoice 的输出
3. 选择效果最好的替换现有流程
4. 如需进一步提升：加热词列表（FunASR支持热词增强）
