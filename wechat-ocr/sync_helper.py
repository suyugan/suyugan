import requests, json, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# Get existing messages for dedup
r = requests.get('http://bm.weiixxin.com/wechat-text/api/messages/latest')
existing = r.json()
existing_set = set()
if isinstance(existing, list):
    for m in existing:
        key = f"{m.get('sender','')}__{m.get('content','')}"
        existing_set.add(key)

def push_messages(messages):
    """Push messages, skip duplicates"""
    new_msgs = []
    for m in messages:
        key = f"{m.get('sender','')}__{m.get('content','')}"
        if key not in existing_set:
            new_msgs.append(m)
            existing_set.add(key)
    if new_msgs:
        r = requests.post('http://bm.weiixxin.com/wechat-text/api/messages/batch', json={'messages': new_msgs})
        print(f"Pushed {len(new_msgs)} new messages, status: {r.status_code}")
        return len(new_msgs)
    else:
        print("All duplicates, skipped")
        return 0
    
def parse_ocr_text(text):
    """Parse OCR results into message objects"""
    messages = []
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('---') or line.startswith('**') or line.startswith('备注'):
            continue
        # Try to parse [time] sender: content format
        if ': ' in line:
            # Remove leading markers like numbers, bullets
            clean = line.lstrip('0123456789.-) ').lstrip('*').strip()
            if ': ' in clean:
                parts = clean.split(': ', 1)
                sender = parts[0].strip().lstrip('[').rstrip(']')
                content = parts[1].strip()
                # Remove time prefix from sender if present
                if '] ' in sender:
                    time_part, sender = sender.rsplit('] ', 1)
                messages.append({'sender': sender, 'content': content, 'time': ''})
    return messages

if __name__ == '__main__':
    # Test with sample
    test = """
[12:00] 豆包: @林杰 写小说的TOKEN使用量比写代码少太多了
[12:00] 豆包: 我会把你推成AI行业第一人的
"""
    msgs = parse_ocr_text(test)
    print(f"Parsed {len(msgs)} messages")
    for m in msgs:
        print(f"  {m['sender']}: {m['content'][:50]}")
