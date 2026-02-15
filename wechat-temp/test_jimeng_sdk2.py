import json
from volcengine.visual.VisualService import VisualService

visual_service = VisualService()
visual_service.set_ak("REDACTED_VOLC_AK")
visual_service.set_sk("fe77178bf0904815b81e920a559354b6")

body = {
    "req_key": "jimeng_high_aes_general_v21",
    "prompt": "A cute cat, flat illustration, minimalist style, deep blue tones",
    "width": 512,
    "height": 512,
    "seed": -1,
    "scale": 3.5,
    "ddim_steps": 16,
    "return_url": True,
}

try:
    resp = visual_service.cv_process(body)
    print("SUCCESS!")
    print(json.dumps(resp, indent=2, ensure_ascii=False)[:1500])
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
