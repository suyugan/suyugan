---
name: douyin-clone
description: 复刻抖音博主完整流程。从分析目标博主视频风格、选题规律、数据表现，到生成原创文案、AI配图、TTS配音、BGM合成、最终视频输出。当用户说"复刻博主"、"模仿抖音号"、"分析抖音博主"、"做一个类似XX的视频"时触发。
---

# 复刻抖音博主

完整流程分6个阶段，按顺序执行。每个阶段完成后向用户汇报进度。

## 阶段一：抓取数据

**本地脚本（不需要下载视频）：**
```powershell
# 1. 抓取视频列表元数据
python scripts/fetch_videos.py "博主主页链接或sec_uid" -o D:\video-analysis\{博主名}

# 2. 数据统计（纯数据，不含AI分析）
python scripts/analyze_data.py -i D:\video-analysis\{博主名}\videos.json -o D:\video-analysis\{博主名}\data_report.md
```

- `scripts/fetch_videos.py` — 批量获取博主所有视频元数据（标题/点赞/评论/收藏/分享/时长/标签/BGM），保存 videos.json
- `scripts/analyze_data.py` — 纯数据统计（点赞/标签/标题模式/时长/频率），输出 data_report.md

**说明**：分析阶段只需要元数据，不需要下载视频。仅在后续需要深度文案风格分析时，才选择性下载+转录少量代表性视频。

## 阶段二：AI分析出报告

**需要token的部分：** 读取 data_report.md（+ 可选的转录文本），由AI生成完整分析报告，包括：
- 博主风格特征、人设定位
- 选题规律与爆款共性
- 文案风格与语气特点
- 复刻建议（选题/文案模板/视觉风格/发布策略）

报告模板见 `references/report-template.md`

**可选：深度文案分析**（需要下载+转录）
```powershell
# 下载Top10视频做文案分析
python scripts/download_videos.py -i D:\video-analysis\{博主名}\videos.json -o D:\video-analysis\{博主名} --top 10
python scripts/transcribe.py -d D:\video-analysis\{博主名} -m medium
```

## 阶段三：写文案

1. 根据分析报告确定选题方向
2. 按目标博主的文案结构写原创文案：
   - **开头**（前3秒）：痛点共鸣/反直觉疑问，抓注意力
   - **正文**：痛点 → 原因分析 → 深层解读 → 解决方案
   - **结尾**：金句收尾 + 引导互动
3. 文案长度参考博主平均时长（口播约 250字/分钟）
4. 保存到 `D:\video-analysis\output\{主题}\script.md`

## 阶段四：拆分场景 + 生成提示词

文案写完后，AI自动完成：

1. **拆分片段**：按内容逻辑将文案拆成若干片段，每个片段对应一个画面场景（数量不固定，根据内容结构决定，通常6-15个）
2. **生成提示词**：为每个片段生成即梦图片提示词，画面要精准匹配该片段的文案内容
3. **输出 prompts.json**：

```json
{
  "scenes": [
    {
      "scene_num": 1,
      "text": "对应的文案片段内容...",
      "prompt": "帮我生成图片：...\n背景：...\n风格：...\n氛围：...\n构图：...。比例 9:16。"
    },
    ...
  ]
}
```

**要求**：
- 每个prompt必须与该片段文案内容强关联，不能泛泛而谈
- 画面风格保持统一（同一套视觉语言）
- 保存到 `D:\video-analysis\output\{主题}\prompts.json`

## 阶段五：生成素材

### 5.1 AI配图

**本地脚本：**
```powershell
# 6. 即梦API批量生图
python scripts/generate_images.py prompts.json -o D:\video-analysis\output\{主题}\images --ak xxx --sk xxx
```

- `scripts/generate_images.py` — 读取prompts.json，调用即梦API异步生图，1080x1920竖版

**提示词格式**（AI写prompt时必须按此结构）：
```
帮我生成图片：{主体描述，人物外貌/动作/表情/服装}
背景：{场景环境、色调、光线}
风格：{画风，如日式漫画/扁平插画/黑白线稿+平涂等}
氛围：{情绪关键词，3-5个}
构图：{景别、视角、镜头效果}。比例 9:16。
```

示例：
```
帮我生成图片：一位疲惫的中年东亚男性，胡茬，灰色睡衣，独自坐在深夜客厅沙发角落，低头抽烟，烟雾缭绕，神情落寞
背景：老式电视机、电视柜，深蓝色调、冷光、低饱和
风格：日式漫画、黑白线稿+平涂、干净利落线条、极简插画、复古质感
氛围：孤独、压抑、深夜寂静、中年男人的隐忍、故事感
构图：近景、侧视角、暗角、景深、电影感。比例 9:16。
```

### 5.2 TTS配音

**本地脚本：**
```powershell
# 5. TTS配音
python scripts/generate_tts.py D:\video-analysis\output\{主题}\script.md -o D:\video-analysis\output\{主题}\narration.mp3
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
# 7. 合成最终视频
python scripts/compose_video.py -i images -n narration.mp3 -b bgm.mp3 -o final.mp4
# 无BGM版本: --no-bgm
# 调整BGM音量: --bgm-volume 0.15
```

- `scripts/compose_video.py` — 图片序列+旁白+BGM合成，1080x1920/30fps/h264+aac

### 章节进度条

如果文案有明确的结构分段（如：引子→第一部分→第二部分→结语），在视频顶部叠加章节导航条：

- 根据 prompts.json 中的场景拆分，自动生成章节标题
- 用 ffmpeg drawtext 在视频顶部绘制章节条（半透明背景 + 白色文字）
- 当前章节高亮显示，其余章节灰色
- 每个章节对应的时间段 = 该片段的起止时间

**实现方式**：
```
# 每个章节时间段内叠加对应的章节条
ffmpeg -i video.mp4 \
  -vf "drawbox=x=0:y=0:w=iw:h=60:color=black@0.5:t=fill, \
       drawtext=text='引子 | 第一部分 | 第二部分 | 结语':x=20:y=20:fontsize=24:fontcolor=white" \
  -c:a copy output.mp4
```

**注意**：章节条样式参考抖音原生效果——横向排列、当前段高亮、可滚动。如果段数多则缩略显示。

## 阶段七：发布

通过浏览器自动化发布到抖音：
1. 打开 `https://creator.douyin.com`
2. 上传视频文件
3. 填写标题、标签、描述
4. 选择封面
5. 发布

## 输出文件结构

```
D:\video-analysis\
├── {博主名}\                    # 原始视频数据
│   ├── {视频ID}\
│   │   ├── video.mp4
│   │   ├── frames\
│   │   ├── audio.wav
│   │   └── audio.txt
│   └── ...
├── final_report.md              # 分析报告
└── output\
    └── {主题}\                  # 制作输出
        ├── script.md            # 文案脚本
        ├── images\              # 场景图
        │   ├── scene_01.png
        │   └── ...
        ├── narration.mp3        # TTS配音
        ├── bgm.mp3              # 背景音乐
        └── final.mp4            # 最终视频
```
