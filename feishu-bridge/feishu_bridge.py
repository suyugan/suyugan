"""
飞书 <-> OpenClaw 桥接服务

功能：
1. 接收飞书机器人消息
2. 转发到OpenClaw webhook
3. 将OpenClaw回复发送回飞书

使用前需要配置环境变量（或修改下面的配置）
"""

import os
import json
import hashlib
import time
import requests
from flask import Flask, request, jsonify
from threading import Thread

app = Flask(__name__)

# ========== 配置 ==========
# 飞书应用配置（从飞书开放平台获取）
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "your_app_id")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "your_app_secret")
FEISHU_VERIFICATION_TOKEN = os.getenv("FEISHU_VERIFICATION_TOKEN", "your_verification_token")
FEISHU_ENCRYPT_KEY = os.getenv("FEISHU_ENCRYPT_KEY", "")  # 可选

# OpenClaw配置
OPENCLAW_WEBHOOK_URL = os.getenv("OPENCLAW_WEBHOOK_URL", "http://127.0.0.1:18789/hooks/agent")
OPENCLAW_HOOK_TOKEN = os.getenv("OPENCLAW_HOOK_TOKEN", "your_hook_token")

# 服务配置
PORT = int(os.getenv("PORT", 8066))

# ========== 飞书API ==========
class FeishuAPI:
    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.tenant_access_token = None
        self.token_expires_at = 0
    
    def get_tenant_access_token(self):
        """获取tenant_access_token"""
        if self.tenant_access_token and time.time() < self.token_expires_at - 60:
            return self.tenant_access_token
        
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        resp = requests.post(url, json=payload)
        data = resp.json()
        
        if data.get("code") == 0:
            self.tenant_access_token = data["tenant_access_token"]
            self.token_expires_at = time.time() + data.get("expire", 7200)
            return self.tenant_access_token
        else:
            raise Exception(f"获取token失败: {data}")
    
    def send_message(self, chat_id, content, msg_type="text"):
        """发送消息到飞书"""
        token = self.get_tenant_access_token()
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        if msg_type == "text":
            content_body = json.dumps({"text": content})
        else:
            content_body = content
        
        payload = {
            "receive_id": chat_id,
            "msg_type": msg_type,
            "content": content_body
        }
        
        resp = requests.post(
            url,
            headers=headers,
            params={"receive_id_type": "chat_id"},
            json=payload
        )
        return resp.json()
    
    def reply_message(self, message_id, content, msg_type="text"):
        """回复消息"""
        token = self.get_tenant_access_token()
        url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/reply"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
        
        if msg_type == "text":
            content_body = json.dumps({"text": content})
        else:
            content_body = content
        
        payload = {
            "msg_type": msg_type,
            "content": content_body
        }
        
        resp = requests.post(url, headers=headers, json=payload)
        return resp.json()


feishu_api = FeishuAPI(FEISHU_APP_ID, FEISHU_APP_SECRET)

# ========== 消息处理 ==========
# 已处理消息ID缓存（防止重复处理）
processed_messages = set()

def call_openclaw(message_text, user_id, chat_id, message_id):
    """调用OpenClaw webhook并回复"""
    try:
        # 构造OpenClaw webhook请求
        payload = {
            "message": message_text,
            "name": "Feishu",
            "sessionKey": f"feishu:{chat_id}",  # 使用chat_id作为session标识
            "deliver": False,  # 我们自己处理回复
            "timeoutSeconds": 120
        }
        
        headers = {
            "Authorization": f"Bearer {OPENCLAW_HOOK_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # 调用OpenClaw
        resp = requests.post(
            OPENCLAW_WEBHOOK_URL,
            headers=headers,
            json=payload,
            timeout=130
        )
        
        if resp.status_code == 202:
            # 异步处理，需要轮询结果或使用回调
            result = resp.json()
            reply_text = result.get("response", "处理完成")
        elif resp.status_code == 200:
            result = resp.json()
            reply_text = result.get("response", result.get("message", "收到"))
        else:
            reply_text = f"OpenClaw返回错误: {resp.status_code}"
        
        # 回复飞书消息
        feishu_api.reply_message(message_id, reply_text)
        print(f"[回复] {reply_text[:100]}...")
        
    except Exception as e:
        error_msg = f"处理消息时出错: {str(e)}"
        print(f"[错误] {error_msg}")
        try:
            feishu_api.reply_message(message_id, error_msg)
        except:
            pass


def handle_message_event(event):
    """处理消息事件"""
    message = event.get("message", {})
    message_id = message.get("message_id")
    chat_id = message.get("chat_id")
    message_type = message.get("message_type")
    
    # 防止重复处理
    if message_id in processed_messages:
        return
    processed_messages.add(message_id)
    
    # 限制缓存大小
    if len(processed_messages) > 10000:
        processed_messages.clear()
    
    # 获取发送者信息
    sender = event.get("sender", {})
    sender_id = sender.get("sender_id", {}).get("user_id", "unknown")
    
    # 解析消息内容
    content = message.get("content", "{}")
    try:
        content_obj = json.loads(content)
        if message_type == "text":
            text = content_obj.get("text", "")
        else:
            text = f"[{message_type}消息]"
    except:
        text = content
    
    print(f"[收到消息] chat_id={chat_id}, sender={sender_id}, text={text[:50]}...")
    
    # 异步处理，避免超时
    thread = Thread(target=call_openclaw, args=(text, sender_id, chat_id, message_id))
    thread.start()


# ========== Flask路由 ==========
@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "service": "Feishu-OpenClaw Bridge",
        "status": "running",
        "endpoints": {
            "/webhook": "飞书事件订阅回调地址"
        }
    })


@app.route("/webhook", methods=["POST"])
def webhook():
    """飞书事件订阅回调"""
    data = request.json
    print(f"[Webhook] 收到请求: {json.dumps(data, ensure_ascii=False)[:200]}...")
    
    # 处理URL验证请求
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})
    
    # 验证token
    token = data.get("token")
    if token != FEISHU_VERIFICATION_TOKEN:
        print(f"[警告] Token验证失败")
        # 仍然返回200避免飞书重试
    
    # 处理事件
    header = data.get("header", {})
    event_type = header.get("event_type", "")
    event = data.get("event", {})
    
    if event_type == "im.message.receive_v1":
        # 收到消息事件
        handle_message_event(event)
    else:
        print(f"[忽略] 未处理的事件类型: {event_type}")
    
    return jsonify({"code": 0})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


# ========== 启动 ==========
if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           飞书 <-> OpenClaw 桥接服务                          ║
╠══════════════════════════════════════════════════════════════╣
║  端口: {PORT}                                                  
║  飞书回调URL: http://你的服务器:{PORT}/webhook                 
║  OpenClaw: {OPENCLAW_WEBHOOK_URL}                              
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 检查配置
    if FEISHU_APP_ID == "your_app_id":
        print("[警告] 请配置 FEISHU_APP_ID 环境变量")
    if FEISHU_APP_SECRET == "your_app_secret":
        print("[警告] 请配置 FEISHU_APP_SECRET 环境变量")
    if OPENCLAW_HOOK_TOKEN == "your_hook_token":
        print("[警告] 请配置 OPENCLAW_HOOK_TOKEN 环境变量")
    
    app.run(host="0.0.0.0", port=PORT, debug=False)
