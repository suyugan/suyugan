import sys
content = open('/etc/nginx/sites-enabled/default').read()
block = """
    location /mj/ {
        proxy_pass http://127.0.0.1:8080/mj/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 20M;
    }

"""
if 'location /mj/' not in content:
    content = content.replace('location /videos/', block + 'location /videos/')
    open('/etc/nginx/sites-enabled/default', 'w').write(content)
    print('Added mj location block')
else:
    print('Already exists')
