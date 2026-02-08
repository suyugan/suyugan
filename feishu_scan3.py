import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
token = "t-g10428jJXJ3WZHWVOFBK25CEB3AYJQ3D4256D5XE"

def api_get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, context=ctx) as resp:
        raw = resp.read()
        return json.loads(raw), raw

# Get raw bytes of app info
data, raw = api_get("https://open.feishu.cn/open-apis/bitable/v1/apps/KDetb7DZSaTeVlsruKacD3Qgnch")
name = data['data']['app']['name']

# Write raw name bytes for inspection  
with open(r"C:\Users\Administrator\.openclaw\workspace\feishu_name.txt", "w", encoding="utf-8") as f:
    f.write(f"Name repr: {repr(name)}\n")
    f.write(f"Name: {name}\n")
    f.write(f"Name bytes (utf-8): {name.encode('utf-8').hex()}\n")
    
# Also get fields with repr
data2, _ = api_get("https://open.feishu.cn/open-apis/bitable/v1/apps/KDetb7DZSaTeVlsruKacD3Qgnch/tables/tbllfpktYGgTA38C/fields")
for field in data2['data']['items']:
    f_name = field['field_name']
    with open(r"C:\Users\Administrator\.openclaw\workspace\feishu_name.txt", "a", encoding="utf-8") as f:
        f.write(f"Field: {repr(f_name)}\n")

# Get table 1 records with repr
data3, _ = api_get("https://open.feishu.cn/open-apis/bitable/v1/apps/KDetb7DZSaTeVlsruKacD3Qgnch/tables/tbllfpktYGgTA38C/records?page_size=20")
with open(r"C:\Users\Administrator\.openclaw\workspace\feishu_name.txt", "a", encoding="utf-8") as f:
    f.write(f"\nTable 1 records:\n")
    f.write(json.dumps(data3, ensure_ascii=False, indent=2))

print("Done")
