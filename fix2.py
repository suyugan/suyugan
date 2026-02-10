import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=10)

def run(cmd):
    print(f'>> {cmd}', flush=True)
    _, stdout, stderr = ssh.exec_command(cmd, timeout=120)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out, flush=True)
    if err: print(f'ERR: {err}', flush=True)
    return out

# 1. Fix better-sqlite3: rebuild native module
run('cd /home/ubuntu/wechat-sync && npm rebuild better-sqlite3 2>&1 | tail -10')

# 2. Restart pm2
run('cd /home/ubuntu/wechat-sync && pm2 restart wechat-sync')
import time; time.sleep(3)
run('pm2 logs wechat-sync --lines 5 --nostream')
run('curl -s http://127.0.0.1:3002/api/stats')

# 3. Fix nginx - add to default (not .bak)
# Also revert .bak changes
run("sudo sed -i '/wechat-sync/,/}/d' /etc/nginx/sites-enabled/default.bak")

# Add to default
nginx_default = run('cat /etc/nginx/sites-enabled/default')
if 'wechat-sync' not in nginx_default:
    run("""sudo sed -i '/^}/i\\    # wechat-sync\\n    location /wechat-sync/ {\\n        proxy_pass http://127.0.0.1:3002/;\\n        proxy_set_header Host $host;\\n        proxy_set_header X-Real-IP $remote_addr;\\n        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\\n        proxy_set_header X-Forwarded-Proto $scheme;\\n    }' /etc/nginx/sites-enabled/default""")
    run('cat /etc/nginx/sites-enabled/default')
    run('sudo nginx -t 2>&1')
    run('sudo systemctl reload nginx')

# 4. Test
time.sleep(1)
run("""curl -s -X POST http://127.0.0.1:3002/api/messages -H "Content-Type: application/json" -d '{"msg_svr_id":"test001","from_user":"test@chatroom","real_sender":"wxid_test","sender_nick":"测试用户","content":"这是一条测试消息","msg_type":1,"create_time":1739174400}'""")
run('curl -s http://127.0.0.1:3002/api/messages?limit=3')
run('curl -s -o /dev/null -w "%{http_code}" http://bm.weiixxin.com/wechat-sync/')

ssh.close()
print('DONE', flush=True)
