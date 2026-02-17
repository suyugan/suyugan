"""预生成所有场景的JS代码"""
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

PROMPTS_FILE = r'D:\video-analysis\output\taohaoxing\prompts.json'
GEN_SCRIPT = r'D:\video-analysis\scripts\jimeng_fetch_gen.py'

d = json.load(open(PROMPTS_FILE, 'r', encoding='utf-8'))
scenes = {s['scene_num']: s['prompt'] for s in d['scenes']}

all_js = {}
for num in range(13, 23):
    prompt = scenes[num]
    r = subprocess.run(
        ['python', GEN_SCRIPT, '--action', 'generate', '--prompt', prompt, '--ratio', '16:9', '--json'],
        capture_output=True, text=True, encoding='utf-8', timeout=15
    )
    data = json.loads(r.stdout.strip())
    all_js[num] = {"js": data["js"], "submit_id": data["submit_id"], "prompt_short": prompt[:40]}
    
    # Also generate poll JS
    r2 = subprocess.run(
        ['python', GEN_SCRIPT, '--action', 'poll', '--submit-id', data["submit_id"]],
        capture_output=True, text=True, encoding='utf-8', timeout=15
    )
    all_js[num]["poll_js"] = r2.stdout.strip()

# Save
with open(r'D:\video-analysis\output\taohaoxing\gen_js_13_22.json', 'w', encoding='utf-8') as f:
    json.dump(all_js, f, ensure_ascii=False, indent=2)

print("Done. Submit IDs:")
for num in range(13, 23):
    print(f"  scene_{num:02d}: {all_js[num]['submit_id']}")
