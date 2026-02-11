import paramiko, sys, json
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Check a few messages for any avatar/head info
stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:3002/api/messages?limit=3')
data = json.loads(stdout.read().decode())
for m in data['data']:
    print(f"sender: {m.get('sender_nick')} | real_sender: {m.get('real_sender')}")
    # Check if content has any img/head info
    c = m.get('content','')
    if 'qlogo' in c or 'mmhead' in c or 'headimg' in c:
        print("  HAS AVATAR INFO!")
    print(f"  keys: {list(m.keys())}")
    print()

# Check DB schema
stdin, stdout, stderr = ssh.exec_command('sqlite3 /home/ubuntu/wechat-sync/data/messages.db ".schema messages"')
print("Schema:", stdout.read().decode())
ssh.close()
