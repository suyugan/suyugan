# 即梦API问题排查报告 (2026-02-16)

## 问题根因

子代理生成的 `generate_images.py` 存在**4个致命错误**：

### 错误1：req_key 错误
- ❌ 错误：`jimeng_high_aes_general_v21_L`
- ✅ 正确：`jimeng_t2i_v40`

### 错误2：task_id 读取位置错误
- ❌ 错误：`resp.get('task_id')` （顶层）
- ✅ 正确：`resp.get('data', {}).get('task_id')` （在data里）

### 错误3：status 读取位置错误
- ❌ 错误：`result.get('status')` （顶层，永远为空，导致无限轮询）
- ✅ 正确：`r.get('data', {}).get('status')` （在data里）

### 错误4：image_urls 读取位置错误
- ❌ 错误：`result.get('image_urls')` （顶层）
- ✅ 正确：`r['data'].get('image_urls', [])` （在data里）

### 错误5：多余的API参数
- ❌ 不需要：`negative_prompt`, `seed`, `scale`, `ddim_steps`, `use_sr`
- ✅ 需要：`logo_info: {'add_logo': False}`

### 错误6：环境变量名错误
- ❌ 错误：`VOLC_ACCESSKEY` / `VOLC_SECRETKEY`
- ✅ 正确：`VOLC_AK` / `VOLC_SK`

## 即梦API响应结构（正确版）

```python
# 提交响应
{
    "code": 10000,
    "data": {
        "task_id": "xxx"   # ← 在data里
    }
}

# 轮询响应
{
    "code": 10000,
    "data": {
        "status": "done",           # ← 在data里
        "image_urls": ["https://..."],  # ← 在data里
        "binary_data_base64": [...]
    }
}
```

## 修复方案

1. **标准化脚本**：`D:\video-analysis\scripts\jimeng_gen.py`
   - 正确的API参数和响应解析
   - 并发限制(50430)自动重试，指数退避
   - 命令行参数支持
   - 进度显示 + flush输出

2. **以后子代理任务必须**：
   - 直接调用 `python D:\video-analysis\scripts\jimeng_gen.py prompts.json -o images/`
   - **不要自己写即梦API调用代码！** 用标准脚本
   - 环境变量用 `VOLC_AK` 和 `VOLC_SK`

## 正确的最小调用代码

```python
from volcengine.visual.VisualService import VisualService
import os, time

vs = VisualService()
vs.set_ak(os.environ['VOLC_AK'])
vs.set_sk(os.environ['VOLC_SK'])

# 提交
resp = vs.cv_sync2async_submit_task({
    'req_key': 'jimeng_t2i_v40',
    'prompt': '...',
    'width': 1080, 'height': 1920,
    'return_url': True,
    'logo_info': {'add_logo': False},
})
task_id = resp['data']['task_id']  # ← data里！

# 轮询
while True:
    time.sleep(3)
    r = vs.cv_sync2async_get_result({'req_key': 'jimeng_t2i_v40', 'task_id': task_id})
    status = r['data']['status']  # ← data里！
    if status == 'done':
        urls = r['data']['image_urls']  # ← data里！
        break
    elif status == 'failed':
        break
```
