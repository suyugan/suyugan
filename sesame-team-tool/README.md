# 芝麻组队工具

一个基于 Vue 3 + Node.js 的 H5 支付宝口令组队工具

## 📋 项目简介

帮助用户通过支付宝口令自动匹配组队，凑齐2026分完成任务。

### 核心功能

- ✅ 支付宝口令解析
- ✅ 智能匹配算法
- ✅ 实时匹配状态
- ✅ 数据统计展示
- ✅ 移动端H5适配

## 🛠️ 技术栈

### 前端
- Vue 3 (Composition API)
- Vite
- Tailwind CSS
- Pinia (状态管理)
- Vue Router
- Axios

### 后端
- Node.js + Express
- SQLite (数据库)
- JWT (认证)

### 部署
- Docker + Docker Compose
- Nginx (反向代理)

## 📁 项目结构

```
sesame-team-tool/
├── frontend/                 # 前端Vue项目
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面
│   │   ├── stores/         # Pinia状态
│   │   ├── router/         # 路由
│   │   ├── api/            # API封装
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css
│   ├── index.html
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
│
├── backend/                  # 后端Node.js项目
│   ├── src/
│   │   ├── index.js
│   │   ├── database.js
│   │   └── routes/
│   │       └── index.js
│   ├── package.json
│   ├── Dockerfile
│   └── .env
│
├── docker-compose.yml          # Docker编排
└── README.md
```

## 🚀 快速开始

### 方式1：使用 Docker（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd sesame-team-tool

# 启动服务
docker-compose up -d

# 访问
# 前端: http://localhost:3000
# 后端: http://localhost:5001
```

### 方式2：本地开发

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问: http://localhost:3000
```

#### 后端开发

```bash
cd backend

# 安装依赖
npm install

# 启动服务器
npm run dev

# 访问: http://localhost:5001
```

## 📡 API文档

### 1. 获取统计数据

```
GET /api/stats

Response:
{
  "success": true,
  "data": {
    "totalTeams": 1057,
    "totalTokens": 1480
  }
}
```

### 2. 解析口令

```
POST /api/token/parse
Body:
{
  "token": "支付宝吱口令"
}

Response:
{
  "success": true,
  "data": {
    "score": 650,
    "userId": "xxx",
    "username": "xxx",
    "avatar": "xxx"
  }
}
```

### 3. 加入匹配池

```
POST /api/match/join
Headers:
Authorization: Bearer <token>
Body:
{
  "token": "支付宝吱口令",
  "score": 650
}

Response:
{
  "success": true,
  "data": {
    "matchId": "xxx",
    "status": "waiting",
    "members": [...],
    "totalScore": 2026
  }
}
```

### 4. 查询匹配状态

```
GET /api/match/status/:matchId

Response:
{
  "success": true,
  "data": {
    "matchId": "xxx",
    "status": "completed",
    "members": [...]
  }
}
```

## 🎨 页面设计

### 已完成

- [x] 首页（状态栏、统计卡片、输入框、广告、指南、导航）
- [x] 状态栏组件
- [x] 统计卡片组件
- [x] 广告位组件
- [x] 步骤指引组件
- [x] 底部导航组件

### 待开发

- [ ] 匹配池页面
- [ ] 找分数页面
- [ ] 个人中心页面
- [ ] 匹配成功页面

## 🔄 匹配算法

系统自动匹配3名用户，使总分达到或接近2026分：

1. 用户加入匹配池
2. 系统查找等待中的用户
3. 智能匹配算法计算最优组合
4. 完成匹配或继续等待

## 📝 开发计划

### Phase 1：基础框架（已完成）
- [x] 创建前后端项目
- [x] 配置 Tailwind CSS
- [x] 搭建数据库
- [x] 实现首页

### Phase 2：核心功能（待开发）
- [ ] 匹配池页面
- [ ] 实时匹配状态
- [ ] WebSocket推送
- [ ] 找分数页面

### Phase 3：补充功能（待开发）
- [ ] 个人中心
- [ ] 历史记录
- [ ] 广告管理后台
- [ ] 数据统计图表

### Phase 4：测试部署（待开发）
- [ ] 功能测试
- [ ] 性能优化
- [ ] 生产部署
- [ ] 域名配置

## 🐛 常见问题

### Q: 如何集成真实的支付宝API？

A: 需要申请支付宝开放平台账号，获取相关API权限。目前使用模拟数据。

### Q: 匹配算法如何调整？

A: 在 `backend/src/routes/index.js` 中的 `tryMatch` 函数修改匹配逻辑。

### Q: 如何更换广告？

A: 可以直接修改 `frontend/src/views/Home.vue` 中的广告组件 props，或开发后台管理页面。

## 📄 许可证

MIT

## 👥 贡献

欢迎提交 Issue 和 Pull Request！
