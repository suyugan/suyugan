#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import paramiko, json

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Upload script via SFTP
sftp = ssh.open_sftp()
with sftp.open('/tmp/update_title.py', 'wb') as f:
    with open(r'C:\Users\Administrator\.openclaw\workspace\wechat-temp\update_title.py', 'rb') as local:
        f.write(local.read())
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/update_title.py')
print(stdout.read().decode())
err = stderr.read().decode()
if err:
    print('STDERR:', err)
ssh.close()
