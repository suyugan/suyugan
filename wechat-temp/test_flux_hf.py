import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

script = r"""
import subprocess, sys
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gradio_client', '-q'], stderr=subprocess.DEVNULL)
from gradio_client import Client
client = Client("black-forest-labs/FLUX.1-schnell")
result = client.predict(
    prompt="a lonely child sitting in dark corner hugging knees, parents arguing silhouette in background, deep blue indigo tones, digital painting, emotional, cinematic lighting, anime illustration style",
    seed=0,
    randomize_seed=True,
    width=1080,
    height=1920,
    num_inference_steps=4,
    api_name="/infer"
)
print("RESULT:", result)
"""

stdin, stdout, stderr = ssh.exec_command(f'python3 -c {repr(script)}', timeout=300)
out = stdout.read().decode()
err = stderr.read().decode()
print("OUT:", out)
if err:
    print("ERR:", err[-800:])
ssh.close()
