/**
 * 飞书 Webhook 代理服务器
 * 支持文本和图片消息
 */

const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const { sendMessage, getTenantAccessToken } = require('./feishu-api');

// 图片保存目录
const IMAGE_DIR = 'C:\\Users\\Administrator\\.openclaw\\media\\feishu';
if (!fs.existsSync(IMAGE_DIR)) {
  fs.mkdirSync(IMAGE_DIR, { recursive: true });
}

// 配置
const PORT = process.env.FEISHU_PROXY_PORT || 8100;
const VERIFICATION_TOKEN = 'jiLWjgdWx668PcNGxK7dwbsE004XPjuT';
const GATEWAY_TOKEN = 'ec5138a325fd81f25b928ce9707b2901fb71c9987f048c7d';

// 记录已处理的消息ID
const processedMessages = new Set();
// 对话历史
const chatHistories = new Map();

console.log(`[feishu-proxy] Starting on port ${PORT}`);

const server = http.createServer((req, res) => {
  if (req.method !== 'POST') {
    res.writeHead(405, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Method not allowed' }));
    return;
  }

  let body = '';
  req.on('data', chunk => body += chunk);
  req.on('end', async () => {
    try {
      const data = JSON.parse(body);
      
      // URL 验证
      if (data.type === 'url_verification') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ challenge: data.challenge }));
        return;
      }

      // 立即返回
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ code: 0 }));

      // 验证 token
      const token = data.token || (data.header && data.header.token);
      if (token !== VERIFICATION_TOKEN) return;

      // 提取消息
      if (data.schema !== '2.0' || !data.header) return;
      if (data.header.event_type !== 'im.message.receive_v1') return;
      
      const eventId = data.header.event_id;
      const message = data.event?.message;
      if (!message) return;

      const chatId = message.chat_id;
      const messageType = message.message_type;

      // 防止重复
      if (processedMessages.has(eventId)) return;
      processedMessages.add(eventId);
      if (processedMessages.size > 100) {
        processedMessages.delete(processedMessages.values().next().value);
      }

      // 解析消息内容
      let userContent = [];
      let logText = '';

      if (messageType === 'text') {
        try {
          const content = JSON.parse(message.content);
          if (content.text) {
            userContent.push({ type: 'text', text: content.text });
            logText = content.text;
          }
        } catch (e) {}
      } else if (messageType === 'image') {
        try {
          const content = JSON.parse(message.content);
          const imageKey = content.image_key;
          if (imageKey) {
            console.log(`[feishu-proxy] Downloading image: ${imageKey}`);
            const imageData = await downloadImage(message.message_id, imageKey);
            if (imageData) {
              // 保存图片到本地文件
              const imagePath = path.join(IMAGE_DIR, `${imageKey}.png`);
              fs.writeFileSync(imagePath, Buffer.from(imageData, 'base64'));
              console.log(`[feishu-proxy] Image saved: ${imagePath}`);
              
              // 告诉AI图片路径，让它用image工具分析
              userContent.push({
                type: 'text',
                text: `[用户发送了一张图片，已保存到: ${imagePath}]\n请用image工具分析这张图片，然后回复用户。`
              });
              logText = '[图片]';
            }
          }
        } catch (e) {
          console.error(`[feishu-proxy] Image error:`, e.message);
        }
      } else if (messageType === 'post') {
        // 富文本消息
        try {
          const content = JSON.parse(message.content);
          // 提取纯文本
          let text = '';
          if (content.content) {
            for (const para of content.content) {
              for (const elem of para) {
                if (elem.tag === 'text') {
                  text += elem.text || '';
                } else if (elem.tag === 'a') {
                  text += elem.text || elem.href || '';
                }
              }
              text += '\n';
            }
          }
          text = text.trim();
          if (text) {
            userContent.push({ type: 'text', text: text });
            logText = text.substring(0, 50);
          }
        } catch (e) {
          console.error(`[feishu-proxy] Post parse error:`, e.message);
        }
      } else {
        console.log(`[feishu-proxy] Unsupported message type: ${messageType}`);
        return;
      }

      if (userContent.length === 0) return;

      console.log(`[feishu-proxy] Message: ${logText}`);

      // 对话历史
      if (!chatHistories.has(chatId)) {
        chatHistories.set(chatId, []);
      }
      const history = chatHistories.get(chatId);
      history.push({ role: 'user', content: userContent });
      while (history.length > 20) history.shift();

      try {
        console.log(`[feishu-proxy] Calling OpenClaw...`);
        const reply = await callOpenClawChat(history, chatId);
        
        if (reply && reply !== 'NO_REPLY' && reply !== 'HEARTBEAT_OK') {
          history.push({ role: 'assistant', content: reply });
          console.log(`[feishu-proxy] Reply: ${reply.substring(0, 50)}...`);
          await sendMessage(chatId, reply);
          console.log(`[feishu-proxy] ✅ Sent to Feishu`);
        }
      } catch (err) {
        console.error(`[feishu-proxy] Error:`, err.message);
        try {
          await sendMessage(chatId, `抱歉，出错了：${err.message}`);
        } catch (e) {}
      }

    } catch (err) {
      console.error(`[feishu-proxy] Parse error:`, err.message);
    }
  });
});

/**
 * 下载飞书图片
 */
async function downloadImage(messageId, imageKey) {
  const token = await getTenantAccessToken();
  
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'open.feishu.cn',
      path: `/open-apis/im/v1/messages/${messageId}/resources/${imageKey}?type=image`,
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }, (res) => {
      console.log(`[feishu-proxy] Image download response: ${res.statusCode}`);
      
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => {
        const buffer = Buffer.concat(chunks);
        
        // 检查是否是JSON错误响应
        if (res.statusCode !== 200) {
          try {
            const errData = JSON.parse(buffer.toString());
            console.error(`[feishu-proxy] Image download error:`, JSON.stringify(errData));
          } catch (e) {
            console.error(`[feishu-proxy] Image download failed: ${res.statusCode}`);
          }
          resolve(null);
          return;
        }
        
        console.log(`[feishu-proxy] Image downloaded: ${buffer.length} bytes`);
        resolve(buffer.toString('base64'));
      });
    });
    
    req.on('error', (e) => {
      console.error(`[feishu-proxy] Image download error:`, e.message);
      resolve(null);
    });
    req.end();
  });
}

/**
 * 调用 OpenClaw Chat API
 */
function callOpenClawChat(messages, chatId) {
  return new Promise((resolve, reject) => {
    const payload = {
      model: 'openclaw:main',
      messages: messages,
      stream: false
    };
    const data = JSON.stringify(payload);
    
    const req = http.request({
      hostname: '127.0.0.1',
      port: 18789,
      path: '/v1/chat/completions',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${GATEWAY_TOKEN}`,
        'x-openclaw-session-key': `feishu:${chatId}`
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          if (result.choices?.[0]?.message?.content) {
            resolve(result.choices[0].message.content);
          } else if (result.error) {
            reject(new Error(result.error.message || 'API error'));
          } else {
            reject(new Error('Unexpected response'));
          }
        } catch (e) {
          reject(e);
        }
      });
    });
    
    req.on('error', reject);
    req.setTimeout(120000, () => {
      req.destroy();
      reject(new Error('Timeout'));
    });
    req.write(data);
    req.end();
  });
}

server.listen(PORT, '0.0.0.0', () => {
  console.log(`[feishu-proxy] ✅ Listening on http://0.0.0.0:${PORT}`);
});
