#!/usr/bin/env node
/**
 * 飞书 Webhook 独立服务器
 * 接收飞书事件，转发给 OpenClaw
 */

const http = require('http');
const { replyMessage } = require('./scripts/feishu-api');

const PORT = process.env.FEISHU_PORT || 18790;
const VERIFICATION_TOKEN = process.env.FEISHU_VERIFICATION_TOKEN;
const OPENCLAW_URL = process.env.OPENCLAW_URL || 'http://localhost:18789';
const OPENCLAW_TOKEN = process.env.OPENCLAW_TOKEN || '';

const server = http.createServer(async (req, res) => {
  if (req.method !== 'POST') {
    res.writeHead(404);
    res.end('Not Found');
    return;
  }

  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', async () => {
    try {
      const data = JSON.parse(body);
      console.log('[feishu] Received:', JSON.stringify(data, null, 2));

      // 1. URL 验证 (challenge)
      if (data.type === 'url_verification') {
        console.log('[feishu] Challenge verification');
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ challenge: data.challenge }));
        return;
      }

      // 2. 验证 token
      if (data.token !== VERIFICATION_TOKEN) {
        console.error('[feishu] Invalid token');
        res.writeHead(401);
        res.end('Unauthorized');
        return;
      }

      // 3. 处理消息事件
      const eventType = data.header?.event_type;
      if (eventType === 'im.message.receive_v1') {
        const event = data.event;
        const message = event?.message;
        
        if (message) {
          let text = '';
          try {
            const content = JSON.parse(message.content);
            text = content.text || '';
          } catch (e) {}

          if (text.trim()) {
            const chatId = message.chat_id;
            const messageId = message.message_id;
            const senderId = event.sender?.sender_id?.user_id || 'unknown';

            console.log(`[feishu] Message from ${senderId}: ${text}`);

            // 调用 OpenClaw 处理消息
            processWithOpenClaw(text, chatId, messageId).catch(err => {
              console.error('[feishu] OpenClaw error:', err);
            });
          }
        }
      }

      // 快速返回 200，避免飞书超时
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ ok: true }));

    } catch (err) {
      console.error('[feishu] Parse error:', err);
      res.writeHead(400);
      res.end('Bad Request');
    }
  });
});

/**
 * 调用 OpenClaw 处理消息并回复
 */
async function processWithOpenClaw(text, chatId, messageId) {
  try {
    // 使用 OpenClaw HTTP API (chat completions)
    const response = await fetch(`${OPENCLAW_URL}/v1/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENCLAW_TOKEN}`
      },
      body: JSON.stringify({
        model: 'default',
        messages: [{ role: 'user', content: text }],
        stream: false
      })
    });

    if (!response.ok) {
      throw new Error(`OpenClaw API error: ${response.status}`);
    }

    const result = await response.json();
    const reply = result.choices?.[0]?.message?.content;

    if (reply) {
      console.log(`[feishu] Replying: ${reply.substring(0, 100)}...`);
      await replyMessage(messageId, reply);
    }
  } catch (err) {
    console.error('[feishu] Process error:', err);
    // 发送错误提示
    try {
      await replyMessage(messageId, '抱歉，处理消息时出错了，请稍后再试。');
    } catch (e) {}
  }
}

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[feishu] Webhook server listening on port ${PORT}`);
  console.log(`[feishu] Webhook URL: http://185.220.239.31:${PORT}/`);
});
