import express from 'express'
import db, { generateId, verifyToken, getStats } from '../database.js'

const router = express.Router()

// 中间件：验证token
function authMiddleware(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '')

  if (!token) {
    return res.status(401).json({ success: false, error: '未登录' })
  }

  const decoded = verifyToken(token)
  if (!decoded) {
    return res.status(401).json({ success: false, error: 'token无效' })
  }

  req.userId = decoded.userId
  next()
}

// GET /api/stats - 获取统计数据
router.get('/stats', (req, res) => {
  try {
    const stats = getStats()
    res.json({
      success: true,
      data: stats
    })
  } catch (error) {
    console.error('获取统计数据失败:', error)
    res.status(500).json({
      success: false,
      error: '获取统计数据失败'
    })
  }
})

// POST /api/token/parse - 解析支付宝口令
router.post('/token/parse', (req, res) => {
  try {
    const { token } = req.body

    if (!token) {
      return res.status(400).json({
        success: false,
        error: '请提供口令'
      })
    }

    // 模拟解析支付宝口令
    // TODO: 集成真实的支付宝API
    const mockData = parseMockToken(token)

    res.json({
      success: true,
      data: mockData
    })
  } catch (error) {
    console.error('解析口令失败:', error)
    res.status(500).json({
      success: false,
      error: '解析口令失败'
    })
  }
})

// POST /api/match/join - 加入匹配池
router.post('/match/join', authMiddleware, (req, res) => {
  try {
    const { token, score } = req.body

    if (!token || !score) {
      return res.status(400).json({
        success: false,
        error: '参数不完整'
      })
    }

    // 解析口令获取分数
    const tokenData = parseMockToken(token)

    // 创建匹配记录
    const matchId = generateId()
    const matchInsert = db.prepare(`
      INSERT INTO matches (id, matchId, status, totalScore, memberCount, targetScore)
      VALUES (?, ?, 'waiting', ?, 1, 2026)
    `)
    matchInsert.run(matchId, matchId, tokenData.score)

    // 添加成员
    const memberId = generateId()
    const memberInsert = db.prepare(`
      INSERT INTO match_members (id, matchId, userId, score)
      VALUES (?, ?, ?, ?)
    `)
    memberInsert.run(memberId, matchId, req.userId, tokenData.score)

    // 尝试匹配
    const matchResult = tryMatch(matchId, req.userId, tokenData.score)

    res.json({
      success: true,
      data: {
        matchId,
        status: matchResult.status,
        members: matchResult.members,
        totalScore: matchResult.totalScore
      }
    })
  } catch (error) {
    console.error('加入匹配池失败:', error)
    res.status(500).json({
      success: false,
      error: '加入匹配池失败'
    })
  }
})

// GET /api/match/status/:matchId - 查询匹配状态
router.get('/match/status/:matchId', (req, res) => {
  try {
    const { matchId } = req.params

    const match = db.prepare('SELECT * FROM matches WHERE matchId = ?').get(matchId)
    if (!match) {
      return res.status(404).json({
        success: false,
        error: '匹配不存在'
      })
    }

    const members = db.prepare(`
      SELECT u.id, u.username, u.avatar, m.score, m.joinedAt
      FROM match_members m
      JOIN users u ON m.userId = u.id
      WHERE m.matchId = ?
    `).all(matchId)

    res.json({
      success: true,
      data: {
        ...match,
        members
      }
    })
  } catch (error) {
    console.error('查询匹配状态失败:', error)
    res.status(500).json({
      success: false,
      error: '查询匹配状态失败'
    })
  }
})

// 模拟函数：解析口令
function parseMockToken(token) {
  // 从口令中提取分数（模拟）
  const scoreMatch = token.match(/分数(\d+)/)
  const score = scoreMatch ? parseInt(scoreMatch[1]) : Math.floor(Math.random() * 1000) + 200

  return {
    score,
    userId: generateId(),
    username: '支付宝用户',
    avatar: 'https://via.placeholder.com/100x100/007AFF/FFFFFF?text=头像'
  }
}

// 匹配算法
function tryMatch(matchId, userId, userScore) {
  // 查找等待中的匹配
  const waitingMatches = db.prepare(`
    SELECT id, matchId, memberCount, totalScore
    FROM matches
    WHERE status = 'waiting' AND id != ?
    ORDER BY createdAt ASC
  `).all(matchId)

  for (const match of waitingMatches) {
    const currentTotal = match.totalScore + userScore

    // 目标分数2026
    const targetScore = 2026

    // 如果正好2026分，立即匹配
    if (currentTotal === targetScore) {
      completeMatch(match.id)
      completeMatch(matchId)

      const members = getMatchMembers(match.id)
      members.push(...getMatchMembers(matchId))

      return {
        status: 'completed',
        totalScore: currentTotal,
        members
      }
    }

    // 如果接近2026分（±20分），也可以匹配
    if (Math.abs(currentTotal - targetScore) <= 20) {
      completeMatch(match.id)
      completeMatch(matchId)

      const members = getMatchMembers(match.id)
      members.push(...getMatchMembers(matchId))

      return {
        status: 'completed',
        totalScore: currentTotal,
        members
      }
    }
  }

  // 没找到匹配，返回等待状态
  return {
    status: 'waiting',
    totalScore: userScore,
    members: getMatchMembers(matchId)
  }
}

// 完成匹配
function completeMatch(matchId) {
  db.prepare('UPDATE matches SET status = "completed", updatedAt = CURRENT_TIMESTAMP WHERE id = ?').run(matchId)
}

// 获取匹配成员
function getMatchMembers(matchId) {
  return db.prepare(`
    SELECT u.id, u.username, u.avatar, m.score, m.joinedAt
    FROM match_members m
    JOIN users u ON m.userId = u.id
    WHERE m.matchId = ?
  `).all(matchId)
}

export default router
