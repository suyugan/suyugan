import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=10)

def run(cmd, timeout=120):
    print(f'>> {cmd}', flush=True)
    _, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out, flush=True)
    if err: print(f'ERR: {err}', flush=True)
    return out

# Check if build tools exist
run('which gcc make python3')
run('sudo apt-get install -y build-essential python3 2>&1 | tail -5')

# Clean reinstall better-sqlite3
run('cd /home/ubuntu/wechat-sync && rm -rf node_modules/better-sqlite3 && npm install better-sqlite3 2>&1 | tail -15')

# Restart
run('pm2 restart wechat-sync')
time.sleep(3)
run('pm2 logs wechat-sync --lines 5 --nostream')
run('curl -s http://127.0.0.1:3002/api/stats')

ssh.close()
print('DONE', flush=True)
