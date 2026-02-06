/**
 * 飞书 Webhook 事件转换器
 * 将飞书事件转换为 OpenClaw 消息格式
 */

/**
 * OpenClaw hook transform 入口
 * @param {object} ctx - { body, headers, query }
 * @returns {object|null} - { message, sessionKey?, name?, deliver?, channel?, to? }
 */
module.exports = async function transform(ctx) {
  const { body } = ctx;

  console.log('[feishu-transform] Received:', JSON.stringify(body).substring(0, 300));

  // 处理 v2 格式事件
  if (body.schema === '2.0' && body.header) {
    const eventType = body.header.event_type;
    
    // 只处理消息事件
    if (eventType !== 'im.message.receive_v1') {
      console.log('[feishu-transform] Ignored event:', eventType);
      return null;
    }

    const event = body.event;
    if (!event || !event.message) return null;

    const message = event.message;
    
    // 提取消息内容
    let text = '';
    try {
      const content = JSON.parse(message.content);
      text = content.text || '';
    } catch (e) {
      console.error('[feishu-transform] Failed to parse message content:', e);
      return null;
    }

    // 忽略空消息
    if (!text.trim()) return null;

    const sender = event.sender;
    const senderId = sender?.sender_id?.open_id || 'unknown';
    const chatId = message.chat_id;

    console.log(`[feishu-transform] Message from ${senderId}: ${text}`);

    // 构造 OpenClaw webhook agent 消息格式
    return {
      message: text,
      name: 'Feishu',
      sessionKey: `hook:feishu:${chatId}`,
      deliver: false,  // 暂不自动投递回复
      wakeMode: 'now'
    };
  }

  // 处理 v1 格式事件
  if (body.event && body.event.message) {
    const message = body.event.message;
    
    let text = '';
    try {
      const content = JSON.parse(message.content);
      text = content.text || '';
    } catch (e) {
      return null;
    }

    if (!text.trim()) return null;

    const chatId = message.chat_id;
    console.log(`[feishu-transform] v1 Message: ${text}`);

    return {
      message: text,
      name: 'Feishu',
      sessionKey: `hook:feishu:${chatId}`,
      deliver: false,
      wakeMode: 'now'
    };
  }

  console.log('[feishu-transform] Unknown format, returning null');
  return null;
};
