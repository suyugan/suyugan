# 即梦AI API 调用指南

## 认证

火山引擎 AK/SK 认证，从 TOOLS.md 获取。

## 生成图片（异步接口）

### 提交任务

```python
import json, hashlib, hmac, datetime, urllib.request

def sign_request(ak, sk, service, region, action, body):
    """火山引擎V4签名"""
    # 使用 volcengine-python-sdk 更简单
    from volcengine.visual.VisualService import VisualService
    visual_service = VisualService()
    visual_service.set_ak(ak)
    visual_service.set_sk(sk)
    return visual_service

# 推荐用SDK
from volcengine.visual.VisualService import VisualService

visual_service = VisualService()
visual_service.set_ak("YOUR_AK")
visual_service.set_sk("YOUR_SK")

# 提交生图任务
form = {
    "req_key": "jimeng_t2i_v40",
    "prompt": "深蓝色调，扁平插画风格，一个女孩蜷缩在角落",
    "width": 1080,
    "height": 1920,
    "seed": -1,
    "return_url": True
}

resp = visual_service.cv_sync2_async_submit_task(form)
task_id = resp["data"]["task_id"]
```

### 查询结果

```python
import time

while True:
    result = visual_service.cv_sync2_async_get_result({"req_key": "jimeng_t2i_v40", "task_id": task_id})
    status = result["data"]["status"]
    if status == "done":
        image_urls = result["data"]["image_urls"]
        break
    elif status == "failed":
        raise Exception("生图失败")
    time.sleep(3)
```

### 下载图片

```python
import urllib.request

for i, url in enumerate(image_urls):
    req = urllib.request.Request(url)
    req.add_header("Referer", "https://jimeng.jianying.com/")
    with urllib.request.urlopen(req) as resp:
        with open(f"scene_{i+1:02d}.png", "wb") as f:
            f.write(resp.read())
```

## 提示词模板

根据目标博主风格调整，示例（心理叨叨兽风格）：

```
深蓝色调，扁平插画风格，极简线条，有限色彩，
{场景描述}，
情感叙事，治愈系，9:16竖版构图
```

## 注意事项

- req_key 用 `jimeng_t2i_v40`（图片生成4.0）
- 异步接口：先submit获取task_id，再轮询get_result
- 图片URL有签名有效期，及时下载
- 积分消耗：每次生成消耗若干积分
