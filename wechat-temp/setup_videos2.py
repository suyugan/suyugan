import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

conf = """location /videos/ {
    alias /home/ubuntu/videos/;
    autoindex on;
}
"""
sftp = ssh.open_sftp()
with sftp.open('/tmp/videos.conf', 'w') as f:
    f.write(conf)
sftp.close()

cmds = [
    "sudo cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.bak",
    "sudo python3 -c \"c=open('/etc/nginx/sites-enabled/default').read(); i=c.rfind('}'); open('/tmp/new_default','w').write(c[:i]+'\\n'+open('/tmp/videos.conf').read()+'\\n'+c[i:])\"",
    "sudo cp /tmp/new_default /etc/nginx/sites-enabled/default",
    "sudo nginx -t",
    "sudo nginx -s reload"
]
for cmd in cmds:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out: print(out)
    if err: print(err)

ssh.close()
