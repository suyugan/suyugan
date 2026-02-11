import re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'D:\laolin-showcase.html', 'r', encoding='utf-8') as f:
    html = f.read()

body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL)
if body_match:
    body = body_match.group(1)
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
    body = re.sub(r'(<svg[^>]*>).*?(</svg>)', r'\1...\2', body, flags=re.DOTALL)
    # Remove data attributes
    body = re.sub(r'\s+data-[a-z-]+="[^"]*"', '', body)
    # Remove long style attributes
    body = re.sub(r'\s+style="[^"]{200,}"', ' style="..."', body)
    with open(r'D:\laolin-structure.txt', 'w', encoding='utf-8') as f:
        f.write(body[:15000])
    print(f"Written structure, {len(body)} chars total")
