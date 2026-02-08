# -*- coding: utf-8 -*-
import sqlite3
import os
import json

# Step 1: Check xInfo.db (might be unencrypted)
accounts = ['wxid_izefflwcf2n822', 'wxid_mqiv7irec7ee21', 'wxid_h1v1an2z78wp12']
for acc in accounts:
    xinfo_path = f'C:/Users/Administrator/Documents/WeChat Files/{acc}/Msg/xInfo.db'
    if os.path.exists(xinfo_path):
        try:
            conn = sqlite3.connect(xinfo_path)
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
            tables = cursor.fetchall()
            print(f'{acc} xInfo.db tables: {tables}')
            for t in tables:
                cursor.execute(f'SELECT * FROM {t[0]} LIMIT 5')
                rows = cursor.fetchall()
                print(f'  {t[0]}: {rows[:3]}')
            conn.close()
        except Exception as e:
            print(f'{acc} xInfo.db error: {e}')

# Step 2: Check if MicroMsg.db is encrypted
for acc in accounts:
    db_path = f'C:/Users/Administrator/Documents/WeChat Files/{acc}/Msg/MicroMsg.db'
    if os.path.exists(db_path):
        # Read first 16 bytes to check if encrypted
        with open(db_path, 'rb') as f:
            header = f.read(16)
        if header[:6] == b'SQLite':
            print(f'{acc} MicroMsg.db: NOT encrypted (plain SQLite)')
        else:
            print(f'{acc} MicroMsg.db: ENCRYPTED (header: {header[:16].hex()})')
        print(f'  Size: {os.path.getsize(db_path)} bytes')
        print(f'  Modified: {os.path.getmtime(db_path)}')
