import sys
import json

try:
    from pywxdump import WX_OFFS, get_wx_info
    print("pywxdump imported successfully")
    
    # Try to get wx info
    result = get_wx_info()
    print(f"Result type: {type(result)}")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
