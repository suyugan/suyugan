import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')
stdin, stdout, stderr = ssh.exec_command('cat /home/ubuntu/.credentials/accounts.md')
print(stdout.read().decode())
ssh.close()
