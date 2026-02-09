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

# Start MySQL and Redis only (skip app build since no Go source)
print("=== 单独启动 MySQL 和 Redis ===")
run(ssh, """cd ~/openclaw-wechat/wechat-service && sudo docker run -d \
  --name my-mysql \
  --network host \
  -e MYSQL_ROOT_PASSWORD='lln@2022' \
  -e MYSQL_DATABASE='lln-robot2' \
  -v $(pwd)/init.sql:/docker-entrypoint-initdb.d/init.sql \
  mysql:8.0 \
  --character-set-server=utf8mb4 \
  --collation-server=utf8mb4_unicode_ci \
  --default-authentication-plugin=mysql_native_password""", timeout=120)

run(ssh, """sudo docker run -d \
  --name my-redis \
  --network host \
  redis:6.2 \
  redis-server --requirepass 'lln@2022'""", timeout=60)

run(ssh, "sleep 5 && sudo docker ps -a")

ssh.close()
print("\n=== 完成 ===")
