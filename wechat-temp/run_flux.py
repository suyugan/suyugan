import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

sftp = ssh.open_sftp()
with sftp.open('/tmp/flux_gen.py', 'wb') as f:
    with open(r'C:\Users\Administrator\.openclaw\workspace\wechat-temp\flux_gen.py', 'rb') as local:
        f.write(local.read())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/flux_gen.py', timeout=300)
out = stdout.read().decode()
err = stderr.read().decode()
print("OUT:", out)
if err:
    print("ERR:", err[-1000:])
ssh.close()
