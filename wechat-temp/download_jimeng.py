"""Download images from jimeng by navigating browser to each image URL directly"""
import subprocess, os, time, json, base64

output_dir = r"D:\video-analysis\output\原生家庭\images"
os.makedirs(output_dir, exist_ok=True)

# We'll use a different approach: save browser screenshots of each image in full resolution
# For now, let's try to use the browser's fetch API through a temp page

# Image IDs from the asset page (first from each group of 4, newest first = scene 10 to scene 1)
# Based on the asset grid order:
# Row 1: scene10(sunset walk x4), scene9(meditation x4), scene8(chains x2...)
image_ids = [
    # scene 1 (corner girl) - oldest generation, English prompt 9:16
    "72f39ecb14164566be50cf659d6f3395",
    # scene 2 (warm family)
    "f125a56d845e41cfb0c26a47f1fe84c8",
    # scene 3 (cry alone, cold family)
    "7b620f169dbc4faf84325dbe69c9dfef",
    # scene 4 (push hand, avoidant love)
    "a8dda736e69744bab978d7169ac84894",
    # scene 5 (peek door, anxious child)
    "31500cfb109a41fb941e544068eaace0",
    # scene 6 (people pleaser)
    "9f59e6aed3624ef09a5f94f0066f2ff4",
    # scene 7 (inner child ghost)
    "58952f671e3241f08660ff948dd249d7",
    # scene 8 (three generations chains)
    "410591cfa4094f5dbd50eba9649a297a",
    # scene 9 (meditation healing)
    "6e8cf6ccccbf491ea67e81f04b66abbe",
    # scene 10 (walking to sunrise)
    # use first ID from asset page which should be newest
    "5cbd46387da2415ab85341d49677ae9b",
]

# The working URL template (from the asset page thumbnails, 480px)
base_url = "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/{id}~tplv-tb4s082cfz-aigc_resize:480:480.webp?lk3s=43402efa&x-expires=1772928000&x-signature=nCYyxOvDzOK488lPqlvsFZVairg%3D&format=.webp"

# But signatures differ per image... We need to get individual signed URLs
# Let's just use the 480px versions and upscale with ffmpeg
print("Note: Need to get signed URLs from browser for each image")
print("Image IDs collected:", len(image_ids))
