"""Generate remaining scenes 8-10 with retry"""
import requests
import os
import time

OUTPUT_DIR = r"D:\video-analysis\output\原生家庭\images"
API_KEY = "587874ff0a224df9ac01c5eabad7209e.TpkrPT7K7Qva7Wsh"
STYLE = "deep blue indigo tones, digital painting, emotional, cinematic lighting, anime illustration style, hand-drawn quality, soft glow, melancholic atmosphere"

remaining = {
    8: f"A woman exhausted offering her heart to indifferent partner, wilting flowers around her, self-sacrifice, {STYLE}",
    9: f"An adult woman crying with transparent ghost of her inner child overlapping, mirror reflection showing child self, {STYLE}",
    10: f"A person standing at dawn breaking free from dark chains, butterfly wings emerging, light breaking through darkness, hope and healing, {STYLE}",
}

for scene_num, prompt in remaining.items():
    out_path = os.path.join(OUTPUT_DIR, f"scene_{scene_num:02d}.png")
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        print(f"Scene {scene_num} exists, skipping")
        continue
    
    for attempt in range(5):
        print(f"Scene {scene_num}, attempt {attempt+1}...")
        resp = requests.post(
            "https://open.bigmodel.cn/api/paas/v4/images/generations",
            json={"model": "cogview-3-plus", "prompt": prompt, "size": "768x1344"},
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            timeout=120
        )
        if resp.status_code == 200:
            data = resp.json()
            img_url = data.get('data', [{}])[0].get('url', '')
            if img_url:
                img = requests.get(img_url, timeout=60)
                with open(out_path, "wb") as f:
                    f.write(img.content)
                print(f"  Saved: {out_path} ({os.path.getsize(out_path)} bytes)")
                break
        elif resp.status_code == 429:
            print(f"  Rate limited, waiting 30s...")
            time.sleep(30)
        else:
            print(f"  Error: {resp.status_code} {resp.text[:200]}")
            time.sleep(10)
    else:
        print(f"  FAILED scene {scene_num} after 5 attempts")
    time.sleep(3)

# Verify all
for i in range(1, 11):
    p = os.path.join(OUTPUT_DIR, f"scene_{i:02d}.png")
    if os.path.exists(p):
        print(f"scene_{i:02d}.png: {os.path.getsize(p)} bytes")
    else:
        print(f"scene_{i:02d}.png: MISSING")
