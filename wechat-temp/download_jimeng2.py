"""
Download jimeng images via browser fetch (bypass CDN restrictions).
Uses browser evaluate to fetch each image, convert to base64, 
then saves via Python.
"""
import json, base64, os, time

output_dir = r"D:\video-analysis\output\原生家庭\images"
os.makedirs(output_dir, exist_ok=True)

# 10 groups of 4 images, pick first from each group
# Asset page order: newest first (scene 10 -> scene 1)
# Each group = 4 consecutive images
# From the 9:16 images (first 4 in the list are scene 1 original 9:16):
# 72f39ecb, 0f838360, 7be4fdbf, 3f5cb120 = scene 1 (corner girl) 480px versions

# For the other 9 scenes generated via "图片生成" mode, they appear as 360px thumbnails
# Groups of 4, newest first:

# Let's just select first image ID from each scene group
# From the full list (newest first):
scene_ids = {
    "scene_10": "5cbd46387da2415ab85341d49677ae9b",  # walking to sunrise
    "scene_09": "6e8cf6ccccbf491ea67e81f04b66abbe",  # meditation healing  
    "scene_08": "410591cfa4094f5dbd50eba9649a297a",  # three generations
    "scene_07": "58952f671e3241f08660ff948dd249d7",  # inner child
    "scene_06": "9f59e6aed3624ef09a5f94f0066f2ff4",  # people pleaser
    "scene_05": "31500cfb109a41fb941e544068eaace0",  # anxious peek door
    "scene_04": "a8dda736e69744bab978d7169ac84894",  # push away hand
    "scene_03": "7b620f169dbc4faf84325dbe69c9dfef",  # cry alone cold
    "scene_02": "f125a56d845e41cfb0c26a47f1fe84c8",  # warm family
    "scene_01": "72f39ecb14164566be50cf659d6f3395",  # corner girl
}

# We need the full signed URLs. Let's map IDs to URLs from what we collected.
# For now, output the mapping
for scene, img_id in sorted(scene_ids.items()):
    print(f"{scene}: {img_id}")
