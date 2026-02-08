import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Check the uploaded test file
cmd = 'file /home/ubuntu/wechat-viewer/uploads/5c021a42-1a6d-4666-b660-c754554bb8a6/1afdd58e-2d14-4d30-ba7f-e7fc522f94aa.png'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8'))

# Check its header
cmd = 'xxd /home/ubuntu/wechat-viewer/uploads/5c021a42-1a6d-4666-b660-c754554bb8a6/1afdd58e-2d14-4d30-ba7f-e7fc522f94aa.png | head -2'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode('utf-8'))

ssh.close()
