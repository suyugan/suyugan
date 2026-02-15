import json
from volcengine.visual.VisualService import VisualService

AK = "REDACTED_VOLC_AK"
SK = "REDACTED_VOLC_SK"

vs = VisualService()
vs.set_ak(AK)
vs.set_sk(SK)

# Try different req_keys for jimeng
req_keys = [
    "jimeng_high_aes_general_v21",
    "high_aes_general_v21", 
    "jimeng_high_aes_general_v20l",
    "high_aes",
    "jimeng_4.0_text2img",
    "t2i_jimeng_4_0",
]

for rk in req_keys:
    body = {
        "req_key": rk,
        "prompt": "a cat",
        "width": 512,
        "height": 512,
        "return_url": True,
    }
    try:
        resp = vs.cv_process(body)
        if isinstance(resp, bytes):
            resp = json.loads(resp)
        print(f"{rk}: {json.dumps(resp, ensure_ascii=False)[:300]}")
    except Exception as e:
        err = str(e)[:200]
        print(f"{rk}: {err}")
