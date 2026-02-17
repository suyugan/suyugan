<!-- 本文件是 douyin-clone 技能的子文件，完整流程见 ../SKILL.md -->

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
