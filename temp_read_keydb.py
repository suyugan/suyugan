import sys, sqlite3
sys.stdout.reconfigure(encoding='utf-8')

path = r'C:\Users\Administrator\xwechat_files\all_users\login\wxid_mqiv7irec7ee21\key_info.db'
conn = sqlite3.connect(path)
cur = conn.cursor()

# List tables
tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print(f'Tables: {tables}')

for t in tables:
    tname = t[0]
    cols = cur.execute(f'PRAGMA table_info({tname})').fetchall()
    print(f'\nTable {tname}: {[c[1] for c in cols]}')
    rows = cur.execute(f'SELECT * FROM {tname}').fetchall()
    print(f'  Rows: {len(rows)}')
    for r in rows[:3]:
        row_display = []
        for val in r:
            if isinstance(val, bytes):
                row_display.append(f'bytes({len(val)})={val[:64].hex()}')
            else:
                row_display.append(repr(val))
        print(f'  {row_display}')

conn.close()
