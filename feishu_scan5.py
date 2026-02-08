import urllib.request
import json
import ssl
from datetime import datetime

ctx = ssl.create_default_context()
token = "t-g10428jJXJ3WZHWVOFBK25CEB3AYJQ3D4256D5XE"

def api_get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read().decode('utf-8'))

results = []

# Check sub-departments  
try:
    r = api_get("https://open.feishu.cn/open-apis/contact/v3/departments?parent_department_id=0&page_size=50")
    results.append(f"Root departments: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"Root dept error: {e}")

# Check sub-departments of 投放组
try:
    r = api_get("https://open.feishu.cn/open-apis/contact/v3/departments?parent_department_id=f787f2g5853fbc17&page_size=50")
    results.append(f"\n投放组 sub-departments: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\n投放组 sub-dept error: {e}")

# Check users in department
try:
    r = api_get("https://open.feishu.cn/open-apis/contact/v3/users?department_id=f787f2g5853fbc17&page_size=50")
    results.append(f"\n投放组 users: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\n投放组 users error: {e}")

# Get tenant info
try:
    r = api_get("https://open.feishu.cn/open-apis/tenant/v2/tenant/query")
    results.append(f"\nTenant info: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nTenant info error: {e}")

# Check approval instances
try:
    r = api_get("https://open.feishu.cn/open-apis/approval/v4/instances?page_size=10")
    results.append(f"\nApprovals: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nApprovals error: {e}")

# Bitable dashboard/views
try:
    r = api_get("https://open.feishu.cn/open-apis/bitable/v1/apps/KDetb7DZSaTeVlsruKacD3Qgnch/tables/tbllfpktYGgTA38C/views")
    results.append(f"\nTable1 views: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nTable1 views error: {e}")

try:
    r = api_get("https://open.feishu.cn/open-apis/bitable/v1/apps/KDetb7DZSaTeVlsruKacD3Qgnch/tables/tbllHb0NJsKRKxdB/views")
    results.append(f"\nTable2 views: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nTable2 views error: {e}")

with open(r"C:\Users\Administrator\.openclaw\workspace\feishu_scan5.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print("Done")
