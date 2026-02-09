import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

def run(ssh, cmd, timeout=120):
    print(f"\n>>> {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out)
    if err: print(f"[STDERR] {err}")
    return out, err

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Check main project README and architecture
run(ssh, "cat ~/openclaw-wechat/openclaw-wechat/README.md")
run(ssh, "cat ~/openclaw-wechat/openclaw-wechat/docs/ARCHITECTURE.md")
run(ssh, "cat ~/openclaw-wechat/openclaw-wechat/docs/API.md | head -50")
run(ssh, "cat ~/openclaw-wechat/wechat-service/start.sh")
run(ssh, "cat ~/openclaw-wechat/openclaw-wechat/scripts/start.sh")

# Check docker status - mysql and redis should be running
run(ssh, "sudo docker ps -a")

ssh.close()
