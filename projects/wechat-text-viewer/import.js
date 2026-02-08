const Database = require('better-sqlite3');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');
const path = require('path');

const db = new Database(path.join(__dirname, 'messages.db'));
db.pragma('journal_mode = WAL');
db.exec(`
  CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    group_name TEXT,
    sender TEXT,
    content TEXT,
    msg_type TEXT DEFAULT 'text',
    timestamp DATETIME,
    created_at DATETIME DEFAULT (datetime('now', 'localtime'))
  )
`);

const text = fs.readFileSync(process.argv[2] || path.join(__dirname, '..', '..', 'wechat-ocr', 'messages.txt'), 'utf-8');
const lines = text.split('\n');

const groupMatch = text.match(/群名：(.+?)（/);
const groupName = groupMatch ? groupMatch[1] : '未知群';

const baseTime = new Date('2026-02-08T20:00:00+08:00');
let msgIndex = 0;
const messages = [];

for (const line of lines) {
  const m = line.match(/^\[(.+?)\]\s+(.+?):\s+(.+)$/);
  if (!m) continue;
  
  let [, timeStr, sender, content] = m;
  sender = sender.trim();
  content = content.trim();
  
  // 判断消息类型
  let msgType = 'text';
  if (content.startsWith('[图片]')) msgType = 'image';
  else if (content.startsWith('[视频]')) msgType = 'video';
  else if (content.startsWith('[分享链接]') || content.includes('https://')) msgType = 'link';
  
  // 时间处理
  let timestamp;
  if (timeStr === '未知时间') {
    timestamp = new Date(baseTime.getTime() + msgIndex * 60000);
  } else {
    const [h, min] = timeStr.split(':').map(Number);
    timestamp = new Date('2026-02-08T00:00:00+08:00');
    timestamp.setHours(h, min, 0, 0);
  }
  
  messages.push({
    id: uuidv4(),
    group_name: groupName,
    sender: sender === '未知发送者' ? '未知' : sender,
    content,
    msg_type: msgType,
    timestamp: timestamp.toISOString()
  });
  msgIndex++;
}

const insert = db.prepare(`INSERT OR IGNORE INTO messages (id, group_name, sender, content, msg_type, timestamp) VALUES (@id, @group_name, @sender, @content, @msg_type, @timestamp)`);
const tx = db.transaction(() => { for (const msg of messages) insert.run(msg); });
tx();

console.log(`导入完成: ${messages.length} 条消息`);
