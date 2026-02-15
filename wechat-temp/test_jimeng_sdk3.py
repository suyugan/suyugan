import json
from volcengine.visual.VisualService import VisualService

# Try old AK with the SK (it was used 7 days ago for "智能视觉")
AK = "REDACTED_VOLC_AK2"
SK = "ZmU3NzE3OGJmMDkwNDgxNWI4MWU5MjBhNTU5MzU0YjY"

vs = VisualService()
vs.set_ak(AK)
vs.set_sk(SK)

# Debug: let's check what the SDK is doing
print("AK:", AK)
print("SK:", SK)
print("SK len:", len(SK))

# Try a simpler API first - just list/check service
body = {
    "req_key": "jimeng_high_aes_general_v21",
    "prompt": "a cat",
    "width": 512,  
    "height": 512,
    "return_url": True,
}

import traceback
try:
    resp = vs.cv_process(body)
    if isinstance(resp, bytes):
        resp = json.loads(resp)
    print(json.dumps(resp, indent=2, ensure_ascii=False)[:1000])
except Exception as e:
    traceback.print_exc()
    # Try alternate: maybe the SK needs the SKLT prefix or something
    # Check if there's a different way to use the visual service
    print("\n--- Trying with alternate SK format ---")
    
    # The old key's SK - maybe it was never the one the user sent
    # Let's try: maybe the SK the user gave is for the NEW key (AKLTY)
    vs2 = VisualService()
    vs2.set_ak("REDACTED_VOLC_AK")
    vs2.set_sk("ZmU3NzE3OGJmMDkwNDgxNWI4MWU5MjBhNTU5MzU0YjY")
    try:
        resp2 = vs2.cv_process(body)
        print(str(resp2)[:500])
    except Exception as e2:
        # Check the SK that was double-base64 - original was REDACTED_VOLC_SK
        # which decoded to ZmU3NzE3OGJmMDkwNDgxNWI4MWU5MjBhNTU5MzU0YjY
        # which decoded to fe77178bf0904815b81e920a559354b6
        # The original Wm1V... might BE the actual SK
        vs3 = VisualService()
        vs3.set_ak("REDACTED_VOLC_AK")
        vs3.set_sk("REDACTED_VOLC_SK")
        try:
            resp3 = vs3.cv_process(body)
            print("WITH ORIGINAL B64:", str(resp3)[:500])
        except Exception as e3:
            print(f"All failed: {str(e3)[:200]}")
