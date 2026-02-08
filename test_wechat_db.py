import sqlite3
import os

# Test each account's MicroMsg.db
accounts = [
    r'C:\Users\Administrator\Documents\WeChat Files\wxid_mqiv7irec7ee21\Msg\MicroMsg.db',
    r'C:\Users\Administrator\Documents\WeChat Files\wxid_izefflwcf2n822\Msg\MicroMsg.db',
    r'C:\Users\Administrator\Documents\WeChat Files\wxid_h1v1an2z78wp12\Msg\MicroMsg.db',
]

for db_path in accounts:
    print(f"\n=== Testing: {db_path} ===")
    print(f"Size: {os.path.getsize(db_path)} bytes")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 10")
        tables = cursor.fetchall()
        print(f"Tables (first 10): {tables}")
        if tables:
            print("Database is NOT encrypted (readable with standard SQLite)")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")
        print("Database is likely ENCRYPTED (SQLCipher)")
