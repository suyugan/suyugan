import json, subprocess, sys, time, os, urllib.request

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = r'D:\video-analysis\output\taohaoxing\images'
PROMPTS_FILE = r'D:\video-analysis\output\taohaoxing\prompts.json'
GEN_SCRIPT = r'D:\video-analysis\scripts\jimeng_fetch_gen.py'

d = json.load(open(PROMPTS_FILE, 'r', encoding='utf-8'))
scenes = {s['scene_num']: s['prompt'] for s in d['scenes']}

results = {}

for num in range(13, 23):
    out_path = os.path.join(OUTPUT_DIR, f'scene_{num:02d}.webp')
    if os.path.exists(out_path):
        print(f"[scene_{num:02d}] 已存在，跳过")
        results[num] = "skipped"
        continue
    
    prompt = scenes.get(num)
    if not prompt:
        print(f"[scene_{num:02d}] 提示词不存在!")
        results[num] = "no prompt"
        continue
    
    print(f"\n[scene_{num:02d}] 开始生成...")
    print(f"  提示词: {prompt[:50]}...")
    
    # Generate
    try:
        r = subprocess.run(
            ['python', GEN_SCRIPT, '--action', 'generate', '--prompt', prompt, '--ratio', '16:9', '--json'],
            capture_output=True, text=True, encoding='utf-8', timeout=30
        )
        gen_out = r.stdout.strip()
        print(f"  generate输出: {gen_out[:200]}")
        gen_data = json.loads(gen_out)
        submit_id = gen_data.get('submit_id')
        if not submit_id:
            print(f"  错误: 没有submit_id")
            results[num] = f"no submit_id: {gen_out[:100]}"
            continue
    except Exception as e:
        print(f"  generate异常: {e}")
        results[num] = f"generate error: {e}"
        continue
    
    print(f"  submit_id: {submit_id}")
    
    # Poll
    start = time.time()
    image_url = None
    while time.time() - start < 120:
        time.sleep(5)
        try:
            r = subprocess.run(
                ['python', GEN_SCRIPT, '--action', 'poll', '--submit-id', submit_id, '--json'],
                capture_output=True, text=True, encoding='utf-8', timeout=30
            )
            poll_out = r.stdout.strip()
            poll_data = json.loads(poll_out)
            status = poll_data.get('status', '')
            print(f"  轮询: status={status} ({int(time.time()-start)}s)")
            
            if status == 'done':
                urls = poll_data.get('urls', [])
                if urls:
                    image_url = urls[0]
                break
            elif status == 'failed':
                print(f"  生成失败: {poll_data}")
                break
        except Exception as e:
            print(f"  轮询异常: {e}")
    
    if image_url:
        # Download
        try:
            urllib.request.urlretrieve(image_url, out_path)
            size = os.path.getsize(out_path)
            print(f"  ✅ 保存成功: {out_path} ({size} bytes)")
            results[num] = "success"
        except Exception as e:
            print(f"  下载失败: {e}")
            results[num] = f"download error: {e}"
    else:
        print(f"  ❌ 未获取到图片URL")
        results[num] = "no image url"
    
    time.sleep(3)  # 间隔

print("\n\n===== 结果汇总 =====")
for num in range(13, 23):
    print(f"scene_{num:02d}: {results.get(num, 'unknown')}")

print("\n===== 目录文件列表 =====")
for f in sorted(os.listdir(OUTPUT_DIR)):
    fp = os.path.join(OUTPUT_DIR, f)
    print(f"  {f}  ({os.path.getsize(fp)} bytes)")
