import paramiko, base64, os, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Try SiliconFlow free API (Chinese service, FLUX available)
script = '''
import json, urllib.request, base64, sys

# Register free at siliconflow.cn - but let's try without key first
# Try Cloudflare Workers AI (free)
url = "https://api.cloudflare.com/client/v4/accounts/placeholder/ai/run/@cf/stabilityai/stable-diffusion-xl-base-1.0"

# Actually let's try a completely free approach - use gradio client to call HF Space
try:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'gradio_client', '-q'])
    from gradio_client import Client
    client = Client("black-forest-labs/FLUX.1-schnell")
    result = client.predict(
        prompt="a lonely child sitting in dark corner, parents arguing silhouette background, deep blue tones, digital art, emotional illustration",
        seed=0,
        randomize_seed=True,
        width=1080,
        height=1920,
        num_inference_steps=4,
        api_name="/infer"
    )
    print("RESULT:", result)
except Exception as e:
    print("GRADIO_ERROR:", e)
'''

stdin, stdout, stderr = ssh.exec_command(f'python3 -c """{script}"""')
out = stdout.read().decode()
err = stderr.read().decode()
print("OUT:", out)
if err:
    print("ERR:", err[-500:])
ssh.close()
