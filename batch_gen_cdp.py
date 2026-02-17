"""批量生成scene_13到scene_22的配图，通过CDP直接在即梦浏览器中执行JS"""
import json, subprocess, sys, time, os, urllib.request, websocket, ssl

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = r'D:\video-analysis\output\taohaoxing\images'
PROMPTS_FILE = r'D:\video-analysis\output\taohaoxing\prompts.json'
GEN_SCRIPT = r'D:\video-analysis\scripts\jimeng_fetch_gen.py'
TAB_WS = "ws://127.0.0.1:18800/devtools/page/67AC4FF65CBF44C148831B65C28FBD9C"

def cdp_eval(ws, expression, timeout=30):
    """通过CDP执行JS并返回结果"""
    import random
    msg_id = random.randint(1, 999999)
    ws.send(json.dumps({
        "id": msg_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": expression,
            "returnByValue": True,
            "awaitPromise": True,
            "timeout": timeout * 1000
        }
    }))
    
    start = time.time()
    while time.time() - start < timeout + 5:
        try:
            resp = ws.recv()
            data = json.loads(resp)
            if data.get("id") == msg_id:
                result = data.get("result", {}).get("result", {})
                return result.get("value", str(result))
        except websocket.WebSocketTimeoutException:
            continue
    return None

# Load prompts
d = json.load(open(PROMPTS_FILE, 'r', encoding='utf-8'))
scenes = {s['scene_num']: s['prompt'] for s in d['scenes']}

# Connect to browser
print("连接浏览器...")
ws = websocket.WebSocket()
ws.settimeout(35)
ws.connect(TAB_WS, origin="http://localhost")
print("已连接")

# Load MD5 helper
print("加载MD5 helper...")
# Read the SIGN_JS_HELPER from the script
r = subprocess.run(
    ['python', '-c', f'import sys; sys.path.insert(0, r"D:\\video-analysis\\scripts"); from jimeng_fetch_gen import SIGN_JS_HELPER; print(SIGN_JS_HELPER)'],
    capture_output=True, text=True, encoding='utf-8'
)
md5_js = r.stdout.strip()
result = cdp_eval(ws, md5_js)
print(f"MD5加载结果: {result}")

results = {}

for num in range(13, 23):
    out_path = os.path.join(OUTPUT_DIR, f'scene_{num:02d}.webp')
    if os.path.exists(out_path):
        print(f"\n[scene_{num:02d}] 已存在，跳过")
        results[num] = "skipped"
        continue
    
    prompt = scenes.get(num)
    if not prompt:
        print(f"\n[scene_{num:02d}] 提示词不存在!")
        results[num] = "no prompt"
        continue
    
    print(f"\n[scene_{num:02d}] 开始生成...")
    print(f"  提示词: {prompt[:50]}...")
    
    # Generate JS
    try:
        r = subprocess.run(
            ['python', GEN_SCRIPT, '--action', 'generate', '--prompt', prompt, '--ratio', '16:9', '--json'],
            capture_output=True, text=True, encoding='utf-8', timeout=15
        )
        gen_data = json.loads(r.stdout.strip())
        gen_js = gen_data['js']
        submit_id = gen_data['submit_id']
        print(f"  submit_id: {submit_id}")
    except Exception as e:
        print(f"  生成JS失败: {e}")
        results[num] = f"js gen error: {e}"
        continue
    
    # Execute generate in browser
    try:
        gen_result = cdp_eval(ws, gen_js, timeout=30)
        print(f"  generate结果: {gen_result}")
        if gen_result:
            gr = json.loads(gen_result) if isinstance(gen_result, str) else gen_result
            if gr.get('ret') != 0 and gr.get('ret') is not None:
                print(f"  ⚠️ API返回错误: ret={gr.get('ret')}, errmsg={gr.get('errmsg')}")
                results[num] = f"api error: {gr.get('errmsg')}"
                continue
    except Exception as e:
        print(f"  执行generate失败: {e}")
        results[num] = f"generate exec error: {e}"
        continue
    
    # Poll
    poll_js_code = subprocess.run(
        ['python', GEN_SCRIPT, '--action', 'poll', '--submit-id', submit_id],
        capture_output=True, text=True, encoding='utf-8', timeout=15
    ).stdout.strip()
    
    start = time.time()
    image_url = None
    while time.time() - start < 120:
        time.sleep(5)
        try:
            poll_result = cdp_eval(ws, poll_js_code, timeout=30)
            if poll_result:
                pr = json.loads(poll_result) if isinstance(poll_result, str) else poll_result
                status = pr.get('status', '')
                print(f"  轮询: status={status} ({int(time.time()-start)}s)")
                
                if status == 'done':
                    urls = pr.get('urls', [])
                    if urls:
                        image_url = urls[0]
                    break
                elif status == 'failed':
                    print(f"  生成失败")
                    break
        except Exception as e:
            print(f"  轮询异常: {e}")
    
    if image_url:
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
    
    time.sleep(3)

ws.close()

print("\n\n===== 结果汇总 =====")
for num in range(13, 23):
    print(f"scene_{num:02d}: {results.get(num, 'unknown')}")

print("\n===== 目录文件列表 =====")
for f in sorted(os.listdir(OUTPUT_DIR)):
    fp = os.path.join(OUTPUT_DIR, f)
    print(f"  {f}  ({os.path.getsize(fp)} bytes)")
