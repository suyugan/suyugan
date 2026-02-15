import paramiko
import os

host = '106.55.158.137'
user = 'ubuntu'
pwd = 'REDACTED_SERVER_PWD'
local_base = r'C:\Users\Administrator\.openclaw\workspace\skills\douyin-clone'
remote_base = '/home/ubuntu/douyin-clone'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=user, password=pwd)
sftp = ssh.open_sftp()

# Create dirs
for d in [remote_base, f'{remote_base}/scripts', f'{remote_base}/references']:
    try:
        sftp.mkdir(d)
        print(f'创建目录: {d}')
    except IOError:
        print(f'目录已存在: {d}')

# Upload scripts/*.py
for f in os.listdir(os.path.join(local_base, 'scripts')):
    if f.endswith('.py'):
        local = os.path.join(local_base, 'scripts', f)
        remote = f'{remote_base}/scripts/{f}'
        sftp.put(local, remote)
        print(f'上传: {f} -> {remote}')

# Upload SKILL.md
sftp.put(os.path.join(local_base, 'SKILL.md'), f'{remote_base}/SKILL.md')
print('上传: SKILL.md')

# Upload references/
for f in os.listdir(os.path.join(local_base, 'references')):
    local = os.path.join(local_base, 'references', f)
    remote = f'{remote_base}/references/{f}'
    sftp.put(local, remote)
    print(f'上传: references/{f}')

# List uploaded files
print('\n--- 服务器文件列表 ---')
stdin, stdout, stderr = ssh.exec_command(f'find {remote_base} -type f')
for line in stdout.read().decode().strip().split('\n'):
    print(line)

sftp.close()
ssh.close()
print('\n✅ 全部上传完成！')
