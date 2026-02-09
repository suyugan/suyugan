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

# Configure Docker mirror
print("=== 配置 Docker 镜像加速器 ===")
run(ssh, """sudo mkdir -p /etc/docker && sudo tee /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me",
    "https://docker.m.daocloud.io"
  ]
}
EOF""")
run(ssh, "sudo systemctl daemon-reload && sudo systemctl restart docker")

# Retry docker compose
print("\n=== 重新启动 wechat-service ===")
run(ssh, "cd ~/openclaw-wechat/wechat-service && sudo docker compose up -d", timeout=300)
run(ssh, "sleep 20 && sudo docker ps -a")
run(ssh, "sudo docker compose -f ~/openclaw-wechat/wechat-service/docker-compose.yaml logs --tail=50 2>&1", timeout=30)

ssh.close()
print("\n=== 完成 ===")
