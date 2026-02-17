import json, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open(r'D:\video-analysis\output\taohaoxing\prompts.json', 'r', encoding='utf-8'))
for s in d['scenes']:
    if 13 <= s['scene_num'] <= 22:
        print(f"scene_{s['scene_num']:02d}: {s['prompt'][:80]}")
