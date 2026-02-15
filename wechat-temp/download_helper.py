"""
Download images from jimeng using browser as proxy.
Click each image, get 1080px URL, navigate to it, save response.
"""
import subprocess, json, time, base64, os

output_dir = r"D:\video-analysis\output\原生家庭\images"
os.makedirs(output_dir, exist_ok=True)

# Scene order (newest first on asset page, we need oldest first for video)
# 10 groups of 4, pick first from each
# From the full ID list, positions 0,4,8,...,36 are first of each group
# But asset page shows newest first, so reverse for scene numbering

# Known 1080px URL for scene_01 (corner girl):
scene01_url = "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/72f39ecb14164566be50cf659d6f3395~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=nCYyxOvDzOK488lPqlvsFZVairg%3D&format=.webp"

# For the remaining 9, I need to click each image in the asset page
# and extract the 1080 URL that loads in the preview

# Write a helper that uses PowerShell to call the browser tool
print("Script ready. Use browser automation to download each image.")
print(f"Output: {output_dir}")
