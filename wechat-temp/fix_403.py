import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

cmds = [
    'sudo chmod 755 /home/ubuntu',
    'curl -s -o /dev/null -w "%{http_code}" http://localhost/videos/fuli_v2_hd.mp4'
]
for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print(cmd, '->', stdout.read().decode().strip(), stderr.read().decode().strip())

ssh.close()
