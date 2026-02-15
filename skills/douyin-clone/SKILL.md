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
  "video_size": [1080, 1920]
}
```
后续同博主的视频直接调用此模板，AI只需填场景描述，不用每次从零写完整prompt。

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
3. **复用画风模板**：如果 `style_template.json` 存在，直接用缓存的画风/色调/氛围，AI只填场景描述部分
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
帮我生成图片：{主体描述，人物外貌/动作/表情/服装}
背景：{场景环境、色调、光线}
风格：{画风，如日式漫画/扁平插画/黑白线稿+平涂等}
氛围：{情绪关键词，3-5个}
构图：{景别、视角、镜头效果}。比例 {与博主视频一致}。
```

**要求**：
- 每个prompt必须与该片段文案内容强关联，不能泛泛而谈
- 画面风格保持统一（同一套视觉语言）
- **图片尺寸**：从视频元数据获取实际画面宽高，避免变形
- 保存到 `D:\video-analysis\output\{主题}\prompts.json`

## 阶段五：生成素材（TTS和生图并行）

⚡ **TTS配音和即梦生图可以同时执行，不需要串行等待。**

### 5.1 AI配图

**本地脚本：**
```powershell
python scripts/generate_images.py prompts.json -o images --ak xxx --sk xxx
```

- `scripts/generate_images.py` — 读取prompts.json，调用即梦API异步生图

即梦API参考：`references/jimeng-api.md`

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
