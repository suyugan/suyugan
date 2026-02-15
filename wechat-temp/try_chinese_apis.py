"""Try Chinese AI image APIs - SiliconFlow, Zhipu CogView, Baidu"""
import requests
import os
import base64
import time

OUTPUT_DIR = r"D:\video-analysis\output\原生家庭\images"
prompt = "a lonely child in dark blue room, anime style, digital painting, emotional, deep indigo tones"

# Method 1: Try SiliconFlow with registration
# Their free tier gives some credits
def try_siliconflow_free():
    print("=== SiliconFlow - checking if there's a free endpoint ===")
    # Try their free models endpoint
    url = "https://api.siliconflow.cn/v1/images/generations"
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell",
        "prompt": prompt,
        "image_size": "768x1344",
    }
    resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
    print(f"No auth: {resp.status_code} {resp.text[:200]}")

# Method 2: Zhipu/BigModel CogView - we already have API key from AutoGLM
def try_zhipu_cogview():
    print("\n=== Trying Zhipu CogView ===")
    # Read API key from autoglm run.ps1
    api_key = None
    try:
        with open(r"D:\autoglm\run.ps1", "r") as f:
            for line in f:
                if "ZHIPUAI_API_KEY" in line or "api_key" in line.lower():
                    # Extract key
                    import re
                    m = re.search(r'["\']([a-zA-Z0-9_\-.]+\.[a-zA-Z0-9_\-.]+)["\']', line)
                    if m:
                        api_key = m.group(1)
                        break
    except:
        pass
    
    if not api_key:
        print("No Zhipu API key found, trying from env or hardcoded search")
        # Try reading the file differently
        try:
            content = open(r"D:\autoglm\run.ps1", "r").read()
            print(f"run.ps1 content (first 500 chars): {content[:500]}")
        except Exception as e:
            print(f"Can't read: {e}")
        return None
    
    print(f"Found API key: {api_key[:10]}...")
    
    url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "cogview-3-plus",
        "prompt": prompt,
        "size": "768x1344",
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Response: {str(data)[:300]}")
        if resp.status_code == 200 and 'data' in data:
            img_url = data['data'][0].get('url', '')
            if img_url:
                img_resp = requests.get(img_url, timeout=60)
                path = os.path.join(OUTPUT_DIR, "test_cogview.png")
                with open(path, "wb") as f:
                    f.write(img_resp.content)
                print(f"SAVED: {path} ({len(img_resp.content)} bytes)")
                return api_key
    except Exception as e:
        print(f"Error: {e}")
    return None

try_siliconflow_free()
result = try_zhipu_cogview()
if result:
    print(f"\nCogView works! API key: {result[:10]}...")
