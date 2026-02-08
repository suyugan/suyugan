import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

# Delete from database using sqlite3
corrupted_files = [
    '1ecace05-fccb-46e0-8f68-5bf14a5544e5.png',
    '109ac73c-f334-4a1e-8db8-f424a7c41aa0.png',
    '5dde2278-d7f7-4f9d-aeae-31151462a220.png',
    'e707a3a2-3234-4ff3-ac1d-232baa1e34b0.png',
    '1afdd58e-2d14-4d30-ba7f-e7fc522f94aa.png',  # test file
]

# Create a Node script to delete from sql.js database
script = '''
const initSqlJs = require('sql.js');
const fs = require('fs');

async function main() {
    const SQL = await initSqlJs();
    const dbPath = './data/db.sqlite';
    const db = new SQL.Database(fs.readFileSync(dbPath));
    
    const filenames = %s;
    
    for (const filename of filenames) {
        db.run('DELETE FROM images WHERE filename = ?', [filename]);
        console.log('Deleted from DB:', filename);
    }
    
    fs.writeFileSync(dbPath, Buffer.from(db.export()));
    console.log('Database saved');
}

main();
''' % str(corrupted_files)

# Write the script to server
sftp = ssh.open_sftp()
with sftp.file('/home/ubuntu/wechat-viewer/cleanup.js', 'w') as f:
    f.write(script)
sftp.close()

# Run the script
stdin, stdout, stderr = ssh.exec_command('cd /home/ubuntu/wechat-viewer && node cleanup.js')
print(stdout.read().decode('utf-8'))
print(stderr.read().decode('utf-8'))

# Clean up the script
ssh.exec_command('rm /home/ubuntu/wechat-viewer/cleanup.js')

ssh.close()
print('Done!')
