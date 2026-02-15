"""Try HuggingFace Inference API with free token, and other approaches"""
import requests
import os
import base64

OUTPUT_DIR = r"D:\video-analysis\output\原生家庭\images"
prompt = "a lonely child in dark blue room, anime style, digital painting, emotional, deep indigo tones"

# Try HuggingFace serverless inference (free tier - limited)
def try_hf_inference():
    print("=== Trying HF Inference API (no token) ===")
    models = [
        "stabilityai/stable-diffusion-xl-base-1.0",
        "runwayml/stable-diffusion-v1-5",
        "CompVis/stable-diffusion-v1-4",
    ]
    for model in models:
        url = f"https://api-inference.huggingface.co/models/{model}"
        try:
            resp = requests.post(url, json={"inputs": prompt}, timeout=120)
            print(f"{model}: Status={resp.status_code}, Size={len(resp.content)}, CT={resp.headers.get('content-type','?')}")
            if resp.status_code == 200 and 'image' in resp.headers.get('content-type', ''):
                path = os.path.join(OUTPUT_DIR, "test_hf.png")
                with open(path, "wb") as f:
                    f.write(resp.content)
                print(f"  SAVED: {path}")
                return model
        except Exception as e:
            print(f"  Error: {e}")
    return None

# Try picsum/placeholder as absolute fallback (not AI but...)
# Actually let me try a different approach: use a Gradio Space that's accessible
def try_gradio_spaces():
    print("\n=== Trying Gradio Spaces directly ===")
    # Try stabilityai spaces
    spaces = [
        "https://stabilityai-stable-diffusion-3-5-large-turbo.hf.space/api/predict",
        "https://prodia-sdxl-stable-diffusion-xl.hf.space/api/predict",
    ]
    for space_url in spaces:
        try:
            resp = requests.post(space_url, json={"data": [prompt, "ugly", 25, 7, 768, 1344, 42]}, timeout=120)
            print(f"{space_url}: Status={resp.status_code}")
            print(f"  Body: {resp.text[:200]}")
        except Exception as e:
            print(f"  Error: {e}")

# Try limewire
def try_limewire():
    print("\n=== Trying Limewire ===")
    try:
        resp = requests.post("https://api.limewire.com/api/image/generation", 
            json={"prompt": prompt, "aspect_ratio": "9:16"},
            headers={"Content-Type": "application/json"},
            timeout=60)
        print(f"Status: {resp.status_code}, Body: {resp.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

# Try craiyon
def try_craiyon():
    print("\n=== Trying Craiyon ===")
    try:
        resp = requests.post("https://api.craiyon.com/v3", 
            json={"prompt": prompt, "version": "c4ue22fb7kb6wlac", "token": None},
            timeout=120)
        print(f"Status: {resp.status_code}, Size: {len(resp.content)}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Keys: {list(data.keys())}")
            if 'images' in data:
                img_data = base64.b64decode(data['images'][0])
                path = os.path.join(OUTPUT_DIR, "test_craiyon.png")
                with open(path, "wb") as f:
                    f.write(img_data)
                print(f"SAVED: {path}")
                return True
    except Exception as e:
        print(f"Error: {e}")
    return False

result = try_hf_inference()
if not result:
    try_craiyon()

