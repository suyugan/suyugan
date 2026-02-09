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

# Use Aliyun mirror for Docker
print("=== 用阿里云镜像安装 Docker ===")
cmds = [
    "sudo apt-get update -qq",
    "sudo apt-get install -y -qq ca-certificates curl gnupg",
    "sudo install -m 0755 -d /etc/apt/keyrings",
    "curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes",
    "sudo chmod a+r /etc/apt/keyrings/docker.gpg",
    'echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null',
    "sudo apt-get update -qq",
    "sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin",
    "sudo docker --version",
    "sudo docker compose version",
]
for cmd in cmds:
    run(ssh, cmd, timeout=180)

# Start services
print("\n=== 启动 wechat-service ===")
run(ssh, "cd ~/openclaw-wechat/wechat-service && sudo docker compose up -d", timeout=300)
run(ssh, "sleep 15 && sudo docker ps -a")
run(ssh, "sudo docker compose -f ~/openclaw-wechat/wechat-service/docker-compose.yaml logs --tail=50 2>&1", timeout=30)

ssh.close()
print("\n=== 完成 ===")
