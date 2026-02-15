import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Check if videos location exists
stdin, stdout, stderr = ssh.exec_command('grep -c "videos" /etc/nginx/sites-enabled/default')
count = stdout.read().decode().strip()
print(f'videos mentions: {count}')

if count == '0':
    # Write a small script to add the config
    script = '''#!/bin/bash
sudo sed -i '/^}/i \\    location /videos/ {\\n        alias /home/ubuntu/videos/;\\n        autoindex on;\\n    }' /etc/nginx/sites-enabled/default
sudo nginx -t
sudo nginx -s reload
'''
    stdin, stdout, stderr = ssh.exec_command('echo \'' + script + '\' > /tmp/add_videos.sh && bash /tmp/add_videos.sh')
    print(stdout.read().decode())
    print(stderr.read().decode())
else:
    print('already configured')
    stdin, stdout, stderr = ssh.exec_command('sudo nginx -s reload')
    print(stderr.read().decode())

ssh.close()
