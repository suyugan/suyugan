"""
生成图片 - 通过paramiko上传脚本到服务器执行FLUX
"""
import os
import sys
import time

try:
    import paramiko
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'paramiko', '-q'])
    import paramiko

OUTPUT_DIR = r"D:\video-analysis\output\原生家庭\images"
STYLE = "deep blue indigo tones, digital painting, emotional, cinematic lighting, anime illustration style, hand-drawn quality, soft glow, melancholic atmosphere"

SCENES = [
    f"A young woman sitting alone on bed at night checking phone anxiously, blue light illuminating worried face, dark bedroom, {STYLE}",
    f"A person curled up behind closed door hugging knees, shadow of partner standing outside, dim hallway light, {STYLE}",
    f"A small child sitting alone watching parents argue as dark silhouettes, broken family scene, child looks scared, {STYLE}",
    f"Warm loving family scene, mother gently holding child, soft golden light in cozy room, feeling of safety and love, {STYLE}",
    f"A child crying alone in empty room reaching out hand, parents turned away ignoring, cold atmosphere, {STYLE}",
    f"A couple where one person reaches out while the other turns away, invisible wall between them, emotional distance, {STYLE}",
    f"A small child carefully watching mothers changing expressions, walking on eggshells, tension in the air, {STYLE}",
    f"A woman exhausted offering her heart to indifferent partner, wilting flowers around her, self-sacrifice, {STYLE}",
    f"An adult woman crying with transparent ghost of her inner child overlapping, mirror reflection showing child self, {STYLE}",
    f"A person standing at dawn breaking free from dark chains, butterfly wings emerging, light breaking through darkness, hope and healing, {STYLE}",
]

# Script to run on server for one image
REMOTE_SCRIPT_TEMPLATE = '''#!/usr/bin/env python3
import sys, shutil, os
sys.path.insert(0, os.path.expanduser("~/.local/lib/python3.12/site-packages"))
sys.path.insert(0, os.path.expanduser("~/.local/lib/python3.10/site-packages"))

from gradio_client import Client

prompt = """{prompt}"""

print("Connecting to FLUX.1-schnell...")
client = Client("black-forest-labs/FLUX.1-schnell")
print("Generating image...")
result = client.predict(
    prompt=prompt,
    seed=0,
    randomize_seed=True,
    width=768,
    height=1344,
    num_inference_steps=4,
    api_name="/infer"
)
print("Result:", result)
src = result[0] if isinstance(result, (list, tuple)) else result
out = "/tmp/flux_out_{idx}.webp"
shutil.copy(src, out)
print("SAVED:" + out)
'''

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("Connecting to server...")
    ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=30)
    sftp = ssh.open_sftp()
    print("Connected!")
    
    # First ensure gradio_client is installed
    print("Installing gradio_client...")
    stdin, stdout, stderr = ssh.exec_command(
        'pip3 install gradio_client -q 2>/dev/null || python3 -m pip install gradio_client -q 2>/dev/null; echo DONE',
        timeout=120
    )
    print(stdout.read().decode().strip())
    print(stderr.read().decode().strip()[:300])
    
    # Test with scene 1
    for i, prompt in enumerate(SCENES):
        out_local = os.path.join(OUTPUT_DIR, f"scene_{i+1:02d}.png")
        if os.path.exists(out_local) and os.path.getsize(out_local) > 10000:
            print(f"Scene {i+1} exists, skipping")
            continue
        
        print(f"\n--- Generating scene {i+1}/10 ---")
        
        # Write script to server
        script_content = REMOTE_SCRIPT_TEMPLATE.replace("{prompt}", prompt.replace('"', '\\"')).replace("{idx}", str(i+1))
        remote_script = f"/tmp/flux_gen_{i+1}.py"
        
        with sftp.open(remote_script, 'w') as f:
            f.write(script_content)
        
        # Execute
        stdin, stdout, stderr = ssh.exec_command(f'python3 {remote_script}', timeout=300)
        out_text = stdout.read().decode()
        err_text = stderr.read().decode()
        print(f"stdout: {out_text.strip()}")
        if err_text.strip():
            print(f"stderr: {err_text.strip()[:300]}")
        
        if "SAVED:" in out_text:
            remote_img = out_text.split("SAVED:")[1].strip()
            sftp.get(remote_img, out_local)
            print(f"Downloaded: {out_local} ({os.path.getsize(out_local)} bytes)")
        else:
            print(f"FAILED scene {i+1}!")
            if i == 0:
                print("First scene failed, aborting.")
                break
        
        time.sleep(2)
    
    sftp.close()
    ssh.close()
    
    # Summary
    generated = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("scene_") and os.path.getsize(os.path.join(OUTPUT_DIR, f)) > 1000]
    print(f"\n=== Generated {len(generated)}/10 images ===")
    for f in sorted(generated):
        print(f"  {f}: {os.path.getsize(os.path.join(OUTPUT_DIR, f))} bytes")

if __name__ == "__main__":
    main()
