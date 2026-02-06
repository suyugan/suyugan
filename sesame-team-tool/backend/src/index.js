import express from 'express'
import cors from 'cors'
import dotenv from 'dotenv'
import { fileURLToPath } from 'url'
import { dirname, join } from 'path'
import db from './database.js'
import routes from './routes/index.js'

dotenv.config()

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const app = express()
const PORT = process.env.PORT || 5001

// 中间件
app.use(cors())
app.use(express.json())
app.use(express.urlencoded({ extended: true }))

// 静态文件（生产环境）
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(join(__dirname, '../frontend/dist')))
}

// API 路由
app.use('/api', routes)

// SPA 路由（生产环境）
if (process.env.NODE_ENV === 'production') {
  app.get('*', (req, res) => {
    res.sendFile(join(__dirname, '../frontend/dist/index.html'))
  })
}

// 启动服务器
app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════╗
║     芝麻组队工具 - 后端服务           ║
╠═══════════════════════════════════════╣
║   服务器已启动                         ║
║   端口: ${PORT}                          ║
║   环境: ${process.env.NODE_ENV || 'development'}        ║
╚═══════════════════════════════════════╝
  `)
})

export default app
