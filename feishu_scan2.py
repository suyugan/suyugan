import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
token = "t-g10428jJXJ3WZHWVOFBK25CEB3AYJQ3D4256D5XE"

def api_get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read().decode('utf-8'))

output = []

# Get app name
r1 = api_get("https://open.feishu.cn/open-apis/bitable/v1/apps/KDetb7DZSaTeVlsruKacD3Qgnch")
app_name = r1['data']['app']['name']
output.append(f"App Name: {app_name}")

# Get table 1 fields
r2 = api_get("https://open.feishu.cn/open-apis/bitable/v1/apps/KDetb7DZSaTeVlsruKacD3Qgnch/tables/tbllfpktYGgTA38C/fields")
output.append("\nTable 1 Fields:")
for f in r2['data']['items']:
    output.append(f"  {f['field_name']} ({f['ui_type']})")

# Get file list
r3 = api_get("https://open.feishu.cn/open-apis/drive/v1/files?page_size=50")
output.append("\nFiles:")
for f in r3['data']['files']:
    output.append(f"  [{f['type']}] {f['name']}")

# Write to file with UTF-8
with open(r"C:\Users\Administrator\.openclaw\workspace\feishu_result.txt", "w", encoding="utf-8") as fout:
    fout.write("\n".join(output))

print("Done - written to feishu_result.txt")
