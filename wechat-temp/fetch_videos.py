#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests, json, os

sec_uid = 'MS4wLjABAAAAsYnXfa8lGctEOw-jFOxRAe1enKCEXD9LLvz5ECWT8jl4a-tUx7KbN_VBgg71eogl'

all_videos = []
cursor = 0
page = 0

while True:
    page += 1
    r = requests.get(f'http://localhost:18810/api/douyin/web/fetch_user_post_videos?sec_user_id={sec_uid}&max_cursor={cursor}&count=20', timeout=10)
    data = r.json()['data']
    videos = data.get('aweme_list', [])
    for v in videos:
        all_videos.append({
            'id': v['aweme_id'],
            'desc': v.get('desc', '')[:100],
            'create_time': v.get('create_time', 0),
        })
    print(f'Page {page}: got {len(videos)} videos, total {len(all_videos)}')
    if not data.get('has_more') or not videos:
        break
    cursor = data.get('max_cursor', 0)

print(f'\nTotal videos: {len(all_videos)}')
for i, v in enumerate(all_videos):
    vid = v['id']
    desc = v['desc']
    print(f'{i+1}. [{vid}] {desc}')

os.makedirs(r'D:\video-analysis', exist_ok=True)
with open(r'D:\video-analysis\video_list.json', 'w', encoding='utf-8') as f:
    json.dump(all_videos, f, ensure_ascii=False, indent=2)
print(f'\nSaved to D:\\video-analysis\\video_list.json')
