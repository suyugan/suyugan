"""Upload a test script to server and run it, capturing output to file"""
import paramiko
import os
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=30)
sftp = ssh.open_sftp()

# Write test script
test_script = '''#!/usr/bin/env python3
import sys, os, shutil
sys.path.insert(0, os.path.expanduser("~/.local/lib/python3.12/site-packages"))

print("Importing gradio_client...", flush=True)
from gradio_client import Client

print("Connecting to FLUX.1-schnell...", flush=True)
client = Client("black-forest-labs/FLUX.1-schnell")

print("Generating test image...", flush=True)
result = client.predict(
    prompt="a lonely child in dark blue room, anime style, digital painting, emotional",
    seed=0,
    randomize_seed=True,
    width=768,
    height=1344,
    num_inference_steps=4,
    api_name="/infer"
)
print(f"Result: {result}", flush=True)
src = result[0] if isinstance(result, (list, tuple)) else result
out = "/tmp/flux_test.webp"
shutil.copy(src, out)
print(f"SAVED:{out}", flush=True)
print(f"Size: {os.path.getsize(out)}", flush=True)
'''

with sftp.open('/tmp/flux_test.py', 'w') as f:
    f.write(test_script)

print("Script uploaded, running...")
# Run with output redirected to file so we can check later
_, stdout, stderr = ssh.exec_command(
    'python3 /tmp/flux_test.py > /tmp/flux_test.log 2>&1; echo EXIT:$?',
    timeout=300
)
result = stdout.read().decode().strip()
print(f"Exit: {result}")

# Read log
_, stdout, _ = ssh.exec_command('cat /tmp/flux_test.log')
log = stdout.read().decode()
print(f"Log:\n{log}")

# Check if image exists
if "SAVED:" in log:
    img_path = log.split("SAVED:")[1].split("\n")[0].strip()
    local_path = r"D:\video-analysis\output\原生家庭\images\test_flux.webp"
    sftp.get(img_path, local_path)
    print(f"Downloaded to {local_path} ({os.path.getsize(local_path)} bytes)")

sftp.close()
ssh.close()
