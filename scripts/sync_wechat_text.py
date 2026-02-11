"""
从 https://laolin.ai/showcase 抓取群聊消息，推送到文字版网页
"""
import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
import requests
from datetime import datetime

def fetch_messages():
    """抓取 showcase 页面的群聊消息"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('https://laolin.ai/showcase', timeout=30000)
        page.wait_for_timeout(8000)
        
        text = page.inner_text('body')
        browser.close()
    return text

def parse_messages(text):
    """解析消息文本为结构化数据"""
    messages = []
    lines = text.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # 尝试匹配时间格式 HH:MM:SS
        time_match = re.match(r'^(\d{2}:\d{2}:\d{2})$', line)
        if time_match and i > 0:
            sender = lines[i-1].strip() if i > 0 else '未知'
            timestamp = time_match.group(1)
            
            # 往后找内容
            content_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    break
                if re.match(r'^\d{2}:\d{2}:\d{2}$', next_line):
                    break
                content_lines.append(next_line)
                i += 1
            
            content = '\n'.join(content_lines) if content_lines else ''
            
            msg_type = 'text'
            if '🖼️ 图片' in content:
                msg_type = 'image'
            elif '😊 表情' in content:
                msg_type = 'text'
                content = '[表情]'
            
            if content and sender:
                today = datetime.now().strftime('%Y-%m-%d')
                messages.append({
                    'sender': sender,
                    'content': content,
                    'msg_type': msg_type,
                    'group_name': '跟不上ai的发展你睡得着吗？',
                    'timestamp': f'{today}T{timestamp}',
                    'media_url': None
                })
        else:
            i += 1
    
    return messages

def get_existing_messages():
    """获取已有消息用于去重"""
    try:
        r = requests.get('http://bm.weiixxin.com/wechat-text/api/messages?limit=200')
        if r.status_code == 200:
            data = r.json()
            return data.get('messages', [])
    except:
        pass
    return []

def push_messages(messages):
    """推送消息到文字版网页"""
    if not messages:
        print('没有新消息需要推送')
        return 0
    
    count = 0
    for msg in messages:
        try:
            r = requests.post('http://bm.weiixxin.com/wechat-text/api/messages', json=msg)
            if r.status_code == 200:
                count += 1
        except Exception as e:
            print(f'推送失败: {e}')
    
    return count

def main():
    print('=== 群聊消息同步 ===')
    
    print('正在抓取 showcase 页面...')
    text = fetch_messages()
    print(f'抓取到 {len(text)} 字符')
    
    messages = parse_messages(text)
    print(f'解析出 {len(messages)} 条消息')
    
    existing = get_existing_messages()
    existing_set = set()
    for m in existing:
        key = f"{m.get('sender','')}|{m.get('content','')}"
        existing_set.add(key)
    
    new_messages = []
    for m in messages:
        key = f"{m['sender']}|{m['content']}"
        if key not in existing_set:
            new_messages.append(m)
    
    print(f'去重后 {len(new_messages)} 条新消息')
    
    if new_messages:
        count = push_messages(new_messages)
        print(f'成功推送 {count} 条消息')
    else:
        print('没有新消息')
    
    return len(new_messages)

if __name__ == '__main__':
    main()
