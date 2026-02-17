#!/usr/bin/env python3
"""Fetch all videos from a Douyin user profile via local API."""
import requests, json, sys, os, time

API_BASE = "http://localhost:18810"
sec_uid = sys.argv[1]
output_dir = sys.argv[2] if len(sys.argv) > 2 else "."

os.makedirs(output_dir, exist_ok=True)

all_videos = []
cursor = 0
page = 0

while True:
    page += 1
    url = f"{API_BASE}/api/douyin/web/fetch_user_post_videos?sec_user_id={sec_uid}&max_cursor={cursor}&count=20"
    r = requests.get(url, timeout=30)
    data = r.json()
    
    aweme_list = data.get("data", {}).get("aweme_list", [])
    has_more = data.get("data", {}).get("has_more", False)
    cursor = data.get("data", {}).get("max_cursor", 0)
    
    for v in aweme_list:
        stats = v.get("statistics", {})
        vid = v.get("aweme_id", "")
        desc = v.get("desc", "")
        duration = v.get("duration", 0)  # ms
        
        # video dimensions
        w = v.get("video", {}).get("width", 0)
        h = v.get("video", {}).get("height", 0)
        
        # tags
        text_extra = v.get("text_extra", [])
        tags = [t.get("hashtag_name", "") for t in (text_extra or []) if t.get("hashtag_name")]
        
        # music
        music = v.get("music", {})
        music_title = music.get("title", "") if music else ""
        
        all_videos.append({
            "aweme_id": vid,
            "desc": desc,
            "duration_ms": duration,
            "width": w,
            "height": h,
            "digg_count": stats.get("digg_count", 0),
            "comment_count": stats.get("comment_count", 0),
            "collect_count": stats.get("collect_count", 0),
            "share_count": stats.get("share_count", 0),
            "play_count": stats.get("play_count", 0),
            "tags": tags,
            "music_title": music_title,
            "create_time": v.get("create_time", 0),
        })
    
    print(f"Page {page}: got {len(aweme_list)} videos, total {len(all_videos)}, has_more={has_more}", flush=True)
    
    if not has_more or not aweme_list:
        break
    time.sleep(1)

# Sort by digg_count desc
all_videos.sort(key=lambda x: x["digg_count"], reverse=True)

out_path = os.path.join(output_dir, "videos.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(all_videos, f, ensure_ascii=False, indent=2)

print(f"\nTotal: {len(all_videos)} videos saved to {out_path}")
print(f"\nTop 10 by likes:")
for i, v in enumerate(all_videos[:10]):
    print(f"  {i+1}. [{v['digg_count']:,} likes] {v['desc'][:80]}")
