# DS720 抖音视频分析系统部署指南
# 在群晖NAS上部署完整的视频AI分析系统

---

## 一、前提条件

### 1.1 确认DS720信息
- **DS720+ 型号**: 确认是否支持Docker
- **IP地址**: 获取DS720在局域网的IP
- **SSH访问**: 确保能SSH连接到DS720
- **存储空间**: 至少10GB可用空间（用于模型和视频）

### 1.2 确认Docker支持
在DS720上：
1. 打开 **套件中心**
2. 搜索 "Docker" 或 "Container Manager"
3. 看到应用就说明支持

---

## 二、在DS720上部署视频分析API

### 2.1 SSH连接到DS720

**Windows上：**
```powershell
# 使用SSH工具（如PuTTY、PowerShell）
ssh 用户名@DS720的IP
```

**或者使用群晖的Web SSH：**
1. DSM → 控制面板 → 终端机
2. 启动SSH终端

### 2.2 拉取Docker镜像

```bash
# 在DS720终端中执行
docker pull evil0ctal/douyin_tiktok_download_api
```

### 2.3 启动容器

```bash
# 创建工作目录
mkdir -p /volume1/docker/douyin-api

# 启动容器（端口18810，可改）
docker run -d \
  --name douyin-api \
  -p 18810:80 \
  -v /volume1/docker/douyin-api:/app/data \
  --restart unless-stopped \
  evil0ctal/douyin_tiktok_download_api
```

**验证容器运行：**
```bash
docker ps | grep douyin-api
```

### 2.4 配置抖音Cookie（关键）

**方法A：从浏览器提取（推荐）**

1. 在电脑浏览器打开：https://www.douyin.com
2. 登录你的抖音账号
3. **按F12** → Application → Cookies
4. 复制所有Cookie值
5. 在DS720上编辑配置文件

**方法B：使用工具导出**

```bash
# 使用curl导出（推荐）
curl -sL 'https://v.douyin.com' \
  -H 'Cookie: 你的cookie字符串' \
  -o /dev/null
```

### 2.5 更新容器内的配置

```bash
# 进入容器
docker exec -it douyin-api bash

# 编辑配置文件
vi /app/douyin_tiktok_download_api/douyin_web/config.yaml
```

找到 `Cookie:` 这一行，替换为你的cookie。

### 2.6 重启容器

```bash
# 退出容器
exit

# 重启容器
docker restart douyin-api
```

### 2.7 测试API

```bash
# 测试API是否正常（在DS720终端）
curl http://localhost:18810/docs

# 或从Windows电脑测试
curl http://DS720的IP:18810/docs
```

应该看到API文档页面。

---

## 三、配置Windows上的OpenClaw Skill

### 3.1 创建Skill目录

```powershell
# 在Windows电脑上
cd C:\Users\Administrator\.openclaw\workspace
mkdir skills
mkdir skills\video-analysis
```

### 3.2 创建Skill脚本

保存为：`C:\Users\Administrator\.openclaw\skills\video-analysis\skill.ps1`

内容见下方（脚本文件）

### 3.3 配置API地址

修改脚本中的 `$API_URL` 变量：

```powershell
# 改为DS720的实际IP
$API_URL = "http://192.168.1.xxx:18810"
```

### 3.4 测试Skill

```powershell
# 在Windows电脑上测试
cd C:\Users\Administrator\.openclaw\skills\video-analysis
.\skill.ps1 -VideoLink "https://v.douyin.com/xxxxx/"
```

---

## 四、在Discord Bot中集成

### 4.1 创建Discord命令

添加到OpenClaw配置中，让Discord bot可以调用分析功能。

在 `C:\Users\Administrator\.openclaw\openclaw.json` 中添加：

```json
{
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "aliases": {
      "分析视频": "powershell -File C:\\Users\\Administrator\\.openclaw\\skills\\video-analysis\\skill.ps1"
    }
  }
}
```

### 4.2 使用方式

在Discord中直接发送：
```
分析视频 https://v.douyin.com/xxxxx/
```

---

## 五、完整使用流程

```
用户 → Discord: "分析视频 https://v.douyin.com/xxxxx/"
      ↓
OpenClaw Gateway 调用Skill
      ↓
DS720 API 解析视频 + 下载 + AI分析
      ↓
Discord Bot 返回分析报告
      ↓
用户查看结果
```

---

## 六、故障排查

### Q: 容器启动失败？
A: 检查端口冲突
```bash
# 查看端口占用
netstat -tuln | grep 18810
```

### Q: API调用失败？
A: 1. 检查DS720和Windows网络连通
```bash
# 从Windows测试
ping DS720的IP
telnet DS720的IP 18810
```
2. 检查容器是否运行
```bash
docker ps | grep douyin-api
```
3. 查看容器日志
```bash
docker logs douyin-api
```

### Q: Cookie无效？
A: 1. Cookie可能过期，重新提取
2. 确保复制完整的cookie字符串

---

## 七、一键部署脚本（可选）

保存为：`deploy_on_ds720.sh`

```bash
#!/bin/bash
# DS720一键部署脚本

echo "========================================"
echo "  DS720 视频分析系统部署"
echo "========================================"
echo ""

# 配置（请修改）
DS720_IP="192.168.1.xxx"
COOKIE="你的cookie字符串"

echo "[1/5] 拉取Docker镜像..."
docker pull evil0ctal/douyin_tiktok_download_api

echo "[2/5] 创建工作目录..."
mkdir -p /volume1/docker/douyin-api

echo "[3/5] 启动容器..."
docker run -d \
  --name douyin-api \
  -p 18810:80 \
  -v /volume1/docker/douyin-api:/app/data \
  --restart unless-stopped \
  evil0ctal/douyin_tiktok_download_api

echo "[4/5] 配置Cookie..."
docker exec -it douyin-api sed -i "s|Cookie:.*|Cookie: ${COOKIE}|g" /app/douyin_tiktok_download_api/douyin_web/config.yaml

echo "[5/5] 重启容器..."
docker restart douyin-api

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "API地址: http://${DS720_IP}:18810"
echo "文档: http://${DS720_IP}:18810/docs"
echo ""
echo "下一步："
echo "1. 在Windows上测试API"
echo "2. 配置OpenClaw Skill"
echo ""
```

使用：
```bash
chmod +x deploy_on_ds720.sh
./deploy_on_ds720.sh
```

---

## 八、快速开始检查清单

部署前确认：
- [ ] DS720支持Docker
- [ ] 知道DS720的IP地址
- [ ] 能SSH连接到DS720
- [ ] 有抖音Cookie
- [ ] Windows电脑能访问DS720

部署后验证：
- [ ] Docker容器运行中
- [ ] API可访问（http://DS720_IP:18810/docs）
- [ ] Cookie配置正确
- [ ] 从Windows能调用API
- [ ] Discord bot能调用分析功能

---

*部署指南版本: 1.0*
*更新时间: 2026-02-05*
