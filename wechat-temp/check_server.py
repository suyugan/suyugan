import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=30)

# Check if the script is still running, and check log
cmds = [
    'ps aux | grep flux_test | grep -v grep',
    'cat /tmp/flux_test.log 2>/dev/null || echo "NO LOG"',
]
for cmd in cmds:
    print(f'>>> {cmd}')
    _, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode().strip())
ssh.close()
