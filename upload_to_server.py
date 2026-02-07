import paramiko
import os

# 服务器信息
host = "106.55.158.137"
username = "ubuntu"
password = "REDACTED_SERVER_PWD"

# 本地文件
local_files = [
    ("C:\\Users\\Administrator\\.openclaw\\workspace\\bookmarks.html", "/tmp/bookmarks.html"),
]

# 连接
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(host, username=username, password=password)

sftp = ssh.open_sftp()

# 上传文件
for local, remote in local_files:
    print(f"Uploading {local} -> {remote}")
    sftp.put(local, remote)
    print(f"  Done!")

sftp.close()

# 复制到正确位置并设置权限
commands = [
    "sudo cp /tmp/bookmarks.html /var/www/html/bookmarks/index.html",
    "sudo chmod 644 /var/www/html/bookmarks/index.html",
    "ls -la /var/www/html/bookmarks/",
]

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out:
        print(out)
    if err:
        print(f"  stderr: {err}")

ssh.close()
print("\nDone!")
