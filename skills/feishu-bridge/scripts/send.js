#!/usr/bin/env node
/**
 * 手动发送飞书消息
 * Usage: node send.js <chat_id> <message>
 */

const { sendMessage } = require('./feishu-api');

async function main() {
  const [,, chatId, ...messageParts] = process.argv;
  const message = messageParts.join(' ');

  if (!chatId || !message) {
    console.log('Usage: node send.js <chat_id> <message>');
    console.log('Example: node send.js oc_xxx "Hello from OpenClaw!"');
    process.exit(1);
  }

  try {
    const result = await sendMessage(chatId, message);
    console.log('✅ 消息发送成功:', result.message_id);
  } catch (err) {
    console.error('❌ 发送失败:', err.message);
    process.exit(1);
  }
}

main();
