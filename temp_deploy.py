import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Upload the updated server.js
sftp = ssh.open_sftp()
sftp.put(r'C:\Users\Administrator\.openclaw\workspace\projects\wechat-viewer\server.js', 
         '/home/ubuntu/wechat-viewer/server.js')
sftp.close()
print('Uploaded server.js')

# Restart PM2
stdin, stdout, stderr = ssh.exec_command('pm2 restart wechat-viewer')
import time
time.sleep(2)
print('Restarted PM2')

# Check status
stdin, stdout, stderr = ssh.exec_command('pm2 status wechat-viewer --no-color')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()
print('Done!')
