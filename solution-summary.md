# 视频分析系统部署 - 最终解决方案

## ⚠️ 问题总结

### Docker 系统现状
- ✅ Docker Engine 已安装（v29.2.0）
- ✅ Docker CLI 已安装
- ❌ Docker Desktop 无法启动（无法连接到 Docker Engine daemon）
- ❌ Docker run 命令无法执行（"Error response from daemon: Docker Desktop is unable to start"）

### 可能原因
1. Docker Engine daemon 未运行
2. Docker Desktop 安装不完整
3. 系统配置冲突
4. Windows 服务问题

---

## 🎯 最终解决方案（推荐）

### 方案 A：完全重装 Docker（最可靠）

**步骤：**

1. **停止所有 Docker 进程**
   ```powershell
   # 杀掉所有 Docker 相关进程
   Get-Process | Where-Object {$_.ProcessName -like "*docker*"} | Stop-Process -Force
   ```

2. **卸载 Docker Desktop**
   - 控制面板 → 程序和功能 → 卸载 Docker Desktop
   - 或运行卸载命令：`"C:\Program Files\Docker\Docker\Docker Desktop.exe" /uninstall`

3. **下载完整 Docker Desktop（使用安装包）**
   - 从官网下载：https://www.docker.com/products/docker-desktop/
   - 双击完整安装包（不是 web 安装器）

4. **重新安装 Docker Desktop**
   - 按照提示完成安装
   - 启动后验证托盘中有鲸鱼图标

5. **使用 docker CLI 部署 API**
   ```powershell
   # 部署视频分析API容器
   docker run -d --name douyin-api -p 18810:80 -v C:\Users\Administrator\.openclaw\video-analysis\data:/app/data --restart unless-stopped evil0ctal/douyin_tiktok_download_api
   ```

6. **验证容器运行**
   ```powershell
   docker ps
   # 应该看到 douyin-api 容器
   ```

---

### 方案 B：修复 Docker Engine（如果方案A失败）

**步骤：**

1. **重置 Docker 配置**
   ```powershell
   # 完全退出 Docker Desktop
   taskkill /F /IM docker* /T
   
   # 删除配置目录（慎重！）
   # Remove-Item -Path "$env:USERPROFILE\.docker" -Recurse -Force
   ```
   
   重启 Docker Desktop

2. **使用 docker CLI 命令**
   Docker CLI 不依赖 Docker Desktop，可以直接使用

---

### 方案 C：使用 Docker Compose（高级用户）

如果需要更复杂的部署，使用 docker-compose.yml：

```yaml
version: "3.8"
services:
  douyin-api:
    image: evil0ctal/douyin_tiktok_download_api
    container_name: douyin-api
    ports:
      - "18810:80"
    volumes:
      - C:\Users\Administrator\.openclaw\video-analysis\data:/app/data
    restart: unless-stopped
```

**部署：**
```powershell
docker-compose up -d
```

---

## 📋 推荐执行顺序

### 立即执行（按顺序）：

1. **方案 A**：重装 Docker Desktop（最可靠）
   - 如果失败，进入方案 B

2. **验证 Docker Engine**
   ```powershell
   docker info
   docker version
   ```

3. **部署 API 容器**
   - 使用 docker CLI 部署（不依赖 Docker Desktop）

4. **配置 Cookie**
   - 粘贴 Cookie 到配置文件

5. **测试完整流程**
   - 发送一个抖音视频链接到 Discord
   - 验证是否返回分析报告

---

## 🔍 故障排查

### 如果容器无法启动

**检查：**
1. 端口 18810 是否被占用
   ```powershell
   netstat -an | findstr ":18810"
   ```

2. 防火墙是否阻止
   - Windows Defender 防火墙
   - 企业防火墙设置

3. 数据卷权限
   - 确认目录存在并可访问

### 如果 API 无响应

**检查：**
1. 容器是否在运行：`docker ps`
2. 容器日志：`docker logs douyin-api`
3. 本地访问：`curl http://localhost:18810/docs`

---

## 💡 一键部署脚本（更新版）

如果方案 A 成功，创建一个更新的 `deploy-api-v2.ps1`，使用 docker CLI 而不是依赖 Docker Desktop。

---

*部署问题解决时间：2026-02-05 10:33*
