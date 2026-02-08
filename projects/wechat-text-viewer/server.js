const express = require('express');
const initSqlJs = require('sql.js');
const multer = require('multer');
const { v4: uuidv4 } = require('uuid');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3001;

app.use(express.json({ limit: '10mb' }));
app.use(express.static('public'));
app.use('/uploads', express.static('uploads'));

// Multer config
const storage = multer.diskStorage({
  destination: 'uploads/',
  filename: (req, file, cb) => cb(null, uuidv4() + path.extname(file.originalname))
});
const upload = multer({ storage, limits: { fileSize: 10 * 1024 * 1024 } });

let db;

async function initDB() {
  const SQL = await initSqlJs();
  const dbPath = path.join(__dirname, 'messages.db');
  if (fs.existsSync(dbPath)) {
    db = new SQL.Database(fs.readFileSync(dbPath));
  } else {
    db = new SQL.Database();
  }
  db.run(`CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    group_name TEXT,
    sender TEXT,
    content TEXT,
    msg_type TEXT DEFAULT 'text',
    media_url TEXT,
    timestamp DATETIME,
    created_at DATETIME DEFAULT (datetime('now'))
  )`);
  db.run(`CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)`);
  saveDB();
}

function saveDB() {
  const data = db.export();
  fs.writeFileSync(path.join(__dirname, 'messages.db'), Buffer.from(data));
}

// GET messages with pagination & search
app.get('/api/messages', (req, res) => {
  const { page = 1, limit = 50, search, before, after } = req.query;
  const offset = (page - 1) * limit;
  let where = [];
  let params = [];
  if (search) { where.push("(content LIKE ? OR sender LIKE ?)"); params.push(`%${search}%`, `%${search}%`); }
  if (before) { where.push("timestamp < ?"); params.push(before); }
  if (after) { where.push("timestamp > ?"); params.push(after); }
  const whereClause = where.length ? 'WHERE ' + where.join(' AND ') : '';
  const countResult = db.exec(`SELECT COUNT(*) as c FROM messages ${whereClause}`, params);
  const total = countResult[0]?.values[0][0] || 0;
  const rows = db.exec(`SELECT * FROM messages ${whereClause} ORDER BY timestamp ASC, rowid ASC LIMIT ? OFFSET ?`, [...params, Number(limit), Number(offset)]);
  const columns = rows[0]?.columns || [];
  const messages = (rows[0]?.values || []).map(r => Object.fromEntries(columns.map((c, i) => [c, r[i]])));
  res.json({ messages, total, page: Number(page), limit: Number(limit) });
});

// GET latest
app.get('/api/messages/latest', (req, res) => {
  const { limit = 20 } = req.query;
  const rows = db.exec(`SELECT * FROM messages ORDER BY timestamp DESC, rowid DESC LIMIT ?`, [Number(limit)]);
  const columns = rows[0]?.columns || [];
  const messages = (rows[0]?.values || []).map(r => Object.fromEntries(columns.map((c, i) => [c, r[i]])));
  res.json({ messages: messages.reverse() });
});

// POST single message
app.post('/api/messages', (req, res) => {
  const { group_name, sender, content, msg_type = 'text', media_url, timestamp } = req.body;
  const id = uuidv4();
  const ts = timestamp || new Date().toISOString();
  db.run(`INSERT INTO messages (id, group_name, sender, content, msg_type, media_url, timestamp) VALUES (?,?,?,?,?,?,?)`,
    [id, group_name, sender, content, msg_type, media_url, ts]);
  saveDB();
  res.json({ id, success: true });
});

// POST batch
app.post('/api/messages/batch', (req, res) => {
  const { messages } = req.body;
  if (!Array.isArray(messages)) return res.status(400).json({ error: 'messages must be array' });
  const ids = [];
  for (const m of messages) {
    const id = uuidv4();
    const ts = m.timestamp || new Date().toISOString();
    db.run(`INSERT INTO messages (id, group_name, sender, content, msg_type, media_url, timestamp) VALUES (?,?,?,?,?,?,?)`,
      [id, m.group_name, m.sender, m.content, m.msg_type || 'text', m.media_url, ts]);
    ids.push(id);
  }
  saveDB();
  res.json({ ids, count: ids.length, success: true });
});

// DELETE
app.delete('/api/messages/:id', (req, res) => {
  db.run(`DELETE FROM messages WHERE id = ?`, [req.params.id]);
  saveDB();
  res.json({ success: true });
});

// Upload
app.post('/api/upload', upload.single('file'), (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'no file' });
  res.json({ url: `uploads/${req.file.filename}`, success: true });
});

initDB().then(() => {
  app.listen(PORT, '0.0.0.0', () => console.log(`Server running on port ${PORT}`));
});
