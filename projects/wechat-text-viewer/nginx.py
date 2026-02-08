import paramiko, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=10)

# Check if wechat-text location already exists in nginx config
stdin, stdout, stderr = ssh.exec_command('grep -r "wechat-text" /etc/nginx/ 2>&1', timeout=5)
existing = stdout.read().decode('utf-8', errors='replace')
print(f'Existing config: {existing}')

if 'wechat-text' not in existing:
    # Find the nginx config file and add the location block
    nginx_block = """
    location /wechat-text/ {
        proxy_pass http://127.0.0.1:3001/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
"""
    # Add before the last closing brace of the server block
    cmd = f"""sudo sed -i '/location \\/wechat\\//i\\    location /wechat-text/ {{\\n        proxy_pass http://127.0.0.1:3001/;\\n        proxy_http_version 1.1;\\n        proxy_set_header Upgrade \\$http_upgrade;\\n        proxy_set_header Connection upgrade;\\n        proxy_set_header Host \\$host;\\n        proxy_set_header X-Real-IP \\$remote_addr;\\n        proxy_cache_bypass \\$http_upgrade;\\n    }}' /etc/nginx/sites-enabled/default"""
    
    print(f'\nAdding nginx config...')
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=10)
    print(stdout.read().decode('utf-8', errors='replace'))
    print(stderr.read().decode('utf-8', errors='replace'))
    
    # Test and reload
    stdin, stdout, stderr = ssh.exec_command('sudo nginx -t 2>&1 && sudo nginx -s reload 2>&1', timeout=10)
    result = stdout.read().decode('utf-8', errors='replace')
    print(f'Nginx test+reload: {result}')
    err = stderr.read().decode('utf-8', errors='replace')
    if err: print(f'stderr: {err}')
else:
    print('Config already exists')

ssh.close()
