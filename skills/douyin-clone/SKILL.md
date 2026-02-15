---
name: douyin-clone
description: 复刻抖音博主完整流程。从分析目标博主视频风格、选题规律、数据表现，到生成原创文案、AI配图、TTS配音、BGM合成、最终视频输出。当用户说"复刻博主"、"模仿抖音号"、"分析抖音博主"、"做一个类似XX的视频"时触发。
---

# 复刻抖音博主

完整流程分6个阶段，按顺序执行。每个阶段完成后向用户汇报进度。

## 阶段一：抓取与下载

1. 获取目标博主主页链接或 sec_uid
2. 调用抖音API批量获取视频列表：
   ```
   GET http://localhost:18810/api/hybrid/video_data?url={视频链接}
   ```
3. 遍历所有视频，下载到 `D:\video-analysis\{博主名}\` 目录
4. 每个视频独立文件夹：`{视频ID}\video.mp4`

## 阶段二：转录与分析

1. **抽帧**：ffmpeg 提取关键帧（短视频 fps=1/5，长视频 fps=1/10）
2. **音频提取**：`ffmpeg -i video.mp4 -vn -ar 16000 -ac 1 audio.wav`
3. **语音转录**：Whisper 转录音频为文字
4. **数据统计**：汇总点赞、评论、收藏、分享数据
5. **生成分析报告**，内容包括：
   - 博主整体风格特征（人设、形式、定位）
   - 数据概览（总计+平均）
   - 高频标签 Top 20
   - 核心选题方向（5-6个方向）
   - 文案风格（高频词、标题模式、开头模式、语气特点）
   - Top10视频共性分析
   - 时长分布、发布频率、最佳发布时间
   - 复刻建议（选题、文案模板、视觉风格、发布策略）

详细报告模板见 `references/report-template.md`

## 阶段三：写文案

1. 根据分析报告确定选题方向
2. 按目标博主的文案结构写原创文案：
   - **开头**（前3秒）：痛点共鸣/反直觉疑问，抓注意力
   - **正文**：痛点 → 原因分析 → 深层解读 → 解决方案
   - **结尾**：金句收尾 + 引导互动
3. 文案长度参考博主平均时长（口播约 250字/分钟）
4. 拆分为 8-12 个场景，每个场景标注画面描述
5. 保存到 `D:\video-analysis\output\{主题}\script.md`

## 阶段四：生成素材

### 4.1 AI配图

使用即梦AI API生成场景插图：

```python
# 火山引擎即梦API
# AK/SK 从 TOOLS.md 或环境变量获取
# 接口：CVSync2AsyncSubmitTask / CVSync2AsyncGetResult
# req_key: jimeng_t2i_v40
```

**图片要求**：
- 尺寸：9:16竖版（1080x1920）
- 风格：根据分析报告中的视觉风格适配
- 每个场景生成1张，共8-12张
- 保存到 `D:\video-analysis\output\{主题}\images\scene_XX.png`

API调用详见 `references/jimeng-api.md`

### 4.2 TTS配音

```powershell
# 使用 edge-tts
edge-tts --voice zh-CN-XiaoyiNeural --text "文案内容" --write-media narration.mp3
```

**声音选择**：
- 温柔女声：`zh-CN-XiaoyiNeural`
- 成熟男声：`zh-CN-YunxiNeural`
- 根据博主风格选择匹配的声音

### 4.3 BGM

- 优先使用目标博主的原版BGM（从视频元数据提取music_url）
- 备选：YouTube搜索同类型BGM，用 yt-dlp 下载
- 保存到 `D:\video-analysis\output\{主题}\bgm.mp3`

## 阶段五：合成视频

用 ffmpeg 将图片序列 + 旁白 + BGM 合成为最终视频：

```powershell
# 1. 生成图片列表文件 images.txt
# 格式：file 'scene_01.png' \n duration 31
# 每张图时长 = 总旁白时长 / 场景数

# 2. 合成
ffmpeg -f concat -safe 0 -i images.txt ^
  -i narration.mp3 ^
  -i bgm.mp3 ^
  -filter_complex "[2:a]volume=0.11,aloop=loop=-1:size=2e+09[bgm];[1:a][bgm]amix=inputs=2:duration=first[aout]" ^
  -map 0:v -map "[aout]" ^
  -c:v libx264 -pix_fmt yuv420p -r 30 ^
  -c:a aac -b:a 128k ^
  -s 1080x1920 -shortest ^
  final.mp4
```

**注意**：
- BGM音量压低（0.10-0.12），不盖过旁白
- BGM循环播放（aloop）
- 输出1080x1920竖屏，30fps
- 可多版本迭代（final_v1无BGM，final_v2有BGM等）

## 阶段六：发布

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
