import paramiko, os, sys
sys.stdout.reconfigure(encoding='utf-8')

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
ssh.connect(HOST, username=USER, password=PASS, timeout=10)
print('SSH OK', flush=True)

def run(cmd):
    print(f'>> {cmd}', flush=True)
    _, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out, flush=True)
    if err: print(f'STDERR: {err}', flush=True)
    return out

# 1. Upload
sftp = ssh.open_sftp()
run(f'mkdir -p {REMOTE_DIR}/db {REMOTE_DIR}/frontend')
for local, remote in FILES.items():
    print(f'Upload {os.path.basename(local)}', flush=True)
    sftp.put(local, remote)
sftp.close()
print('Upload done', flush=True)

# 2. Fix static path and copy
run(f"sed -i \"s|path.join(__dirname, '..', 'frontend')|path.join(__dirname, 'frontend')|\" {REMOTE_DIR}/server.js")
run(f'cp {REMOTE_DIR}/index.html {REMOTE_DIR}/frontend/')

# 3. Install deps (skip optional like nodejieba which needs native build)
run(f'cd {REMOTE_DIR} && npm install --omit=optional 2>&1 | tail -5')

# 4. pm2
run('which pm2 || sudo npm install -g pm2')
run(f'cd {REMOTE_DIR} && pm2 delete wechat-sync 2>/dev/null; pm2 start server.js --name wechat-sync')
run('pm2 save 2>&1')
run('pm2 list')

# 5. Test API
import time; time.sleep(2)
run('curl -s http://127.0.0.1:3002/api/stats')

# 6. Nginx
nginx_file = run('grep -rl "bm.weiixxin.com" /etc/nginx/sites-enabled/ /etc/nginx/conf.d/ 2>/dev/null').strip().split('\n')[0]
print(f'Nginx file: {nginx_file}', flush=True)

if nginx_file:
    content = run(f'cat {nginx_file}')
    if 'wechat-sync' not in content:
        # Insert before last }
        snippet = '    # wechat-sync\\n    location /wechat-sync/ {\\n        proxy_pass http://127.0.0.1:3002/;\\n        proxy_set_header Host \\$host;\\n        proxy_set_header X-Real-IP \\$remote_addr;\\n        proxy_set_header X-Forwarded-For \\$proxy_add_x_forwarded_for;\\n        proxy_set_header X-Forwarded-Proto \\$scheme;\\n    }'
        run(f"sudo sed -i '$i\\{snippet}' {nginx_file}")
        run(f'sudo nginx -t 2>&1')
        run('sudo systemctl reload nginx')
        print('Nginx updated', flush=True)
    else:
        print('wechat-sync already in nginx', flush=True)

# 7. Test POST
run("""curl -s -X POST http://127.0.0.1:3002/api/messages -H "Content-Type: application/json" -d '{"msg_svr_id":"test001","from_user":"test@chatroom","real_sender":"wxid_test","sender_nick":"测试用户","content":"这是一条测试消息","msg_type":1,"create_time":1739174400}'""")
run('curl -s http://127.0.0.1:3002/api/messages?limit=3')

# 8. Test via domain
run('curl -s -o /dev/null -w "%{http_code}" http://bm.weiixxin.com/wechat-sync/')

ssh.close()
print('DONE', flush=True)
