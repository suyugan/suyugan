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

# Install Docker via official script
print("=== 用官方脚本安装 Docker ===")
run(ssh, "curl -fsSL https://get.docker.com -o /tmp/get-docker.sh && sudo sh /tmp/get-docker.sh", timeout=300)
run(ssh, "sudo docker --version")
run(ssh, "sudo usermod -aG docker ubuntu")

# Start wechat-service
print("\n=== 启动 wechat-service (docker compose) ===")
run(ssh, "cd ~/openclaw-wechat/wechat-service && sudo docker compose up -d", timeout=300)
run(ssh, "sleep 10 && sudo docker ps -a")
run(ssh, "sudo docker compose -f ~/openclaw-wechat/wechat-service/docker-compose.yaml logs --tail=50 2>&1", timeout=30)

ssh.close()
print("\n=== 完成 ===")
