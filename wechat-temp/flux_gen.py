import subprocess, sys, os
subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--user', 'gradio_client', '-q'])
sys.path.insert(0, os.path.expanduser('~/.local/lib/python3.12/site-packages'))
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
