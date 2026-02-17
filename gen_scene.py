import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')

scene_num = int(sys.argv[1])
action = sys.argv[2]  # "generate" or "poll"

if action == "generate":
    d = json.load(open(r'D:\video-analysis\output\taohaoxing\prompts.json', 'r', encoding='utf-8'))
    prompt = None
    for s in d['scenes']:
        if s['scene_num'] == scene_num:
            prompt = s['prompt']
            break
    if not prompt:
        print(json.dumps({"error": "scene not found"}))
        sys.exit(1)
    
    result = subprocess.run(
        ['python', r'D:\video-analysis\scripts\jimeng_fetch_gen.py', 
         '--action', 'generate', '--prompt', prompt, '--ratio', '16:9', '--json'],
        capture_output=True, text=True, encoding='utf-8'
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
elif action == "poll":
    submit_id = sys.argv[3]
    result = subprocess.run(
        ['python', r'D:\video-analysis\scripts\jimeng_fetch_gen.py',
         '--action', 'poll', '--submit-id', submit_id, '--json'],
        capture_output=True, text=True, encoding='utf-8'
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
