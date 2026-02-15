import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')
cmd = 'echo "\n## Volcengine - Jimeng AI\nAK: REDACTED_VOLC_AK\nSK: ZmU3NzE3OGJmMDkwNDgxNWI4MWU5MjBhNTU5MzU0YjY\n" >> /home/ubuntu/.credentials/accounts.md'
stdin, stdout, stderr = ssh.exec_command(cmd)
print(stdout.read().decode(), stderr.read().decode())
ssh.close()
print('done')
