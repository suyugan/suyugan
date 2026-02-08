import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Check which of the latest files are corrupted
cmd = 'ls -lt /home/ubuntu/wechat-viewer/uploads/5c021a42-1a6d-4666-b660-c754554bb8a6/*.png | head -10'
stdin, stdout, stderr = ssh.exec_command(cmd)
print('Latest files by modification time:')
print(stdout.read().decode('utf-8'))

# Check specific files
files_to_check = [
    '1ecace05-fccb-46e0-8f68-5bf14a5544e5.png',
    '109ac73c-f334-4a1e-8db8-f424a7c41aa0.png',
    '5dde2278-d7f7-4f9d-aeae-31151462a220.png',
    'e707a3a2-3234-4ff3-ac1d-232baa1e34b0.png',
]
print('\nChecking specific files:')
for f in files_to_check:
    cmd = f'file /home/ubuntu/wechat-viewer/uploads/5c021a42-1a6d-4666-b660-c754554bb8a6/{f}'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(stdout.read().decode('utf-8').strip())

ssh.close()
