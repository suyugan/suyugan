import paramiko
import os
import stat

# 服务器信息
host = "106.55.158.137"
username = "ubuntu"
password = "REDACTED_SERVER_PWD"

# 本地项目目录
local_project = r"C:\Users\Administrator\.openclaw\workspace\projects\wechat-viewer"
remote_project = "/home/ubuntu/wechat-viewer"

# 需要上传的文件（排除 node_modules 和 uploads）
files_to_upload = [
    "server.js",
    "package.json",
    "package-lock.json",
    "public/index.html",
]

def mkdir_p(sftp, remote_directory):
    """递归创建远程目录"""
    if remote_directory == '/':
        sftp.chdir('/')
        return
    try:
        sftp.chdir(remote_directory)
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip('/'))
        mkdir_p(sftp, dirname)
        try:
            sftp.mkdir(basename)
        except:
            pass
        sftp.chdir(basename)

# 连接
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)

sftp = ssh.open_sftp()

# 创建目录
print(f"Creating remote directory: {remote_project}")
mkdir_p(sftp, remote_project)
sftp.chdir('/')

# 上传文件
for f in files_to_upload:
    local_path = os.path.join(local_project, f)
    remote_path = f"{remote_project}/{f}"
    
    # 确保远程目录存在
    remote_dir = os.path.dirname(remote_path)
    mkdir_p(sftp, remote_dir)
    sftp.chdir('/')
    
    if os.path.exists(local_path):
        print(f"Uploading: {f}")
        sftp.put(local_path, remote_path)
    else:
        print(f"Skipping (not found): {f}")

sftp.close()

# 在服务器上安装依赖和配置
commands = [
    # 检查 Node.js
    "node -v || (curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs)",
    
    # 安装依赖
    f"cd {remote_project} && npm install",
    
    # 创建 data 和 uploads 目录
    f"mkdir -p {remote_project}/data {remote_project}/uploads",
    
    # 安装 pm2
    "sudo npm install -g pm2 2>/dev/null || true",
    
    # 停止旧进程
    "pm2 delete wechat-viewer 2>/dev/null || true",
    
    # 启动应用
    f"cd {remote_project} && pm2 start server.js --name wechat-viewer",
    
    # 保存 pm2 配置
    "pm2 save",
    
    # 设置开机启动
    "sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u ubuntu --hp /home/ubuntu 2>/dev/null || true",
]

for cmd in commands:
    print(f"\n>>> {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out)
    if err and 'npm WARN' not in err:
        print(f"stderr: {err}")

# 配置 nginx
nginx_config = """
server {
    listen 80;
    server_name _;
    
    # bookmarks 红包码页面
    location /bookmarks {
        alias /var/www/html/bookmarks;
        index index.html;
    }
    
    # wechat-viewer 反向代理
    location /wechat {
        rewrite ^/wechat(/.*)$ $1 break;
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
    
    # 默认页面
    location / {
        root /var/www/html;
        index index.html;
    }
}
"""

# 写入 nginx 配置
print("\n>>> Writing nginx config...")
stdin, stdout, stderr = ssh.exec_command(f"echo '{nginx_config}' | sudo tee /etc/nginx/sites-available/default")
stdout.read()

# 测试并重载 nginx
print(">>> Testing and reloading nginx...")
stdin, stdout, stderr = ssh.exec_command("sudo nginx -t && sudo systemctl reload nginx")
out = stdout.read().decode()
err = stderr.read().decode()
print(out if out else err)

# 检查状态
print("\n>>> Checking pm2 status...")
stdin, stdout, stderr = ssh.exec_command("pm2 list")
print(stdout.read().decode())

ssh.close()
print("\n=== Deployment Complete! ===")
print(f"Bookmarks: http://{host}/bookmarks/")
print(f"WeChat Viewer: http://{host}/wechat/")
