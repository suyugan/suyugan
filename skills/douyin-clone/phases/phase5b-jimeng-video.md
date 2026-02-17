<!-- 本文件是 douyin-clone 技能的子文件，完整流程见 ../SKILL.md -->
<!-- phase5b: 即梦视频生成（content_type=视频模式时使用） -->

## 5.1b AI视频生成（即梦视频模式）

**当 style_template.json 中 content_type 为「视频模式」时使用。**

### 双模式自动选择

每个场景在阶段四已标注 `video_mode`：

| 模式 | 适用场景 | 流程 |
|------|---------|------|
| **t2v**（文生视频） | 大场景/风景/抽象概念/动物 | 直接用prompt生成5秒视频 |
| **i2v**（图生视频） | 需精确人物/构图/一致性 | 先生图→图作首帧→生视频 |

### 脚本
`D:\video-analysis\scripts\jimeng_video_gen.py`

### 调用流程

```
步骤1：获取即梦tab（同生图）

步骤2：加载MD5签名
  python jimeng_video_gen.py --action md5 --json → browser evaluate

步骤3：逐个场景生成（循环）
  3a. chcp 65001 >nul & python jimeng_video_gen.py --action generate --prompt "描述" --ratio "16:9" --duration 5 --resolution 720p --json
  3b. browser evaluate → 记录 history_id（数字！）
  3c. 等5秒
  3d. python jimeng_video_gen.py --action poll-full --history-id "<id>" --json
  3e. 间隔30秒轮询（视频比图片慢！），超时300秒
  3f. curl -o videos/scene_XX.mp4 "<video_url>"
```

### i2v模式执行
```
1. video_mode == "i2v" → 先用即梦生图（phase5a流程）生成静态图
2. 用图片URL作首帧 → 调用图生视频接口
3. video_mode == "t2v" → 直接文字生视频
```

### ffmpeg拼接
```bash
# concat清单
echo "file 'videos/scene_01.mp4'" > concat_list.txt
# ...
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy video_only.mp4
```

### 与图片生成的区别
- 轮询接口：视频用 `get_history_queue_info`（图片用 `get_history_by_ids`）
- 轮询用 `history_id`（数字），不是 `submit_id`
- 轮询间隔30秒（图片5秒）
- 模型默认 fast（vgfm_3.0_fast），可选 standard
- 分辨率默认720p，可选1080p
