"""Generate images using Zhipu CogView API"""
import requests
import os
import time

OUTPUT_DIR = r"D:\video-analysis\output\原生家庭\images"
API_KEY = "587874ff0a224df9ac01c5eabad7209e.TpkrPT7K7Qva7Wsh"

STYLE = "deep blue indigo tones, digital painting, emotional, cinematic lighting, anime illustration style, hand-drawn quality, soft glow, melancholic atmosphere"

SCENES = [
    f"A young woman sitting alone on bed at night checking phone anxiously, blue light illuminating worried face, dark bedroom, {STYLE}",
    f"A person curled up behind closed door hugging knees, shadow of partner standing outside, dim hallway light, {STYLE}",
    f"A small child sitting alone watching parents argue as dark silhouettes, broken family scene, child looks scared, {STYLE}",
    f"Warm loving family scene, mother gently holding child, soft golden light in cozy room, feeling of safety and love, {STYLE}",
    f"A child crying alone in empty room reaching out hand, parents turned away ignoring, cold atmosphere, {STYLE}",
    f"A couple where one person reaches out while the other turns away, invisible wall between them, emotional distance, {STYLE}",
    f"A small child carefully watching mothers changing expressions, walking on eggshells, tension in the air, {STYLE}",
    f"A woman exhausted offering her heart to indifferent partner, wilting flowers around her, self-sacrifice, {STYLE}",
    f"An adult woman crying with transparent ghost of her inner child overlapping, mirror reflection showing child self, {STYLE}",
    f"A person standing at dawn breaking free from dark chains, butterfly wings emerging, light breaking through darkness, hope and healing, {STYLE}",
]

def generate_image(prompt, output_path):
    url = "https://open.bigmodel.cn/api/paas/v4/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    # CogView supports 1024x1024, 768x1344, 864x1152 etc
    payload = {
        "model": "cogview-3-plus",
        "prompt": prompt,
        "size": "768x1344",
    }
    
    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    if resp.status_code != 200:
        print(f"  Error: {resp.status_code} {resp.text[:200]}")
        return False
    
    data = resp.json()
    if 'data' not in data or not data['data']:
        print(f"  No data: {data}")
        return False
    
    img_url = data['data'][0].get('url', '')
    if not img_url:
        print(f"  No URL in response")
        return False
    
    img_resp = requests.get(img_url, timeout=60)
    with open(output_path, "wb") as f:
        f.write(img_resp.content)
    return True

# Test with first image
print("Testing CogView with scene 1...")
test_path = os.path.join(OUTPUT_DIR, "test_cogview.png")
if generate_image(SCENES[0], test_path):
    print(f"SUCCESS! Test image: {test_path} ({os.path.getsize(test_path)} bytes)")
    
    # Generate all 10
    for i, prompt in enumerate(SCENES):
        out_path = os.path.join(OUTPUT_DIR, f"scene_{i+1:02d}.png")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            print(f"Scene {i+1} exists, skipping")
            continue
        
        print(f"Generating scene {i+1}/10...")
        if generate_image(prompt, out_path):
            print(f"  Saved: {out_path} ({os.path.getsize(out_path)} bytes)")
        else:
            print(f"  FAILED scene {i+1}")
        
        time.sleep(2)  # Rate limit
    
    # Summary
    generated = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("scene_") and f.endswith(".png")]
    print(f"\n=== Generated {len(generated)}/10 images ===")
else:
    print("CogView test FAILED!")
