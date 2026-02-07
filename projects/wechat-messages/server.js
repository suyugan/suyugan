const express = require('express');
const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');

const app = express();
const PORT = 3001;
const DATA_FILE = path.join(__dirname, 'data.json');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// 读取数据
function loadData() {
  try {
    const raw = fs.readFileSync(DATA_FILE, 'utf-8');
    return JSON.parse(raw);
  } catch (e) {
    return { groups: [], messages: [] };
  }
}

// 保存数据
function saveData(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), 'utf-8');
}

// GET /api/groups - 获取群组列表
app.get('/api/groups', (req, res) => {
  const data = loadData();
  // 附带每个群的最新消息和消息数量
  const groups = data.groups.map(g => {
    const msgs = data.messages.filter(m => m.group_id === g.id);
    const latest = msgs.sort((a, b) => new Date(b.time) - new Date(a.time))[0];
    return {
      ...g,
      message_count: msgs.length,
      latest_message: latest ? latest.content.substring(0, 50) : '',
      latest_time: latest ? latest.time : g.created_at
    };
  });
  // 按最新消息时间排序
  groups.sort((a, b) => new Date(b.latest_time) - new Date(a.latest_time));
  res.json(groups);
});

// POST /api/groups - 创建群组
app.post('/api/groups', (req, res) => {
  const { name } = req.body;
  if (!name) {
    return res.status(400).json({ error: '群组名称不能为空' });
  }
  const data = loadData();
  const group = {
    id: uuidv4(),
    name,
    created_at: new Date().toISOString().replace('T', ' ').substring(0, 19)
  };
  data.groups.push(group);
  saveData(data);
  res.json(group);
});

// DELETE /api/groups/:id - 删除群组
app.delete('/api/groups/:id', (req, res) => {
  const { id } = req.params;
  const data = loadData();
  const idx = data.groups.findIndex(g => g.id === id);
  if (idx === -1) {
    return res.status(404).json({ error: '群组不存在' });
  }
  data.groups.splice(idx, 1);
  // 同时删除该群的所有消息
  data.messages = data.messages.filter(m => m.group_id !== id);
  saveData(data);
  res.json({ success: true });
});

// GET /api/groups/:id/messages - 获取消息（分页）
app.get('/api/groups/:id/messages', (req, res) => {
  const { id } = req.params;
  const page = parseInt(req.query.page) || 1;
  const limit = parseInt(req.query.limit) || 50;
  
  const data = loadData();
  const group = data.groups.find(g => g.id === id);
  if (!group) {
    return res.status(404).json({ error: '群组不存在' });
  }
  
  // 按时间倒序排列
  const msgs = data.messages
    .filter(m => m.group_id === id)
    .sort((a, b) => new Date(b.time) - new Date(a.time));
  
  const total = msgs.length;
  const start = (page - 1) * limit;
  const end = start + limit;
  const pagedMsgs = msgs.slice(start, end);
  
  res.json({
    group,
    messages: pagedMsgs,
    pagination: {
      page,
      limit,
      total,
      total_pages: Math.ceil(total / limit),
      has_more: end < total
    }
  });
});

// POST /api/groups/:id/messages - 批量添加消息
app.post('/api/groups/:id/messages', (req, res) => {
  const { id } = req.params;
  const { messages } = req.body;
  
  if (!messages || !Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: '消息列表不能为空' });
  }
  
  const data = loadData();
  const group = data.groups.find(g => g.id === id);
  if (!group) {
    return res.status(404).json({ error: '群组不存在' });
  }
  
  const now = new Date().toISOString().replace('T', ' ').substring(0, 19);
  const newMsgs = messages.map(m => ({
    id: uuidv4(),
    group_id: id,
    sender: m.sender || '未知',
    content: m.content || '',
    time: m.time || now,
    created_at: now
  }));
  
  data.messages.push(...newMsgs);
  saveData(data);
  
  res.json({
    success: true,
    count: newMsgs.length,
    messages: newMsgs
  });
});

// DELETE /api/messages/:id - 删除消息
app.delete('/api/messages/:id', (req, res) => {
  const { id } = req.params;
  const data = loadData();
  const idx = data.messages.findIndex(m => m.id === id);
  if (idx === -1) {
    return res.status(404).json({ error: '消息不存在' });
  }
  data.messages.splice(idx, 1);
  saveData(data);
  res.json({ success: true });
});

app.listen(PORT, () => {
  console.log(`微信消息监控系统已启动: http://localhost:${PORT}`);
});
