import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=30)

cmds = [
    'sudo apt-get update -qq && sudo apt-get install -y -qq python3-pip 2>&1 | tail -3',
    'python3 -m pip install gradio_client 2>&1 | tail -5',
    'python3 -c "import gradio_client; print(gradio_client.__version__)"',
]
for cmd in cmds:
    print(f'\n>>> {cmd}')
    _, stdout, stderr = ssh.exec_command(cmd, timeout=300)
    print(stdout.read().decode().strip())
    e = stderr.read().decode().strip()
    if e: print(f'ERR: {e[:500]}')
ssh.close()
print("\nDone!")
