import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

stdin, stdout, stderr = ssh.exec_command('cat /home/ubuntu/wechat-sync/server.js')
js = stdout.read().decode()

# Add sender_avatar to INSERT columns
js = js.replace(
    '(msg_svr_id, from_user, real_sender, sender_nick, content,',
    '(msg_svr_id, from_user, real_sender, sender_nick, sender_avatar, content,'
)
js = js.replace(
    'VALUES (@msg_svr_id, @from_user, @real_sender, @sender_nick, @content,',
    'VALUES (@msg_svr_id, @from_user, @real_sender, @sender_nick, @sender_avatar, @content,'
)

# Add sender_avatar to parameter binding
js = js.replace(
    "sender_nick: msg.sender_nick || '',\n        content:",
    "sender_nick: msg.sender_nick || '',\n        sender_avatar: msg.sender_avatar || '',\n        content:"
)

# Write back
stdin, stdout, stderr = ssh.exec_command('cat > /home/ubuntu/wechat-sync/server.js', bufsize=-1)
stdin.write(js.encode('utf-8'))
stdin.channel.shutdown_write()
print(stderr.read().decode())

# Restart pm2
stdin, stdout, stderr = ssh.exec_command('pm2 restart wechat-sync')
print(stdout.read().decode())

# Verify API still works
import time
time.sleep(2)
stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:3002/api/messages?limit=1')
print("API test:", stdout.read().decode()[:200])

ssh.close()
