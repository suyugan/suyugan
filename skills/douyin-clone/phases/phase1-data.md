<!-- 本文件是 douyin-clone 技能的子文件，完整流程见 ../SKILL.md -->

## 阶段一：抓取数据

**⚠️ 作品数量控制：如果博主作品较多（>30个），只取点赞量最高的前30个分析，不需要全部抓取。**

### 动效检测（阶段1.5附属步骤）

类型识别完成后，对参考视频做**相邻帧对比分析**，判断画面是否有动效：

**抽帧策略**：用更高频率抽帧（fps=2，即每0.5秒一帧），取3组相邻帧：
- 开头（0-10秒）：2-3帧连续帧
- 中间（30-40秒）：2-3帧连续帧
- 结尾（最后10秒）：2-3帧连续帧

**对比方式**：用AI视觉能力同时读取每组的2-3帧，判断：
- 元素是否有位移、缩放、旋转
- 是否有淡入淡出/透明度变化
- 文字/图标是否逐个出现
- 场景切换是硬切还是有过渡动画

**动效分类**：
| 类型 | 特征 | 后续路线 |
|------|------|---------|
| 无动效 | 相邻帧几乎完全一致，只有字幕变化 | 即梦生图（phase5a） |
| PPT式动效 | 元素淡入/缩放/滑入，场景有过渡 | Remotion简单动画（phase5c） |
| 复杂动画 | 人物有连续运动/骨骼动画/形变 | Remotion复杂动画（phase5c） |

**写入 style_template.json**：
```json
{
  "motion_type": "ppt_animation",
  "motion_details": {
    "element_entrance": "淡入+缩放",
    "scene_transition": "淡入淡出",
    "subtitle_animation": "逐句切换",
    "detected_from": "3组相邻帧对比，共9帧"
  }
}
```

### 数据来源：主页链接 vs 视频链接

**优先用主页链接**。主页能一次获取博主全部视频列表+基本数据，比逐个分析视频高效得多。

#### 方案A：通过主页链接获取数据（推荐）

当用户给的是主页链接（短链接重定向到 `/user/xxx`），流程如下：

**步骤1：解析主页链接，获取sec_uid**
```
browser({ action: "navigate", profile: "openclaw", target: "host", targetUrl: "用户给的链接" })
# 等重定向完成，URL变成 https://www.douyin.com/user/{sec_uid}
# 从URL提取sec_uid
```

**步骤2：从主页snapshot提取视频ID列表**
```
browser({ action: "snapshot", profile: "openclaw", target: "host", targetId: "xxx", compact: true })
# 从snapshot中找到所有视频链接，提取aweme_id（格式：/video/数字ID）
# 如果页面只显示部分视频，需要滚动加载更多
```

**步骤3：从snapshot提取博主基本信息**
- 昵称、粉丝数、获赞数、关注数、简介、IP属地
- 直接从snapshot文本中提取，不需要RENDER_DATA

**步骤4：用本地API批量获取每个视频的详细数据**
```powershell
# 对每个视频ID调用API
$body = @{ url = "https://www.douyin.com/video/$vid" } | ConvertTo-Json
$resp = Invoke-RestMethod -Uri "http://localhost:18810/api/hybrid/video_data" -Method POST -ContentType "application/json" -Body $body
# 提取：desc, statistics(digg/comment/collect/share), duration, music, tags
```

**步骤5：保存为标准格式**
```
D:\video-analysis\{博主名}\
├── blogger_info.json   # 博主基本信息
├── videos.json         # 所有视频元数据（按点赞排序）
└── data_report.md      # 数据统计报告
```

#### 方案B：通过单个视频链接获取数据

如果用户给的是单个视频链接，用API直接获取：
```powershell
$body = @{ url = "视频链接" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:18810/api/hybrid/video_data" -Method POST -ContentType "application/json" -Body $body
```
然后从视频数据中提取博主sec_uid，再走方案A获取完整主页数据。

#### ⚠️ 主页链接识别规则
- 短链接（如 `v.douyin.com/xxx`）需要browser打开才能判断是主页还是视频
- 重定向到 `/user/xxx` → 主页链接，走方案A
- 重定向到 `/video/xxx` → 视频链接，走方案B
- **子代理收到主页链接不能报错说"需要视频链接"，必须走方案A处理**

**博主数据缓存**：videos.json只抓一次，后续同博主的新视频只做增量更新（对比已有视频ID，只抓新的）。

**说明**：分析阶段只需要元数据，不需要下载视频。仅在后续需要深度文案风格分析时，才选择性下载+转录少量代表性视频。

## 阶段1.5：账号类型自动识别

**在抓取数据之后、AI分析之前，自动判断博主的内容类型。**

**流程**：
1. 读取 `videos.json`，分析以下特征：
   - **时长分布**：口播类通常1-3分钟，混剪类3-10分钟，实拍类时长不定
   - **标签关键词**：提取高频标签，匹配类型特征词（如"vlog""实拍""剪辑""口播"等）
   - **封面风格**：用AI视觉能力抽样分析3-5张封面图（是否有真人、是否为插画/配图、是否为实景）
   - **视频宽高比**：竖屏9:16居多→口播/实拍概率高，横屏→混剪概率高

2. **自动分类为以下四种类型之一**：

| 类型 | 特征 | 后续流程 |
|------|------|---------|
| **配图口播** | 封面为插画/图片，无真人出镜，1-3分钟 | 标准流程（阶段二~七） |
| **混剪** | 多素材拼接，3-10分钟，封面为影视/纪录片截图 | 走混剪流程 |
| **真人出镜** | 封面有真人，vlog/口播类标签 | 自动转为配图口播模式（抄内容风格，不抄真人） |
| **实拍** | 封面为实景照片，生活/旅行/美食类标签 | 自动转为配图口播模式 |
| **视频模式** | 博主使用AI视频/动态画面，非静态配图 | 走阶段5.1b即梦视频生成流程 |
| **动画模式** | 博主使用火柴人/简笔画/线条动画/MG动画风格 | 走阶段5.1c Remotion动画生成流程 |

3. **真人出镜/实拍类自动转换**：
   - **不需要询问用户，直接自动转为配图口播模式**
   - 复刻的是内容风格（文案结构、选题方向、叙事节奏），不是真人形象
   - 配图风格：根据视频内容主题自动选择合适的AI插画风格（如历史题材用古风绘画、情感题材用治愈插画等）
   - 转换时告知用户一句：「该博主为真人出镜，已自动转为AI配图模式，复刻内容风格」

4. **写入 style_template.json**：
```json
{
  "content_type": "配图口播",
  "content_type_confidence": 0.85,
  "content_type_reason": "封面均为插画风格，无真人出镜，平均时长2分钟，高频标签含'心理''情感'",
  ...其他已有字段...
}
```

5. **后续阶段根据 content_type 自动走对应分支**：
   - `配图口播` → 标准阶段二~七
   - `混剪` → 混剪视频复刻流程
   - `真人出镜` → 提示用户确认后走配图口播流程
   - `实拍` → 提示用户选择配图或混剪
   - `视频模式` → 阶段5.1b即梦视频生成 + ffmpeg拼接
   - `动画模式` → 阶段5.1c Remotion动画生成流程

---
