"""
为原生家庭视频生成10张AI插画
尝试方案：SiliconFlow API -> FLUX on server -> Pollinations
"""
import requests
import json
import base64
import os
import time

OUTPUT_DIR = r"D:\video-analysis\output\原生家庭\images"

STYLE = "deep blue indigo tones, digital painting, emotional, cinematic lighting, anime illustration style, hand-drawn quality, vertical composition, soft glow, melancholic atmosphere"

SCENES = [
    # 1. 开头 - 手机焦虑
    f"A young woman sitting alone on bed at night checking phone anxiously, blue light illuminating worried face, dark bedroom, {STYLE}",
    # 2. 冷战 - 把自己关起来
    f"A person curled up behind closed door hugging knees, shadow of partner standing outside, dim hallway light, {STYLE}",
    # 3. 童年 - 原生家庭写入身体
    f"A small child sitting alone watching parents argue as dark silhouettes, broken family scene, child looks scared, {STYLE}",
    # 4. 安全型依恋 - 温暖家庭
    f"Warm loving family scene, mother gently holding child, soft golden light in cozy room, feeling of safety and love, {STYLE}",
    # 5. 回避型 - 冷淡家庭
    f"A child crying alone in empty room reaching out hand, parents turned away ignoring, cold atmosphere, {STYLE}",
    # 6. 回避型恋爱 - 推开爱人
    f"A couple where one person reaches out while the other turns away pushing them back, invisible wall between them, {STYLE}",
    # 7. 焦虑型 - 察言观色
    f"A small child carefully watching mother's changing expressions, walking on eggshells, tension in the air, split face showing happy and angry, {STYLE}",
    # 8. 讨好型恋爱 - 卑微付出
    f"A woman exhausted kneeling offering heart to indifferent partner, wilting flowers around her, self-sacrifice metaphor, {STYLE}",
    # 9. 内在小孩 - 成年人里的孩子
    f"An adult woman crying with ghostly transparent image of her inner child overlapping, mirror reflection showing child self, {STYLE}",
    # 10. 结尾 - 改写结局/治愈
    f"A person standing at dawn breaking free from dark chains, butterfly wings emerging, light breaking through darkness, hope and healing, {STYLE}",
]

def try_siliconflow():
    """Try SiliconFlow API (has free tier)"""
    # Try without API key first, then with common free tier
    urls_and_keys = [
        ("https://api.siliconflow.cn/v1/images/generations", None),
    ]
    
    for url, key in urls_and_keys:
        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"
        
        payload = {
            "model": "stabilityai/stable-diffusion-3-medium",
            "prompt": SCENES[0],
            "image_size": "768x1344",
            "num_inference_steps": 20,
        }
        
        try:
            print(f"Trying SiliconFlow: {url}")
            resp = requests.post(url, json=payload, headers=headers, timeout=120)
            print(f"Status: {resp.status_code}")
            print(f"Response: {resp.text[:500]}")
            if resp.status_code == 200:
                return "siliconflow", url, key
        except Exception as e:
            print(f"Error: {e}")
    
    return None

def try_pollinations():
    """Try Pollinations.ai"""
    import urllib.parse
    prompt = urllib.parse.quote(SCENES[0])
    url = f"https://image.pollinations.ai/prompt/{prompt}?width=768&height=1344&nologo=true&model=flux"
    print(f"Trying Pollinations...")
    try:
        resp = requests.get(url, timeout=180, allow_redirects=True)
        print(f"Status: {resp.status_code}, Content-Type: {resp.headers.get('content-type','?')}, Size: {len(resp.content)}")
        if resp.status_code == 200 and len(resp.content) > 10000:
            test_path = os.path.join(OUTPUT_DIR, "test_pollinations.png")
            with open(test_path, "wb") as f:
                f.write(resp.content)
            print(f"Test image saved: {test_path} ({len(resp.content)} bytes)")
            return "pollinations"
    except Exception as e:
        print(f"Error: {e}")
    return None

def try_cloudflare():
    """Try Cloudflare Workers AI - needs account"""
    print("Cloudflare Workers AI requires account setup, skipping for now")
    return None

def try_flux_server():
    """Try FLUX via paramiko on Tencent Cloud server"""
    try:
        import paramiko
    except ImportError:
        import subprocess, sys
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'paramiko', '-q'])
        import paramiko
    
    print("Trying FLUX on Tencent Cloud server...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=30)
        print("SSH connected!")
        
        # Check if gradio_client is installed
        stdin, stdout, stderr = ssh.exec_command('pip3 install gradio_client -q 2>&1 && python3 -c "from gradio_client import Client; print(\'OK\')"', timeout=120)
        result = stdout.read().decode()
        err = stderr.read().decode()
        print(f"gradio_client check: {result.strip()} {err.strip()}")
        
        # Try generating one image
        test_script = '''
import sys
sys.path.insert(0, '/home/ubuntu/.local/lib/python3.12/site-packages')
try:
    from gradio_client import Client
    client = Client("black-forest-labs/FLUX.1-schnell")
    result = client.predict(
        prompt="a lonely child in dark room, deep blue indigo tones, digital painting, anime style",
        seed=0, randomize_seed=True, width=768, height=1344,
        num_inference_steps=4, api_name="/infer"
    )
    print("SUCCESS:" + str(result))
except Exception as e:
    print("FAIL:" + str(e))
'''
        stdin, stdout, stderr = ssh.exec_command(f'python3 -c """{test_script}"""', timeout=300)
        result = stdout.read().decode()
        err = stderr.read().decode()
        print(f"FLUX result: {result.strip()}")
        if err.strip():
            print(f"FLUX stderr: {err.strip()[:500]}")
        
        if "SUCCESS:" in result:
            return "flux_server", ssh
        
        ssh.close()
    except Exception as e:
        print(f"SSH error: {e}")
    
    return None

def generate_all_pollinations():
    """Generate all 10 images via Pollinations"""
    import urllib.parse
    
    for i, prompt in enumerate(SCENES):
        out_path = os.path.join(OUTPUT_DIR, f"scene_{i+1:02d}.png")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            print(f"Scene {i+1} already exists, skipping")
            continue
            
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=1344&nologo=true&model=flux"
        
        print(f"Generating scene {i+1}/10...")
        for attempt in range(3):
            try:
                resp = requests.get(url, timeout=300, allow_redirects=True)
                if resp.status_code == 200 and len(resp.content) > 10000:
                    with open(out_path, "wb") as f:
                        f.write(resp.content)
                    print(f"  Saved: {out_path} ({len(resp.content)} bytes)")
                    break
                else:
                    print(f"  Attempt {attempt+1} failed: status={resp.status_code}, size={len(resp.content)}")
                    time.sleep(5)
            except Exception as e:
                print(f"  Attempt {attempt+1} error: {e}")
                time.sleep(10)
        else:
            print(f"  FAILED to generate scene {i+1} after 3 attempts!")
        
        time.sleep(3)  # Rate limiting

def generate_all_flux(ssh):
    """Generate all 10 images via FLUX on server, then download"""
    sftp = ssh.open_sftp()
    
    for i, prompt in enumerate(SCENES):
        out_path = os.path.join(OUTPUT_DIR, f"scene_{i+1:02d}.png")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
            print(f"Scene {i+1} already exists, skipping")
            continue
        
        print(f"Generating scene {i+1}/10 via FLUX...")
        script = f'''
import sys, shutil
sys.path.insert(0, '/home/ubuntu/.local/lib/python3.12/site-packages')
from gradio_client import Client
client = Client("black-forest-labs/FLUX.1-schnell")
result = client.predict(
    prompt="""{prompt}""",
    seed=0, randomize_seed=True, width=768, height=1344,
    num_inference_steps=4, api_name="/infer"
)
# result is (filepath, seed)
src = result[0] if isinstance(result, (list,tuple)) else result
shutil.copy(src, "/tmp/flux_output.webp")
print("DONE")
'''
        stdin, stdout, stderr = ssh.exec_command(f"python3 << 'PYEOF'\n{script}\nPYEOF", timeout=300)
        result = stdout.read().decode()
        err = stderr.read().decode()
        
        if "DONE" in result:
            remote_path = "/tmp/flux_output.webp"
            sftp.get(remote_path, out_path)
            print(f"  Downloaded: {out_path}")
        else:
            print(f"  FAILED: {result.strip()} | {err.strip()[:200]}")
        
        time.sleep(2)
    
    sftp.close()

if __name__ == "__main__":
    print("=== Trying Pollinations first (simplest) ===")
    result = try_pollinations()
    if result:
        print("\n=== Pollinations works! Generating all images ===")
        generate_all_pollinations()
    else:
        print("\n=== Pollinations failed, trying FLUX on server ===")
        result = try_flux_server()
        if result:
            method, ssh = result
            print("\n=== FLUX works! Generating all images ===")
            generate_all_flux(ssh)
            ssh.close()
        else:
            print("\n=== All methods failed! ===")
            print("Need to try: SiliconFlow with API key, or Cloudflare Workers AI")
    
    # Check results
    generated = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("scene_") and f.endswith(".png")]
    print(f"\n=== Generated {len(generated)}/10 images ===")
    for f in sorted(generated):
        path = os.path.join(OUTPUT_DIR, f)
        print(f"  {f}: {os.path.getsize(path)} bytes")
