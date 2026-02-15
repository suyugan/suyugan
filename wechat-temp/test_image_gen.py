import requests

# Test pollinations.ai
url = 'https://image.pollinations.ai/prompt/child%20sitting%20alone%20dark%20corner%20parents%20arguing%20silhouette%20deep%20blue%20tones%20digital%20illustration%20emotional%20anime?width=1080&height=1920&nologo=true'
try:
    r = requests.get(url, timeout=120, allow_redirects=True)
    print(f'Status: {r.status_code}')
    print(f'Size: {len(r.content)}')
    ct = r.headers.get('content-type', '')
    print(f'Content-Type: {ct}')
    if r.status_code == 200 and len(r.content) > 10000:
        with open(r'D:\video-analysis\test_pollinations.png', 'wb') as f:
            f.write(r.content)
        print('Saved test image!')
    else:
        print('Failed:', r.text[:200])
except Exception as e:
    print(f'Error: {e}')

# Also try from server via paramiko
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')
cmd = '''python3 -c "
import urllib.request
url='https://image.pollinations.ai/prompt/child%20alone%20dark%20corner%20blue%20illustration?width=1080&height=1920&nologo=true'
try:
    req = urllib.request.urlopen(url, timeout=60)
    data = req.read()
    print('Server size:', len(data))
    if len(data) > 10000:
        with open('/tmp/test_flux.png','wb') as f:
            f.write(data)
        print('Server saved!')
except Exception as e:
    print('Server error:', e)
"'''
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
