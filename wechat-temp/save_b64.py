"""
Save jimeng images from base64 extracted via browser.
Run from PowerShell, pass base64 as argument.
"""
import base64, sys, os
from PIL import Image
from io import BytesIO

output_dir = r"D:\video-analysis\output\原生家庭\images"
os.makedirs(output_dir, exist_ok=True)

scene_name = sys.argv[1]  # e.g. scene_02
b64_data = sys.argv[2]

img_data = base64.b64decode(b64_data)
img = Image.open(BytesIO(img_data))
# Upscale to 1080x1920
img_resized = img.resize((1080, 1920), Image.LANCZOS)
out_path = os.path.join(output_dir, f"{scene_name}.png")
img_resized.save(out_path)
print(f"Saved {scene_name}: {img.size} -> {img_resized.size} @ {out_path}")
