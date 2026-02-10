"""部署微信群聊分析平台到腾讯云"""
import paramiko
import os

HOST = '106.55.158.137'
USER = 'ubuntu'
PASS = 'REDACTED_SERVER_PWD'
REMOTE_DIR = '/home/ubuntu/wechat-sync'

FILES = {
    r'D:\wechat-plugin-dev\server\server.js': f'{REMOTE_DIR}/server.js',
    r'D:\wechat-plugin-dev\server\package.json': f'{REMOTE_DIR}/package.json',
    r'D:\wechat-plugin-dev\frontend\index.html': f'{REMOTE_DIR}/index.html',
}

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)
print('✅ SSH连接成功')

# Upload files
sftp = ssh.open_sftp()
def run(cmd):
    print(f'$ {cmd}')
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out)
    if err: print(err)
    return out, err

run(f'mkdir -p {REMOTE_DIR}/db {REMOTE_DIR}/frontend')

for local, remote in FILES.items():
    print(f'上传 {os.path.basename(local)} ...')
    sftp.put(local, remote)
print('✅ 文件上传完成')

# Fix static path: change '../frontend' to 'frontend'
run(f"sed -i \"s|path.join(__dirname, '..', 'frontend')|path.join(__dirname, 'frontend')|\" {REMOTE_DIR}/server.js")

# Copy index.html to frontend/
run(f'cp {REMOTE_DIR}/index.html {REMOTE_DIR}/frontend/')

# Install deps
run(f'cd {REMOTE_DIR} && npm install --omit=optional 2>&1')

# Check pm2
out, _ = run('which pm2')
if not out.strip():
    run('sudo npm install -g pm2')

# Start with pm2
run(f'cd {REMOTE_DIR} && pm2 delete wechat-sync 2>/dev/null; pm2 start server.js --name wechat-sync && pm2 save')

# Check it's running
run('pm2 list')
run('sleep 2 && curl -s http://127.0.0.1:3002/api/stats')

# Nginx config
print('\n--- 配置Nginx ---')
out, _ = run('ls /etc/nginx/sites-enabled/')
print(f'sites-enabled: {out}')

# Read existing config to find the right file
out, _ = run('grep -rl "bm.weiixxin.com" /etc/nginx/sites-enabled/ /etc/nginx/conf.d/ 2>/dev/null')
nginx_file = out.strip().split('\n')[0] if out.strip() else ''
print(f'找到配置文件: {nginx_file}')

if nginx_file:
    out, _ = run(f'cat {nginx_file}')
    print(f'--- 当前Nginx配置 ---\n{out[:2000]}')

    # Check if wechat-sync location already exists
    if 'wechat-sync' not in out:
        # Add location before the last closing brace of the server block
        nginx_snippet = """
    # 微信群聊分析平台
    location /wechat-sync/ {
        proxy_pass http://127.0.0.1:3002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
"""
        # Use sed to insert before the last }
        # Find line number of last }
        run(f"sudo sed -i '/^}}/i\\    # 微信群聊分析平台\\n    location /wechat-sync/ {{\\n        proxy_pass http://127.0.0.1:3002/;\\n        proxy_set_header Host $host;\\n        proxy_set_header X-Real-IP $remote_addr;\\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\\n        proxy_set_header X-Forwarded-Proto $scheme;\\n    }}' {nginx_file}")
        
        run(f'cat {nginx_file}')
        run('sudo nginx -t')
        run('sudo systemctl reload nginx')
        print('✅ Nginx配置已更新')
    else:
        print('⚠️ wechat-sync location已存在，跳过')

# Test API
print('\n--- 测试API ---')
run("""curl -s -X POST http://127.0.0.1:3002/api/messages -H "Content-Type: application/json" -d '{"msg_svr_id":"test001","from_user":"test@chatroom","real_sender":"wxid_test","sender_nick":"测试用户","content":"这是一条测试消息","msg_type":1,"create_time":1739174400}'""")
run('curl -s http://127.0.0.1:3002/api/messages?limit=5')

# Test via domain
run('curl -s -o /dev/null -w "%{http_code}" http://bm.weiixxin.com/wechat-sync/')

sftp.close()
ssh.close()
print('\n✅ 部署完成！')
print('📊 访问地址: http://bm.weiixxin.com/wechat-sync/')
