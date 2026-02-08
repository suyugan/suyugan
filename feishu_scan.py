import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
token = "t-g10428jJXJ3WZHWVOFBK25CEB3AYJQ3D4256D5XE"

def api_get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read().decode('utf-8'))

# Get app name
r1 = api_get("https://open.feishu.cn/open-apis/bitable/v1/apps/KDetb7DZSaTeVlsruKacD3Qgnch")
print("=== App Name ===")
print(r1['data']['app']['name'])

# Get table 1 fields
r2 = api_get("https://open.feishu.cn/open-apis/bitable/v1/apps/KDetb7DZSaTeVlsruKacD3Qgnch/tables/tbllfpktYGgTA38C/fields")
print("\n=== Table 1 (数据表) Fields ===")
for f in r2['data']['items']:
    print(f"  {f['field_name']} ({f['ui_type']})")

# Get file list with proper encoding
r3 = api_get("https://open.feishu.cn/open-apis/drive/v1/files?page_size=50")
print("\n=== Files in Root ===")
for f in r3['data']['files']:
    print(f"  [{f['type']}] {f['name']} (token: {f['token']})")
    print(f"    URL: {f['url']}")
    print(f"    Created: {f['created_time']}, Modified: {f['modified_time']}")
