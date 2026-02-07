const express = require('express');
const initSqlJs = require('sql.js');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 3000;

// 确保目录存在
const dataDir = path.join(__dirname, 'data');
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });
if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

let db;
const dbPath = path.join(dataDir, 'db.sqlite');

// 初始化数据库
async function initDb() {
  const SQL = await initSqlJs();
  
  if (fs.existsSync(dbPath)) {
    const buffer = fs.readFileSync(dbPath);
    db = new SQL.Database(buffer);
  } else {
    db = new SQL.Database();
  }
  
  // 群组表
  db.run(`
    CREATE TABLE IF NOT EXISTS groups (
      id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      avatar TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);
  
  // 图片表
  db.run(`
    CREATE TABLE IF NOT EXISTS images (
      id TEXT PRIMARY KEY,
      group_id TEXT NOT NULL,
      filename TEXT NOT NULL,
      original_name TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE
    )
  `);
  
  saveDb();
}

function saveDb() {
  const data = db.export();
  const buffer = Buffer.from(data);
  fs.writeFileSync(dbPath, buffer);
}

// 中间件
app.use(express.json());
app.use(express.static('public'));
app.use('/uploads', express.static('uploads'));

// 配置 multer
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const groupDir = path.join(uploadsDir, req.params.groupId);
    if (!fs.existsSync(groupDir)) fs.mkdirSync(groupDir, { recursive: true });
    cb(null, groupDir);
  },
  filename: (req, file, cb) => {
    const ext = path.extname(file.originalname);
    cb(null, uuidv4() + ext);
  }
});
const upload = multer({ storage });

// ========== API 路由 ==========

// 获取所有群组
app.get('/api/groups', (req, res) => {
  const stmt = db.prepare(`
    SELECT g.id, g.name, g.avatar, g.created_at, COUNT(i.id) as image_count
    FROM groups g LEFT JOIN images i ON g.id = i.group_id
    GROUP BY g.id ORDER BY g.created_at DESC
  `);
  
  const groups = [];
  while (stmt.step()) groups.push(stmt.getAsObject());
  stmt.free();
  res.json(groups);
});

// 创建群组
app.post('/api/groups', (req, res) => {
  const { name, avatar } = req.body;
  if (!name) return res.status(400).json({ error: '群名不能为空' });
  
  const id = uuidv4();
  db.run('INSERT INTO groups (id, name, avatar) VALUES (?, ?, ?)', [id, name, avatar || null]);
  saveDb();
  res.json({ id, name, avatar });
});

// 更新群组
app.put('/api/groups/:id', (req, res) => {
  const { name, avatar } = req.body;
  db.run('UPDATE groups SET name = ?, avatar = ? WHERE id = ?', [name, avatar, req.params.id]);
  saveDb();
  res.json({ success: true });
});

// 删除群组
app.delete('/api/groups/:id', (req, res) => {
  const groupId = req.params.id;
  
  // 删除图片文件
  const groupDir = path.join(uploadsDir, groupId);
  if (fs.existsSync(groupDir)) {
    fs.rmSync(groupDir, { recursive: true, force: true });
  }
  
  // 删除数据库记录
  db.run('DELETE FROM images WHERE group_id = ?', [groupId]);
  db.run('DELETE FROM groups WHERE id = ?', [groupId]);
  saveDb();
  res.json({ success: true });
});

// 获取群组图片（分页，按时间倒序，最新的在前面）
app.get('/api/groups/:groupId/images', (req, res) => {
  const { groupId } = req.params;
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 50;
  const offset = (page - 1) * limit;
  
  // 按 created_at 倒序排列，rowid 作为次要排序（保证按插入顺序，后插入的在前）
  const stmt = db.prepare(`
    SELECT * FROM images 
    WHERE group_id = ? 
    ORDER BY created_at DESC, rowid DESC
    LIMIT ? OFFSET ?
  `);
  stmt.bind([groupId, limit, offset]);
  
  const images = [];
  while (stmt.step()) {
    const row = stmt.getAsObject();
    row.url = `uploads/${groupId}/${row.filename}`;
    images.push(row);
  }
  stmt.free();
  
  const countStmt = db.prepare('SELECT COUNT(*) as count FROM images WHERE group_id = ?');
  countStmt.bind([groupId]);
  countStmt.step();
  const total = countStmt.getAsObject().count;
  countStmt.free();
  
  res.json({ images, page, limit, total, hasMore: offset + images.length < total });
});

// 上传图片
app.post('/api/groups/:groupId/images', upload.array('images', 50), (req, res) => {
  const { groupId } = req.params;
  
  // 验证群组存在
  const groupStmt = db.prepare('SELECT * FROM groups WHERE id = ?');
  groupStmt.bind([groupId]);
  if (!groupStmt.step()) {
    groupStmt.free();
    return res.status(404).json({ error: '群组不存在' });
  }
  groupStmt.free();
  
  const results = [];
  for (const file of req.files) {
    const id = uuidv4();
    const now = new Date().toISOString();
    db.run('INSERT INTO images (id, group_id, filename, original_name, created_at) VALUES (?, ?, ?, ?, ?)', 
      [id, groupId, file.filename, file.originalname, now]);
    results.push({
      id,
      filename: file.filename,
      original_name: file.originalname,
      url: `uploads/${groupId}/${file.filename}`
    });
  }
  
  saveDb();
  res.json({ uploaded: results.length, images: results });
});

// 删除单张图片
app.delete('/api/images/:id', (req, res) => {
  const stmt = db.prepare('SELECT * FROM images WHERE id = ?');
  stmt.bind([req.params.id]);
  
  if (!stmt.step()) {
    stmt.free();
    return res.status(404).json({ error: '图片不存在' });
  }
  
  const image = stmt.getAsObject();
  stmt.free();
  
  // 删除文件
  const filePath = path.join(uploadsDir, image.group_id, image.filename);
  if (fs.existsSync(filePath)) fs.unlinkSync(filePath);
  
  // 删除数据库记录
  db.run('DELETE FROM images WHERE id = ?', [req.params.id]);
  saveDb();
  res.json({ success: true });
});

// 启动服务器
initDb().then(() => {
  app.listen(PORT, () => {
    console.log(`🚀 微信群聊截图查看器已启动`);
    console.log(`📍 访问地址: http://localhost:${PORT}`);
  });
});
