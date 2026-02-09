import paramiko
import time

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

# Step 1: Clone repo
print("=" * 60)
print("步骤1: 克隆项目")
run(ssh, "rm -rf ~/openclaw-wechat && git clone https://github.com/laolin5564/openclaw-wechat ~/openclaw-wechat", timeout=60)

# Step 2: Check wechat-service directory
print("=" * 60)
print("步骤2: 检查 wechat-service 目录")
run(ssh, "ls -la ~/openclaw-wechat/wechat-service/ 2>/dev/null || echo 'wechat-service目录不存在'")
run(ssh, "find ~/openclaw-wechat/wechat-service -name 'Dockerfile*' -o -name 'docker-compose*' -o -name '*.go' -o -name 'go.mod' 2>/dev/null || echo '无相关文件'")
run(ssh, "file ~/openclaw-wechat/wechat-service/* 2>/dev/null || echo '无法检查文件类型'")

# Step 3: Check overall project structure
print("=" * 60)
print("步骤3: 项目整体结构")
run(ssh, "find ~/openclaw-wechat -maxdepth 3 -type f | head -80")
run(ssh, "cat ~/openclaw-wechat/README.md 2>/dev/null | head -100")

# Step 4: Check for Docker files at root
print("=" * 60)
print("步骤4: 检查Docker相关文件")
run(ssh, "find ~/openclaw-wechat -name 'Dockerfile*' -o -name 'docker-compose*' -o -name 'docker*' 2>/dev/null")

# Step 5: Install Docker if needed
print("=" * 60)
print("步骤5: 安装Docker")
run(ssh, "curl -fsSL https://get.docker.com | sudo sh", timeout=180)
run(ssh, "sudo usermod -aG docker ubuntu")
run(ssh, "docker --version")

# Step 6: Start wechat-service if docker-compose exists
print("=" * 60)
print("步骤6: 启动 wechat-service")
out, _ = run(ssh, "find ~/openclaw-wechat -name 'docker-compose*' -o -name 'compose.yaml' -o -name 'compose.yml' 2>/dev/null")
if out.strip():
    for f in out.strip().split('\n'):
        d = '/'.join(f.strip().split('/')[:-1])
        print(f"找到compose文件: {f.strip()}, 在目录: {d}")
        run(ssh, f"cd {d} && sudo docker compose up -d", timeout=120)
else:
    print("无docker-compose文件，尝试查看wechat-service内容")
    run(ssh, "ls -la ~/openclaw-wechat/wechat-service/")
    run(ssh, "cat ~/openclaw-wechat/wechat-service/Dockerfile 2>/dev/null")

# Step 7: Bridge npm install
print("=" * 60)
print("步骤7: 安装 bridge 依赖")
run(ssh, "which node && node --version || echo 'Node.js未安装'")
out, _ = run(ssh, "which node")
if not out.strip() or 'not found' in out:
    print("安装Node.js...")
    run(ssh, "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -", timeout=60)
    run(ssh, "sudo apt-get install -y nodejs", timeout=120)
    run(ssh, "node --version && npm --version")

run(ssh, "ls ~/openclaw-wechat/bridge/ 2>/dev/null || echo 'bridge目录不存在'")
run(ssh, "cd ~/openclaw-wechat/bridge && npm install 2>&1", timeout=120)

# Step 8: Check running services
print("=" * 60)
print("步骤8: 检查服务状态")
run(ssh, "sudo docker ps -a 2>/dev/null")
run(ssh, "sudo docker compose -f ~/openclaw-wechat/wechat-service/docker-compose.yml logs --tail=20 2>/dev/null || echo '无compose日志'")

ssh.close()
print("\n" + "=" * 60)
print("部署脚本执行完毕")
