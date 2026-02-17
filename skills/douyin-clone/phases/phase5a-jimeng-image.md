<!-- 本文件是 douyin-clone 技能的子文件，完整流程见 ../SKILL.md -->
<!-- phase5a: 即梦AI配图（content_type=配图口播时使用） -->

## 5.1 AI配图（即梦无感方案 — 逆向签名算法）

**⚠️ 使用即梦网页版内部API（Fetch方式），不走官方API！**
**⚠️ 必须使用标准脚本，严禁自己写JS/API调用代码！脚本已内置sign签名算法（MD5逆向）。**

**前置条件：** openclaw浏览器中 jimeng.jianying.com 已登录。

**标准脚本：**
- 单张：`D:\video-analysis\scripts\jimeng_fetch_gen.py`
- 批量：`D:\video-analysis\scripts\jimeng_batch_fetch.py`
- 并发：`D:\video-analysis\scripts\jimeng_batch_concurrent.py`

---

### 方案A：并发模式（推荐，10张图3-4分钟）

```
步骤1：获取即梦tab
  browser({ action: "tabs", profile: "openclaw", target: "host" })
  → 找到 jimeng.jianying.com 的 targetId

步骤2：初始化MD5签名函数
  读取 jimeng_fetch_gen.py 中的 SIGN_JS_HELPER
  browser evaluate 执行，确保 window.__jimeng_md5 可用

步骤3：读取 prompts.json，获取所有场景的prompt

步骤4：构建并发提交JS
  在browser evaluate中执行大JS：
  a) 定义 __jimengGen(prompt, submitId)（调用generate API）
  b) 定义 __jimengPoll(submitIds)（批量查询）
  c) 连续提交所有generate请求（每个间隔2秒setTimeout错开）
  d) 收集submit_id到 window.__batchSubmitIds
  e) 自动轮询，每5秒批量查所有id状态
  f) 结果存 window.__batchResults = { sceneNum: {status, url} }
  g) 全部完成后 window.__batchDone = true

步骤5：每10秒检查 window.__batchDone

步骤6：下载图片 → images/scene_XX.webp
```

**并发数**：3-5个同时，间隔2秒。超时120秒/张，整批300秒。
**断点续传**：跳过已存在的 scene_XX.webp。

### 方案B：串行模式（备用）

```
对每个场景：
  1. python jimeng_fetch_gen.py --action generate --prompt "xxx" --ratio "16:9" --json
  2. browser evaluate 执行返回的js
  3. 等3秒
  4. python jimeng_fetch_gen.py --action poll --submit-id "xxx" --json
  5. 间隔5秒轮询到 status=done
  6. 下载第一张图 → images/scene_XX.webp
```

**Windows编码问题解决：**
```powershell
chcp 65001
python D:\video-analysis\scripts\jimeng_fetch_gen.py ...
```

### 比例参数映射

| 比例 | image_ratio | 宽x高 |
|------|------------|--------|
| 1:1  | 1 | 2048x2048 |
| 3:4  | 3 | 1536x2048 |
| 4:3  | 4 | 2048x1536 |
| 9:16 | 5 | 1440x2560 |
| 16:9 | 6 | 2560x1440 |

**⚠️ 抖音视频一律 16:9（image_ratio=6, 2560x1440）**

### 注意事项
- 频率：生图间隔2-3秒，轮询间隔5秒，超时120秒
- 模型：`high_aes_general_v41`
- 每次生成4张图，取第一张
- 详细文档：`skills/jimeng-fetch/SKILL.md`

### 图片预览（必须步骤）
每完成5张图随机挑2-3张发给用户：
```
message({ action: "send", message: "🎨 即梦生图进度 X/Y", media: "images/scene_XX.webp" })
```
