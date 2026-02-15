"""Try multiple free image generation APIs"""
import requests
import os
import urllib.parse
import time
import json

OUTPUT_DIR = r"D:\video-analysis\output\原生家庭\images"
prompt = "a lonely child in dark blue room, anime style, digital painting, emotional, deep indigo tones"

# Method 1: Together AI (free tier)
def try_together():
    print("=== Trying Together AI ===")
    url = "https://api.together.xyz/v1/images/generations"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "black-forest-labs/FLUX.1-schnell-Free",
        "prompt": prompt,
        "width": 768,
        "height": 1344,
        "n": 1,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")

# Method 2: Stability AI (DreamStudio) 
def try_stability():
    print("\n=== Trying Stability AI ===")
    url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
    headers = {"Content-Type": "application/json"}
    payload = {
        "text_prompts": [{"text": prompt}],
        "cfg_scale": 7,
        "height": 1344,
        "width": 768,
        "samples": 1,
        "steps": 30,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")

# Method 3: Prodia (free, no key needed)
def try_prodia():
    print("\n=== Trying Prodia ===")
    url = "https://api.prodia.com/v1/sd/generate"
    payload = {
        "model": "dreamshaper_8.safetensors [9d40847d]",
        "prompt": prompt,
        "negative_prompt": "ugly, blurry, low quality",
        "steps": 25,
        "cfg_scale": 7,
        "width": 768,
        "height": 1344,
        "sampler": "Euler",
    }
    try:
        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")

# Method 4: Pollinations with different params
def try_pollinations():
    print("\n=== Trying Pollinations (different model) ===")
    for model in ["flux", "turbo", ""]:
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&nologo=true"
        if model:
            url += f"&model={model}"
        try:
            resp = requests.get(url, timeout=180, allow_redirects=True)
            print(f"Model={model or 'default'}: Status={resp.status_code}, Size={len(resp.content)}, CT={resp.headers.get('content-type','?')}")
            if resp.status_code == 200 and len(resp.content) > 10000:
                path = os.path.join(OUTPUT_DIR, f"test_poll_{model or 'default'}.png")
                with open(path, "wb") as f:
                    f.write(resp.content)
                print(f"  SAVED: {path}")
                return True
        except Exception as e:
            print(f"  Error: {e}")
    return False

# Method 5: getimg.ai free tier
def try_getimg():
    print("\n=== Trying getimg.ai ===")
    url = "https://api.getimg.ai/v1/stable-diffusion-xl/text-to-image"
    payload = {
        "prompt": prompt,
        "width": 768,
        "height": 1344,
        "steps": 25,
        "output_format": "png",
    }
    try:
        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=120)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.text[:300]}")
    except Exception as e:
        print(f"Error: {e}")

# Method 6: Dezgo (free)
def try_dezgo():
    print("\n=== Trying Dezgo ===")
    url = "https://api.dezgo.com/text2image"
    payload = {
        "prompt": prompt,
        "width": 768,
        "height": 1344,
        "model": "sdxl",
        "negative_prompt": "ugly, blurry",
        "guidance": 7,
        "steps": 30,
    }
    try:
        resp = requests.post(url, data=payload, timeout=180)
        print(f"Status: {resp.status_code}, Size={len(resp.content)}, CT={resp.headers.get('content-type','?')}")
        if resp.status_code == 200 and len(resp.content) > 10000:
            path = os.path.join(OUTPUT_DIR, "test_dezgo.png")
            with open(path, "wb") as f:
                f.write(resp.content)
            print(f"  SAVED: {path}")
            return True
    except Exception as e:
        print(f"Error: {e}")
    return False

try_pollinations()
try_together()
try_prodia()
try_dezgo()
