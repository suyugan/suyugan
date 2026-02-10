import paramiko, sys, time
sys.stdout.reconfigure(encoding='utf-8')

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=10)

def run(cmd):
    print(f'>> {cmd}', flush=True)
    _, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out, flush=True)
    if err: print(f'ERR: {err}', flush=True)
    return out

# Check pm2 logs for crash
run('pm2 logs wechat-sync --lines 20 --nostream')

# Check if server is actually responding
run('curl -s http://127.0.0.1:3002/api/stats')

# Fix nginx - add to default (not .bak), and revert .bak
run('cat /etc/nginx/sites-enabled/default')

ssh.close()
