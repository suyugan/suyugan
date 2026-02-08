import sys, os
sys.stdout.reconfigure(encoding='utf-8')

base = r'C:\Users\Administrator\xwechat_files\wxid_mqiv7irec7ee21_620c\db_storage'

# Check each db folder
for folder in ['message', 'contact', 'general']:
    full = os.path.join(base, folder)
    if os.path.exists(full):
        for f in os.listdir(full):
            if f.endswith('.db'):
                fp = os.path.join(full, f)
                with open(fp, 'rb') as fh:
                    header = fh.read(16)
                size = os.path.getsize(fp)
                is_sqlite = header[:6] == b'SQLite'
                print(f'{folder}/{f}: {size//1024}KB | {"SQLite" if is_sqlite else "Encrypted"} | {header[:8].hex()}')
