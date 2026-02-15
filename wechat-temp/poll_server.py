import paramiko, time
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=30)

# Poll log every 30 seconds
for i in range(10):
    _, stdout, _ = ssh.exec_command('cat /tmp/flux_test.log 2>/dev/null', timeout=10)
    log = stdout.read().decode().strip()
    print(f"[{i*30}s] {log}")
    
    if "SAVED:" in log or "Error" in log or "Traceback" in log:
        break
    
    _, stdout, _ = ssh.exec_command('ps aux | grep flux_test.py | grep -v grep | wc -l', timeout=10)
    count = stdout.read().decode().strip()
    if count == "0":
        print("Process finished!")
        break
    
    time.sleep(30)

ssh.close()
