import urllib.request
import json
import ssl

ctx = ssl.create_default_context()
token = "t-g10428jJXJ3WZHWVOFBK25CEB3AYJQ3D4256D5XE"

def api_get(url):
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read().decode('utf-8'))

def api_post(url, body):
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })
    with urllib.request.urlopen(req, context=ctx) as resp:
        return json.loads(resp.read().decode('utf-8'))

results = []

# 1. Try shared spaces
try:
    r = api_get("https://open.feishu.cn/open-apis/drive/v1/files?page_size=200")
    results.append(f"Drive files: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"Drive files error: {e}")

# 2. Try to list all docs
try:
    r = api_get("https://open.feishu.cn/open-apis/docx/v1/documents?page_size=50")
    results.append(f"\nDocs: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nDocs error: {e}")

# 3. Try sheets
try:
    r = api_get("https://open.feishu.cn/open-apis/sheets/v3/spreadsheets?page_size=50")
    results.append(f"\nSheets: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nSheets error: {e}")

# 4. Try search
try:
    r = api_post("https://open.feishu.cn/open-apis/suite/docs-api/search/object", {
        "search_key": "",
        "count": 50,
        "offset": 0,
        "owner_ids": [],
        "chat_ids": [],
        "docs_types": []
    })
    results.append(f"\nSearch: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nSearch error: {e}")

# 5. Try recent docs  
try:
    r = api_get("https://open.feishu.cn/open-apis/drive/v1/files?page_size=50&order_by=EditedTime&direction=DESC")
    results.append(f"\nRecent files: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nRecent files error: {e}")

# 6. Try chat list (to find group docs)
try:
    r = api_get("https://open.feishu.cn/open-apis/im/v1/chats?page_size=50")
    results.append(f"\nChats: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nChats error: {e}")

# 7. Try to get user info
try:
    r = api_get("https://open.feishu.cn/open-apis/contact/v3/users?page_size=50")
    results.append(f"\nUsers: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nUsers error: {e}")

# 8. Try departments
try:
    r = api_get("https://open.feishu.cn/open-apis/contact/v3/departments?page_size=50")
    results.append(f"\nDepartments: {json.dumps(r, ensure_ascii=False, indent=2)}")
except Exception as e:
    results.append(f"\nDepartments error: {e}")

with open(r"C:\Users\Administrator\.openclaw\workspace\feishu_full_scan.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print("Done - feishu_full_scan.txt")
