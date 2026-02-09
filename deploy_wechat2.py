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

# Check key files
print("=== 查看 Dockerfile 和 docker-compose ===")
run(ssh, "cat ~/openclaw-wechat/wechat-service/Dockerfile")
run(ssh, "cat ~/openclaw-wechat/wechat-service/docker-compose.yaml")
run(ssh, "cat ~/openclaw-wechat/wechat-service/README.md")

# Install Docker
print("\n=== 安装 Docker ===")
run(ssh, "sudo apt-get update -qq && sudo apt-get install -y -qq docker.io docker-compose-plugin", timeout=180)
run(ssh, "sudo systemctl start docker && sudo systemctl enable docker", timeout=30)
run(ssh, "sudo docker --version")

# Start wechat-service
print("\n=== 启动 wechat-service ===")
run(ssh, "cd ~/openclaw-wechat/wechat-service && sudo docker compose up -d", timeout=180)
run(ssh, "sudo docker ps -a")
run(ssh, "sleep 5 && sudo docker compose -f ~/openclaw-wechat/wechat-service/docker-compose.yaml logs --tail=30 2>&1", timeout=30)

# Install Node.js and bridge deps
print("\n=== 安装 Node.js 和 bridge 依赖 ===")
out, _ = run(ssh, "node --version 2>/dev/null || echo NO_NODE")
if 'NO_NODE' in out:
    run(ssh, "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -", timeout=60)
    run(ssh, "sudo apt-get install -y nodejs", timeout=120)
    run(ssh, "node --version && npm --version")

run(ssh, "cat ~/openclaw-wechat/openclaw-wechat/bridge/package.json")
run(ssh, "cd ~/openclaw-wechat/openclaw-wechat/bridge && npm install 2>&1", timeout=120)

# Final status
print("\n=== 最终状态 ===")
run(ssh, "sudo docker ps -a")

ssh.close()
print("\n=== 完成 ===")
