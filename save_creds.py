import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Create credentials directory
ssh.exec_command('mkdir -p /home/ubuntu/.credentials')
ssh.exec_command('chmod 700 /home/ubuntu/.credentials')

creds = """# 苏总账号密码存储
# 最后更新: 2026-02-11
# ⚠️ 仅限助手查询使用，勿外泄

## 腾讯云服务器
- IP: 106.55.158.137
- 用户: ubuntu
- 密码: REDACTED_SERVER_PWD

## GitHub
- 用户: suyugan
- Token: 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
- Scopes: repo, workflow
- 过期: 2026-03-10

## 飞书应用 (皮皮虾)
- App ID: cli_a90f5a7ee979dbef
- App Secret: AMnZ3JosdeIamSXn8BBzZcCXCpfpIMV4

## 中转API (林杰)
- Base URL: http://m.laolin.me:3002
- (API Key 存在 openclaw.json 中，REDACTED)

## 域名
- 主域名: weiixxin.com

## USDT地址 (TRC20)
- TLjhZPkH3UW8FLDUyVT21GQ5eL1nzPmEo6
"""

stdin, stdout, stderr = ssh.exec_command('cat > /home/ubuntu/.credentials/accounts.md', bufsize=-1)
stdin.write(creds)
stdin.channel.shutdown_write()
print(stdout.read().decode())

# Set permissions
ssh.exec_command('chmod 600 /home/ubuntu/.credentials/accounts.md')

# Verify
stdin, stdout, stderr = ssh.exec_command('ls -la /home/ubuntu/.credentials/')
print(stdout.read().decode())
ssh.close()
