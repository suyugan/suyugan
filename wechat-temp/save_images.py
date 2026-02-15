"""Save jimeng images from base64 data"""
import base64, os, sys, json

output_dir = r"D:\video-analysis\output\原生家庭\images"
os.makedirs(output_dir, exist_ok=True)

# Read base64 data from stdin (piped from browser)
data = json.loads(sys.argv[1]) if len(sys.argv) > 1 else json.loads(sys.stdin.read())

for item in data:
    scene = item["scene"]
    b64 = item["b64"]
    # Remove data:image/webp;base64, prefix
    if "," in b64:
        b64 = b64.split(",", 1)[1]
    img_data = base64.b64decode(b64)
    path = os.path.join(output_dir, f"{scene}.webp")
    with open(path, "wb") as f:
        f.write(img_data)
    print(f"Saved {scene}: {len(img_data)} bytes -> {path}")
