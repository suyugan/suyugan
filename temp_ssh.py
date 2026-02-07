import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

sftp = ssh.open_sftp()
sftp.put(r'C:\Users\Administrator\.openclaw\workspace\projects\wechat-viewer\server.js', 
         '/home/ubuntu/wechat-viewer/server.js')
sftp.close()
print("Uploaded server.js")

stdin, stdout, stderr = ssh.exec_command('pm2 restart wechat-viewer')
print(stdout.read().decode('utf-8', errors='replace'))
print(stderr.read().decode('utf-8', errors='replace'))
ssh.close()
print("Done!")
