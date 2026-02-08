import sqlite3
import os
import glob

# Read xInfo.db (not encrypted!)
print("=== xInfo.db contents ===")
for wxid in ['wxid_mqiv7irec7ee21', 'wxid_izefflwcf2n822', 'wxid_h1v1an2z78wp12']:
    db_path = rf'C:\Users\Administrator\Documents\WeChat Files\{wxid}\Msg\xInfo.db'
    if os.path.exists(db_path):
        print(f"\n--- {wxid} ---")
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"Tables: {tables}")
            for table in tables:
                tname = table[0]
                cursor.execute(f"SELECT * FROM {tname} LIMIT 20")
                rows = cursor.fetchall()
                cols = [desc[0] for desc in cursor.description]
                print(f"\nTable '{tname}' columns: {cols}")
                for row in rows:
                    # Show data, but truncate long binary blobs
                    display_row = []
                    for v in row:
                        if isinstance(v, bytes) and len(v) > 100:
                            display_row.append(f"<blob {len(v)} bytes>")
                        elif isinstance(v, bytes):
                            display_row.append(v.hex())
                        else:
                            display_row.append(v)
                    print(f"  {display_row}")
            conn.close()
        except Exception as e:
            print(f"Error: {e}")

# Find WeChat.exe
print("\n\n=== Looking for WeChat.exe ===")
for drive in ['C:', 'D:']:
    for root, dirs, files in os.walk(drive + '\\'):
        # Skip deep/slow dirs
        if any(skip in root.lower() for skip in ['windows', 'appdata', '.git', 'node_modules', 'recycle']):
            dirs.clear()
            continue
        for f in files:
            if f.lower() == 'wechat.exe':
                full = os.path.join(root, f)
                print(f"Found: {full} ({os.path.getsize(full)} bytes)")
        # Don't go too deep
        if root.count('\\') > 5:
            dirs.clear()
