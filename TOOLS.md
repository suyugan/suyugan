# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## 🖥️ 腾讯云服务器

### 轻量应用服务器
- **IP**: 106.55.158.137
- **用户名**: ubuntu
- **密码**: REDACTED_SERVER_PWD
- **系统**: Ubuntu 24.04 LTS
- **配置**: 2核4G / 60GB SSD / 500GB流量/月
- **到期**: 2027-02-07
- **用途**: 部署网站（bookmarks.html、群聊监控器等）

---

## 🎨 即梦AI生图（Fetch API）

通过browser evaluate在即梦网页版内调用内部API生图，无需官方API key。

- **Skill文档**: `skills/jimeng-fetch/SKILL.md`
- **JS生成脚本**: `D:\video-analysis\scripts\jimeng_fetch_gen.py`
- **批量脚本**: `D:\video-analysis\scripts\jimeng_batch_fetch.py`
- **前置条件**: openclaw浏览器中即梦网页版已登录
- **browser参数**: `profile="openclaw", target="host"`
- **比例**: 1:1, 3:4, 4:3, 9:16, 16:9
- **频率**: 生图间隔2-3秒，轮询间隔5秒，超时120秒

---

## 📹 视频分析配置

- **下载目录**: `D:\video-analysis\`
- **API地址**: `http://localhost:18810`
- **每个视频独立文件夹**: `D:\video-analysis\{视频ID}\`
  - video.mp4 (无水印视频)
  - frames\ (关键帧)
  - audio.wav / audio.txt (音频+转录)
  - video_data.json (元数据)

### ⚡ 执行方式
**收到视频链接后，必须spawn子代理处理！**

```
sessions_spawn({
  task: "分析抖音视频: {链接}\n\n完整流程:\n1. API获取元数据(http://localhost:18810)\n2. 下载到D:\\video-analysis\\{视频ID}\\\n3. ffmpeg抽帧(短视频fps=1/5,长视频fps=1/10)\n4. ffmpeg提取音频+Whisper转录\n5. 读取关键帧AI分析画面\n6. 输出完整报告(基本信息+画面内容+音频转录+总结)\n7. 输出小红书素材(封面建议+文案+发布建议)\n8. 生成小红书封面图:\n   - 写HTML到D:\\video-analysis\\{视频ID}\\cover.html\n   - 用browser打开截图\n   - 发送封面图到频道\n\n过程中发送状态更新到频道",
  label: "视频分析-{简短描述}"
})
```

**封面图HTML模板：**
```html
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body{width:1080px;height:1440px;margin:0;
background:url('frame_001.jpg') center/cover;
font-family:'Microsoft YaHei';color:white;position:relative}
.overlay{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,0.3),rgba(0,0,0,0.7))}
.content{position:relative;z-index:1;height:100%;display:flex;flex-direction:column;justify-content:flex-end;padding:80px 60px}
.title{font-size:88px;font-weight:900;text-shadow:4px 4px 12px rgba(0,0,0,0.9);margin-bottom:30px}
.sub{font-size:48px;color:#ffd700;text-shadow:2px 2px 8px rgba(0,0,0,0.9);margin-bottom:40px}
.tag{font-size:28px;background:rgba(255,255,255,0.2);padding:12px 24px;border-radius:30px}
</style></head>
<body><div class="overlay"></div>
<div class="content">
<div class="title">{主标题}</div>
<div class="sub">{副标题}</div>
<span class="tag">{标签}</span>
</div></body></html>
```

主会话回复：「收到，spawn出去分析了 🐾」然后可以继续聊别的

---

## 🤖 多机器人协作学习（五一服务器）

**频道**: discord:1469357020573339672 (五一的服务器 #ai)

**行为准则**:
- **潜水观察**，不主动说话
- 有不懂的 **@ 对应 bot 询问**
- **学别人的口吻和称呼**，融入进去
- **学会新技能主动汇报**给苏总
- **遇到需要苏总操作的事**，私信他 (Discord ID: 1468275763462541342)

**频道里的 bot**:
- 多多 — 技术强，能看图，干练
- 老林的AI助手 — 擅长排查，英文思考中文输出
- 五一 — 桔梗的猫猫人设
- 牛牛 — 也能帮忙

---

## 📱 手机控制 (moto g54)

### 连接信息
- **IP地址**: 192.168.41.203
- **当前端口**: 39075 (端口会变，如连接失败需更新)
- **设备ID**: ZY22HXZ953
- **最后更新**: 2026-02-07 20:22

---

## 🤖 AutoGLM 手机操控 (推荐)

使用智谱 AutoGLM 视觉语言模型自动操控手机。

### 部署位置
- **项目目录**: `D:\autoglm\Open-AutoGLM`
- **启动脚本**: `D:\autoglm\run.ps1`
- **API**: 智谱 BigModel (`https://open.bigmodel.cn/api/paas/v4`)
- **模型**: `autoglm-phone`

### 快速使用
```powershell
# 执行任务
D:\autoglm\run.ps1 "打开美团点外卖"
D:\autoglm\run.ps1 "打开微信给张三发消息你好"
D:\autoglm\run.ps1 "打开淘宝搜索手机壳"
```

### 注意事项
- 如果有多个 ADB 设备，需设置 `$env:ANDROID_SERIAL="192.168.41.203:34129"`
- 需要安装 ADB Keyboard 用于中文输入
- API Key 存储在 `D:\autoglm\run.ps1` 中
- **解锁屏幕**：锁屏状态下向上滑动即可解锁（无需密码/图案）

---

## 📸 微信群截图任务（看群）

### 快捷命令
- 「看群」→ 截图上传到截图版网页
- 「同步」→ 截图+OCR识别+推送到文字版网页 http://bm.weiixxin.com/wechat-text/

### 截图流程（重要！每次必须截完所有新消息！）
1. 打开微信，进入群聊「跟不上ai发展你睡得着吗?」
2. **先向上滑动**到上次截图的位置（找到已截过的消息边界）
3. 从边界位置开始，**向下滑动截图**（从旧消息到新消息）
4. 每滑动一屏截一张，**必须截到最底部（最新消息）为止**
5. **不能漏消息**——中间有多少屏就截多少屏（可能20-30张）
6. **按截图顺序上传**（先截的先传 = 旧消息先传）

### 显示规则
- 服务器排序：`ORDER BY created_at DESC, rowid DESC`
- 效果：**后上传的（最新消息）显示在最左/最上**
- 符合阅读习惯：左→右、上→下 = 新→旧

### 上传接口
```
POST http://bm.weiixxin.com/wechat/api/groups/5c021a42-1a6d-4666-b660-c754554bb8a6/images
Content-Type: multipart/form-data
Field: images (可多个)
```

### Python 上传示例
```python
import requests
files = [('images', (f'screenshot_{i}.png', open(path, 'rb'), 'image/png')) for i, path in enumerate(screenshot_paths)]
requests.post('http://bm.weiixxin.com/wechat/api/groups/5c021a42-1a6d-4666-b660-c754554bb8a6/images', files=files)
```

---

### 旧方案：手动 ADB 控制（备用）

### 快速命令
```bash
# 检查连接
python skills/phone-control/scripts/phone.py status

# 截图
python skills/phone-control/scripts/phone.py screen

# 打开App
python skills/phone-control/scripts/phone.py app meituan
python skills/phone-control/scripts/phone.py app wechat
python skills/phone-control/scripts/phone.py app taobao

# 点击
python skills/phone-control/scripts/phone.py tap 540 1200
```

### 重新连接流程
如果连接断开：
1. 用户打开手机 设置→开发者选项→无线调试
2. 获取新的IP:端口
3. 如果之前未配对，点「使用配对码配对设备」获取配对码
4. `adb pair <IP>:<配对端口> <配对码>`
5. `adb connect <IP>:<连接端口>`

### 屏幕信息
- 分辨率: 1080x2400
- 美团外卖入口约坐标: (80, 290)

---

## 📹 视频分析输出格式

分析视频时按以下格式输出：

### 状态更新（实时发送）
```
✅ 视频已下载（约XXX秒）
✅ 抽了XX帧关键帧
✅ Whisper 语音转录已完成
✅ 正在用 AI 逐帧分析画面（已完成 X/X 帧）

内容是XXX，讲XXX话题。快好了，再等一两分钟。
```

### 📝 视频分析报告

#### 📋 基本信息
- **标题**: 
- **作者**: 
- **数据**: ❤️ XX | 💬 XX | ⭐ XX | 🔄 XX
- **BGM**: 
- **时长**: 
- **标签**: #xxx #xxx

#### 🎬 画面内容
（详细描述场景、人物、动作、画面文字，按时间线或场景分段）

#### 🔊 音频内容（Whisper转录）
（转录文字 + 分段整理成要点/预言/观点）

#### 💡 总结
（核心观点提炼，3-5条关键信息）

---

### 📕 小红书搬运素材

#### 🖼️ 封面图建议
- **主标题**: （8字以内，大字醒目）
- **副标题**: （补充说明，制造好奇）
- **配图风格**: （推荐用视频中哪一帧/什么风格）
- **配色建议**: （根据内容推荐）

#### 📝 小红书文案

```
【标题】（带emoji，20字以内，制造好奇/痛点）

正文（口语化、分段、emoji丰富）

···

话题标签
#xxx #xxx #xxx
```

#### 🎯 发布建议
- **最佳发布时间**: 
- **目标人群**: 
- **互动引导**: （评论区置顶/引导话术）
