import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD')

stdin, stdout, stderr = ssh.exec_command('cat /home/ubuntu/wechat-sync/frontend/index.html')
html = stdout.read().decode()

old_block = """      let text = m.content || '';
      if (m.msg_type === 49 && m.title) text = `[${m.title}]`;
      else if (m.msg_type === 3) text = '[ͼƬ]';
      else if (m.msg_type === 34) text = '[����]';
      else if (m.msg_type === 43) text = '[��Ƶ]';
      else if (m.msg_type === 47) text = '[����]';
      else if (m.msg_type === 48) text = '[λ��]';
      else if (m.msg_type === 42) text = '[��Ƭ]';
      else if (m.msg_type >= 10000) text = '[ϵͳ��Ϣ]';
      if (text.length > 200) text = text.slice(0, 200) + '...';"""

new_block = """      let text = parseContent(m);
      if (text.length > 300) text = text.slice(0, 300) + '...';"""

if old_block in html:
    html = html.replace(old_block, new_block)
    print("Replaced message rendering block")
else:
    print("ERROR: old block not found, trying fuzzy match...")
    # Try line by line
    lines = html.split('\n')
    new_lines = []
    skip_until = -1
    for i, line in enumerate(lines):
        if i < skip_until:
            continue
        if 'let text = m.content' in line:
            new_lines.append('      let text = parseContent(m);')
            # Skip until the text.length line
            j = i + 1
            while j < len(lines) and 'text.length' not in lines[j]:
                j += 1
            if j < len(lines):
                new_lines.append("      if (text.length > 300) text = text.slice(0, 300) + '...';")
                skip_until = j + 1
            else:
                skip_until = -1
            print(f"Fuzzy replaced lines {i} to {j}")
            continue
        new_lines.append(line)
    html = '\n'.join(new_lines)

# Also change escapeHtml(text) to just text for parsed HTML content (links etc)
html = html.replace('${escapeHtml(text)}</div>', '${text}</div>')

stdin, stdout, stderr = ssh.exec_command('cat > /home/ubuntu/wechat-sync/frontend/index.html', bufsize=-1)
stdin.write(html)
stdin.channel.shutdown_write()
print("Written", len(html), "bytes")
print(stderr.read().decode())

# Verify
stdin, stdout, stderr = ssh.exec_command('grep -c "parseContent" /home/ubuntu/wechat-sync/frontend/index.html')
print("parseContent count:", stdout.read().decode().strip())
ssh.close()
