import paramiko, os, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = '106.55.158.137'
USER = 'ubuntu'
PASS = 'REDACTED_SERVER_PWD'
REMOTE_DIR = '/home/ubuntu/wechat-text-viewer'
LOCAL_DIR = r'C:\Users\Administrator\.openclaw\workspace\projects\wechat-text-viewer'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USER, password=PASS)

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode('utf-8', errors='replace')
    err = stderr.read().decode('utf-8', errors='replace')
    if out: print(f'[OUT] {out[:500]}')
    if err: print(f'[ERR] {err[:500]}')
    return out

# Create dirs
run(f'mkdir -p {REMOTE_DIR}/public {REMOTE_DIR}/uploads')
run(f'rm -f {REMOTE_DIR}/messages.db')

# Upload files via SFTP
sftp = ssh.open_sftp()

files_to_upload = [
    ('server.js', 'server.js'),
    ('public/index.html', 'public/index.html'),
    ('import_data.json', 'import_data.json'),
]

for local_name, remote_name in files_to_upload:
    local_path = os.path.join(LOCAL_DIR, local_name)
    remote_path = f'{REMOTE_DIR}/{remote_name}'
    print(f'Uploading {local_name}...')
    sftp.put(local_path, remote_path)

sftp.close()

# Install deps and start
run(f'cd {REMOTE_DIR} && npm init -y')
run(f'cd {REMOTE_DIR} && npm install express sql.js multer uuid')

# Import data via a temp node script
import_script = '''
const fs = require('fs');
const initSqlJs = require('sql.js');
const path = require('path');

async function main() {
  const SQL = await initSqlJs();
  const dbPath = path.join(__dirname, 'messages.db');
  let db;
  if (fs.existsSync(dbPath)) db = new SQL.Database(fs.readFileSync(dbPath));
  else db = new SQL.Database();
  db.run(`CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY, group_name TEXT, sender TEXT, content TEXT,
    msg_type TEXT DEFAULT 'text', media_url TEXT, timestamp DATETIME,
    created_at DATETIME DEFAULT (datetime('now'))
  )`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)`);
  const messages = JSON.parse(fs.readFileSync(path.join(__dirname, 'import_data.json'), 'utf8'));
  for (const m of messages) {
    db.run(`INSERT OR IGNORE INTO messages (id,group_name,sender,content,msg_type,media_url,timestamp) VALUES (?,?,?,?,?,?,?)`,
      [m.id, m.group_name, m.sender, m.content, m.msg_type, m.media_url, m.timestamp]);
  }
  fs.writeFileSync(dbPath, Buffer.from(db.export()));
  console.log(`Imported ${messages.length} messages`);
}
main();
'''

# Write import script remotely
sftp2 = ssh.open_sftp()
with sftp2.open(f'{REMOTE_DIR}/import.js', 'w') as f:
    f.write(import_script)
sftp2.close()

print('Running import...')
run(f'cd {REMOTE_DIR} && node import.js')

# PM2 restart
run(f'cd {REMOTE_DIR} && pm2 delete wechat-text 2>/dev/null; pm2 start server.js --name wechat-text')
run('pm2 save')

# Nginx config
nginx_block = '''
    location /wechat-text/ {
        proxy_pass http://127.0.0.1:3001/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
        client_max_body_size 10M;
    }
'''

# Check if already configured
out = run('cat /etc/nginx/sites-enabled/default')
if '/wechat-text/' not in out:
    # Add before the last closing brace
    print('Adding nginx config...')
    run(f'''sudo bash -c "cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.bak"''')
    # Use sed to insert before last }
    escaped = nginx_block.replace("'", "'\\''").replace('\n', '\\n')
    run(f'''sudo sed -i '/^}}/i\\    location /wechat-text/ {{\\n        proxy_pass http://127.0.0.1:3001/;\\n        proxy_http_version 1.1;\\n        proxy_set_header Upgrade \\$http_upgrade;\\n        proxy_set_header Connection '\\''upgrade'\\'';\\n        proxy_set_header Host \\$host;\\n        proxy_set_header X-Real-IP \\$remote_addr;\\n        proxy_cache_bypass \\$http_upgrade;\\n        client_max_body_size 10M;\\n    }}' /etc/nginx/sites-enabled/default''')
else:
    print('Nginx config already exists')

run('sudo nginx -t')
run('sudo systemctl reload nginx')

print('Deploy complete!')
ssh.close()
