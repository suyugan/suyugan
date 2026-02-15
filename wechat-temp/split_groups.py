import json
with open(r'D:\video-analysis\video_list.json','r',encoding='utf-8') as f:
    videos = json.load(f)
n = len(videos)
groups = []
size = n // 10
remainder = n % 10
idx = 0
for i in range(10):
    g = size + (1 if i < remainder else 0)
    groups.append(videos[idx:idx+g])
    idx += g
for i, grp in enumerate(groups):
    ids = [v["id"] for v in grp]
    descs = [v["desc"][:30] for v in grp]
    print(f"Group {i+1}: {len(grp)} videos")
    for j, (vid, desc) in enumerate(zip(ids, descs)):
        print(f"  {j+1}. {vid} - {desc}")
