# 即梦AI Fetch生图 Skill

通过browser evaluate在即梦网页版内执行fetch调用内部API生图。

## 前置条件

1. **即梦网页版已登录** — 在openclaw浏览器中打开 `https://jimeng.jianying.com` 并已登录
2. **获取即梦tab的targetId** — 通过 `browser tabs` 找到即梦的tab

```
browser({ action: "tabs", profile: "openclaw", target: "host" })
// 找到 url 包含 jimeng.jianying.com 的tab，记下 targetId
```

## 完整流程

### 第1步：提交生图任务

用 `browser({ action: "act", ... })` 执行evaluate：

```
browser({
  action: "act",
  profile: "openclaw",
  target: "host",
  targeid: "<即梦tab的targetId>",
  request: {
    kind: "evaluate",
    fn: "<生成JS代码>"
  }
})
```

**生成JS代码（完整模板）：**

```javascript
fetch("https://jimeng.jianying.com/mweb/v1/aigc_draft/generate?aid=513695&device_platform=web&region=cn&webId=7604484243590465030&da_version=3.3.9&os=windows&web_component_open_flag=1&web_version=7.5.0&aigc_features=app_lip_sync", {
  method: "POST",
  credentials: "include",
  headers: {"Content-Type":"application/json","sign-ver":"1","pf":"7","appvr":"8.4.0","loc":"cn","lan":"zh-Hans","app-sdk-version":"48.0.0","appid":"513695"},
  body: JSON.stringify({
    "extend": {"root_model": "high_aes_general_v41"},
    "submit_id": "<UUID>",
    "metrics_extra": "{\"sceneOptions\":{\"value\":\"text_to_image\",\"label\":\"文生图\"}}",
    "draft_content": "<draft_content_json_string>",
    "http_common_info": {"aid": 513695}
  })
}).then(r => r.json()).then(d => JSON.stringify({ret: d.ret, errmsg: d.errmsg, submit_id: "<UUID>"}))
```

**draft_content JSON字符串结构：**

```json
{
  "type": "image",
  "guide_param": {},
  "requirement_id": "<UUID>",
  "component_list": [{
    "type": "image_base_component",
    "id": "<UUID>",
    "generate_type": 0,
    "aigc_mode": "workbench",
    "image_ratio": 5,
    "generate_count": 4,
    "width": 1440,
    "height": 2560,
    "seed": 1234567890,
    "text_list": [{"text": "你的提示词", "id": "<UUID>", "weight": 100, "text_type": 0}],
    "style_id": "",
    "model": "high_aes_general_v41",
    "face_recognize": 0,
    "cref_list": [],
    "sref_list": [],
    "sub_component_list": [],
    "logo_info": {"add_logo": false, "position": 0, "language": 0, "opacity": 0.3, "logo_text_content": ""},
    "history_option": {"check_repeat": false, "check_repeat_type": ""},
    "refine_prompt_switch": true
  }]
}
```

### 第2步：轮询结果

间隔5秒轮询，超时120秒：

```javascript
fetch("https://jimeng.jianying.com/mweb/v1/get_history_by_ids?aid=513695&device_platform=web&region=cn&webId=7604484243590465030&da_version=3.3.9&web_version=7.5.0&aigc_features=app_lip_sync", {
  method: "POST",
  credentials: "include",
  headers: {"Content-Type":"application/json","sign-ver":"1","pf":"7","appvr":"8.4.0","loc":"cn","lan":"zh-Hans","app-sdk-version":"48.0.0","appid":"513695"},
  body: JSON.stringify({"submit_ids": ["<submit_id>"]})
}).then(r => r.json()).then(d => {
  const item = d.data && d.data["<submit_id>"];
  if (!item) return JSON.stringify({status: "pending", data: null});
  const list = item.item_list || [];
  if (list.length === 0) return JSON.stringify({status: "pending", data: null});
  const urls = list.map(img => {
    const m = img.cover_url_map || {};
    return m["4096"] || m["2048"] || m["1024"] || Object.values(m)[0] || "";
  });
  return JSON.stringify({status: "done", urls: urls, count: urls.length});
})
```

返回 `{"status":"done","urls":[...]}` 时表示完成。

### 第3步：下载图片

```python
# 用exec下载
import urllib.request
urllib.request.urlretrieve(url, "output.jpg")
```

或用curl：
```bash
curl -o output.jpg "图片URL"
```

## 比例参数映射

| 比例 | image_ratio | 宽x高 |
|------|------------|--------|
| 1:1  | 1 | 2048x2048 |
| 3:4  | 3 | 1536x2048 |
| 4:3  | 4 | 2048x1536 |
| 9:16 | 5 | 1440x2560 |
| 16:9 | 6 | 2560x1440 |

## Python辅助脚本

位于 `D:\video-analysis\scripts\jimeng_fetch_gen.py`，可自动生成JS代码：

```bash
# 生成提交JS
python D:\video-analysis\scripts\jimeng_fetch_gen.py --prompt "一只可爱的猫" --ratio 9:16 --action generate

# 生成轮询JS
python D:\video-analysis\scripts\jimeng_fetch_gen.py --submit-id "xxx-xxx" --action poll

# JSON格式输出（含submit_id）
python D:\video-analysis\scripts\jimeng_fetch_gen.py --prompt "xxx" --ratio 1:1 --action generate --json
```

批量生成：`D:\video-analysis\scripts\jimeng_batch_fetch.py`

```bash
python D:\video-analysis\scripts\jimeng_batch_fetch.py --input prompts.json --output jimeng_batch_output --ratio 9:16
```

## 子代理完整调用示例

```python
# 1. 获取即梦tab
tabs = browser(action="tabs", profile="openclaw", target="host")
jimeng_tab_id = "找到jimeng的targetId"

# 2. 用Python生成JS代码
result = exec("python D:\\video-analysis\\scripts\\jimeng_fetch_gen.py --prompt '一只猫' --ratio 9:16 --action generate --json")
data = json.loads(result)
js_code = data["js"]
submit_id = data["submit_id"]

# 3. 提交生图
browser(action="act", profile="openclaw", target="host", targeid=jimeng_tab_id,
        request={"kind": "evaluate", "fn": js_code})

# 4. 等待5秒后轮询
poll_js = exec(f"python D:\\video-analysis\\scripts\\jimeng_fetch_gen.py --submit-id {submit_id} --action poll")
# 循环执行poll_js直到status=done

# 5. 下载图片
exec(f'curl -o output.jpg "{image_url}"')
```

## 注意事项

- **频率控制**：每次生图间隔2-3秒
- **轮询间隔**：5秒一次，超时120秒
- **登录状态**：必须在即梦网页版已登录，cookies有效
- **所有UUID**：每次调用都随机生成新的UUID
- **模型**：默认 `high_aes_general_v41`（高质量通用模型）
- **每次生成4张图**：generate_count=4
- **图片分辨率**：优先取4096，依次降级到2048、1024
