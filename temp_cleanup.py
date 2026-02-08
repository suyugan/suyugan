import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Delete test file
cmd = 'rm -f /home/ubuntu/wechat-viewer/uploads/5c021a42-1a6d-4666-b660-c754554bb8a6/1afdd58e-2d14-4d30-ba7f-e7fc522f94aa.png'
ssh.exec_command(cmd)

# Delete all corrupted files (the 4 broken ones)
corrupted_files = [
    '1ecace05-fccb-46e0-8f68-5bf14a5544e5.png',
    '109ac73c-f334-4a1e-8db8-f424a7c41aa0.png',
    '5dde2278-d7f7-4f9d-aeae-31151462a220.png',
    'e707a3a2-3234-4ff3-ac1d-232baa1e34b0.png',
]
for f in corrupted_files:
    cmd = f'rm -f /home/ubuntu/wechat-viewer/uploads/5c021a42-1a6d-4666-b660-c754554bb8a6/{f}'
    ssh.exec_command(cmd)
    print(f'Deleted: {f}')

print('Cleanup done')
ssh.close()
