import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import sqlite3 from 'sqlite3'
import jwt from 'jsonwebtoken'
import fs from 'fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const JWT_SECRET = process.env.JWT_SECRET || 'sesame-team-tool-secret-key-2026'

// 确保数据目录存在
const dataDir = join(__dirname, '../data')
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true })
  console.log('✓ 数据目录已创建:', dataDir)
}

// 数据库路径
const dbPath = join(dataDir, 'sesame.db')
console.log('数据库路径:', dbPath)

// 初始化数据库
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('✗ 数据库连接失败:', err)
  } else {
    console.log('✓ 数据库连接成功')
    initTables()
  }
})

// 初始化表
function initTables() {
  db.serialize(() => {
    // 用户表
    db.exec(`
      CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT,
        avatar TEXT,
        totalScore INTEGER DEFAULT 0,
        teamCount INTEGER DEFAULT 0,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `)

    // 匹配表
    db.exec(`
      CREATE TABLE IF NOT EXISTS matches (
        id TEXT PRIMARY KEY,
        matchId TEXT UNIQUE,
        status TEXT DEFAULT 'waiting',
        totalScore INTEGER DEFAULT 0,
        memberCount INTEGER DEFAULT 0,
        targetScore INTEGER DEFAULT 2026,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        updatedAt DATETIME
      )
    `)

    // 匹配成员表
    db.exec(`
      CREATE TABLE IF NOT EXISTS match_members (
        id TEXT PRIMARY KEY,
        matchId TEXT,
        userId TEXT,
        score INTEGER,
        joinedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (userId) REFERENCES users(id),
        FOREIGN KEY (matchId) REFERENCES matches(matchId)
      )
    `)

    // 广告表
    db.exec(`
      CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        imageUrl TEXT,
        linkUrl TEXT,
        position TEXT,
        isActive BOOLEAN DEFAULT 1,
        createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `)

    console.log('✓ 数据库表初始化完成')
  })
}

// 工具函数：生成UUID
function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

// 工具函数：生成JWT
function generateToken(userId) {
  return jwt.sign({ userId }, JWT_SECRET, { expiresIn: '7d' })
}

// 工具函数：验证JWT
function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET)
  } catch (error) {
    return null
  }
}

// API：获取统计数据
function getStats() {
  return new Promise((resolve, reject) => {
    db.all('SELECT COUNT(*) as count FROM matches WHERE status = "completed"', (err, rows) => {
      if (err) {
        reject(err)
      } else {
        const totalTeams = rows[0].count

        db.get('SELECT COUNT(*) as count FROM match_members', (err, rows) => {
          if (err) {
            reject(err)
          } else {
            const totalTokens = rows[0].count
            resolve({
              totalTeams,
              totalTokens
            })
          }
        })
      }
    })
  })
}

export default db

// 导出工具函数
export {
  generateId,
  generateToken,
  verifyToken,
  getStats
}
