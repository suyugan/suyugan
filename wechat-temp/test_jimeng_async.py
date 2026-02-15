import json
from volcengine.visual.VisualService import VisualService
import time

AK = "REDACTED_VOLC_AK"
SK = "REDACTED_VOLC_SK"

vs = VisualService()
vs.set_ak(AK)
vs.set_sk(SK)

# Submit task
body = {
    "req_key": "jimeng_t2i_v40",
    "prompt": "A cute cat sitting on windowsill, flat illustration, deep blue tones, minimalist",
    "width": 1080,
    "height": 1920,
    "force_single": True,
}

print("Submitting task...")
try:
    resp = vs.cv_sync2async_submit_task(body)
    if isinstance(resp, bytes):
        resp = json.loads(resp)
    print("Submit response:", json.dumps(resp, indent=2, ensure_ascii=False)[:500])
    
    task_id = resp.get("data", {}).get("task_id")
    if task_id:
        print(f"\nTask ID: {task_id}")
        # Poll for result
        for i in range(30):
            time.sleep(3)
            query_body = {
                "req_key": "jimeng_t2i_v40",
                "task_id": task_id,
                "req_json": json.dumps({"return_url": True}),
            }
            result = vs.cv_sync2async_get_result(query_body)
            if isinstance(result, bytes):
                result = json.loads(result)
            status = result.get("data", {}).get("status", "")
            print(f"Poll {i+1}: status={status}")
            if status == "done" or result.get("code") == 10000:
                print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
                break
            elif "fail" in str(status).lower():
                print("FAILED:", json.dumps(result, indent=2, ensure_ascii=False)[:500])
                break
except Exception as e:
    print(f"Error: {e}")
