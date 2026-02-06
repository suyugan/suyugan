/**
 * 飞书 API 封装
 */

const https = require('https');
const http = require('http');

const APP_ID = process.env.FEISHU_APP_ID || 'cli_a90f5a7ee979dbef';
const APP_SECRET = process.env.FEISHU_APP_SECRET || 'AMnZ3JosdeIamSXn8BBzZcCXCpfpIMV4';

let tenantAccessToken = null;
let tokenExpireAt = 0;

/**
 * 获取 tenant_access_token
 */
async function getTenantAccessToken() {
  if (tenantAccessToken && Date.now() < tokenExpireAt) {
    return tenantAccessToken;
  }

  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      app_id: APP_ID,
      app_secret: APP_SECRET
    });

    const req = https.request({
      hostname: 'open.feishu.cn',
      path: '/open-apis/auth/v3/tenant_access_token/internal',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          if (result.code === 0) {
            tenantAccessToken = result.tenant_access_token;
            tokenExpireAt = Date.now() + (result.expire - 300) * 1000; // 提前5分钟刷新
            console.log('[feishu-api] Got tenant_access_token');
            resolve(tenantAccessToken);
          } else {
            console.error('[feishu-api] Failed to get token:', result);
            reject(new Error(result.msg));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * 发送消息到聊天
 */
async function sendMessage(chatId, text) {
  const token = await getTenantAccessToken();

  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      receive_id: chatId,
      msg_type: 'text',
      content: JSON.stringify({ text })
    });

    const req = https.request({
      hostname: 'open.feishu.cn',
      path: '/open-apis/im/v1/messages?receive_id_type=chat_id',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Content-Length': Buffer.byteLength(data)
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          if (result.code === 0) {
            console.log('[feishu-api] Message sent successfully');
            resolve(result);
          } else {
            console.error('[feishu-api] Failed to send message:', result);
            reject(new Error(result.msg));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * 回复消息
 */
async function replyMessage(messageId, text) {
  const token = await getTenantAccessToken();

  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      msg_type: 'text',
      content: JSON.stringify({ text })
    });

    const req = https.request({
      hostname: 'open.feishu.cn',
      path: `/open-apis/im/v1/messages/${messageId}/reply`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Content-Length': Buffer.byteLength(data)
      }
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const result = JSON.parse(body);
          if (result.code === 0) {
            console.log('[feishu-api] Reply sent successfully');
            resolve(result);
          } else {
            console.error('[feishu-api] Failed to reply:', result);
            reject(new Error(result.msg));
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

module.exports = {
  getTenantAccessToken,
  sendMessage,
  replyMessage
};
