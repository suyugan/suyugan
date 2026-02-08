import re, json, uuid, datetime

messages = []
with open(r'C:\Users\Administrator\.openclaw\workspace\wechat-ocr\messages.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

group_name = '跟不上ai发展你睡得着吗?'
base_date = '2026-02-08'
order = 0

for line in lines:
    line = line.strip()
    if not line or line.startswith('微信群聊') or line.startswith('群名') or line.startswith('提取') or line.startswith('===') or line.startswith('共识别') or line.startswith('注意') or line.startswith('---'):
        continue
    
    # Match [time] sender: content
    m = re.match(r'\[([^\]]+)\]\s+(.+?):\s+(.*)', line)
    if not m:
        continue
    
    time_str, sender, content = m.group(1), m.group(2).strip(), m.group(3).strip()
    
    # Build timestamp
    if re.match(r'\d{2}:\d{2}$', time_str):
        ts = f'{base_date}T{time_str}:00'
    else:
        ts = f'{base_date}T00:00:{order:02d}'
    
    # Determine type
    msg_type = 'text'
    media_url = None
    if '[图片]' in content:
        msg_type = 'image'
    elif '[分享链接]' in content:
        msg_type = 'link'
    
    if sender == '未知发送者':
        sender = '未知'
    
    order += 1
    messages.append({
        'id': str(uuid.uuid4()),
        'group_name': group_name,
        'sender': sender,
        'content': content,
        'msg_type': msg_type,
        'media_url': media_url,
        'timestamp': ts
    })

# Write as JSON for import
with open(r'C:\Users\Administrator\.openclaw\workspace\projects\wechat-text-viewer\import_data.json', 'w', encoding='utf-8') as f:
    json.dump(messages, f, ensure_ascii=False, indent=2)

print(f'Parsed {len(messages)} messages')
