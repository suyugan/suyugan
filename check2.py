import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

cmds = [
    'curl -s -o /dev/null -w "%{http_code}" http://localhost:3002/showcase',
    'curl -s http://localhost:3002/showcase | head -3',
    'curl -s -o /dev/null -w "%{http_code}" http://bm.weiixxin.com/wechat-sync/showcase',
]
for c in cmds:
    _, out, err = ssh.exec_command(c)
    r = out.read().decode().strip()
    print(f'>>> {c[:80]}')
    print(r[:300])
    print()
ssh.close()
