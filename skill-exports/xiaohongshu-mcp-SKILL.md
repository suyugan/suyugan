---
name: xiaohongshu-mcp
description: 小红书MCP工具。搜索笔记、发布图文/视频、获取帖子详情、评论、用户主页等。当用户提到"小红书发布"、"小红书搜索"、"发小红书"、"XHS"时触发。
---

# 小红书 MCP

基于 xiaohongshu-mcp Docker 服务，通过 MCP 协议操控小红书。

## 服务信息
- **Docker容器**: xiaohongshu-mcp
- **MCP端点**: http://localhost:18060/mcp
- **协议**: Streamable HTTP MCP

## 可用工具（13个）
1. **login** - 登录小红书（需要扫码）
2. **check_login** - 检查登录状态
3. **search** - 搜索小红书内容
4. **get_feed_list** - 获取推荐列表
5. **get_feed_detail** - 获取帖子详情（需要帖子ID + xsec_token）
6. **publish_image_post** - 发布图文帖子（标题≤20字，正文≤1000字）
7. **publish_video_post** - 发布视频帖子
8. **post_comment** - 发表评论
9. **get_user_profile** - 获取用户主页信息

## 调用方式

通过 Python 调用 MCP HTTP endpoint：

```python
import requests, json

def call_mcp_tool(tool_name, arguments=None):
    """调用小红书MCP工具"""
    # Initialize session
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "openclaw", "version": "1.0"}
        }
    }
    
    session = requests.Session()
    r = session.post("http://localhost:18060/mcp", json=init_payload)
    session_id = r.headers.get("mcp-session-id")
    
    # Call tool
    tool_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments or {}
        }
    }
    
    headers = {}
    if session_id:
        headers["mcp-session-id"] = session_id
    
    r = session.post("http://localhost:18060/mcp", json=tool_payload, headers=headers)
    return r.json()

# 示例：搜索
result = call_mcp_tool("search", {"keyword": "AI教程", "limit": 10})

# 示例：发布图文
result = call_mcp_tool("publish_image_post", {
    "title": "标题（≤20字）",
    "content": "正文内容（≤1000字）",
    "images": ["D:\\path\\to\\image1.png", "D:\\path\\to\\image2.png"]
})
```

## 重要限制
- **标题不超过20字**
- **正文不超过1000字**
- 需要先登录（扫码），登录状态保存在 Docker volume
- 同一账号不能在多个网页端同时登录
- 每天发帖上限约50篇
- 图文流量 > 视频 > 纯文字

## Docker 管理
```powershell
# 查看状态
docker ps | findstr xiaohongshu

# 重启
docker restart xiaohongshu-mcp

# 查看日志
docker logs xiaohongshu-mcp --tail 20
```
