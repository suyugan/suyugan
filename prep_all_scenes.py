import json, subprocess, sys, time
sys.stdout.reconfigure(encoding='utf-8')

# Read prompts
d = json.load(open(r'D:\video-analysis\output\taohaoxing\prompts.json', 'r', encoding='utf-8'))
scenes = {s['scene_num']: s['prompt'] for s in d['scenes'] if 7 <= s['scene_num'] <= 22}

for scene_num in sorted(scenes.keys()):
    prompt = scenes[scene_num]
    print(f"\n=== SCENE {scene_num} ===")
    
    # Step A: Generate submit JS
    result = subprocess.run(
        ['python', r'D:\video-analysis\scripts\jimeng_fetch_gen.py',
         '--action', 'generate', '--prompt', prompt, '--ratio', '16:9', '--json'],
        capture_output=True, text=True, encoding='utf-8'
    )
    try:
        data = json.loads(result.stdout)
        js = data['js']
        submit_id = data['submit_id']
        print(f"submit_id: {submit_id}")
    except Exception as e:
        print(f"ERROR generating JS: {e}")
        print(f"stdout: {result.stdout[:200]}")
        continue
    
    # Output for the orchestrator
    print(f"GENERATE_JS_START_{scene_num}")
    print(js)
    print(f"GENERATE_JS_END_{scene_num}")
    print(f"SUBMIT_ID:{submit_id}")
    
    # Step D: Generate poll JS
    poll_result = subprocess.run(
        ['python', r'D:\video-analysis\scripts\jimeng_fetch_gen.py',
         '--action', 'poll', '--submit-id', submit_id, '--json'],
        capture_output=True, text=True, encoding='utf-8'
    )
    poll_js = poll_result.stdout.strip()
    print(f"POLL_JS_START_{scene_num}")
    print(poll_js)
    print(f"POLL_JS_END_{scene_num}")
