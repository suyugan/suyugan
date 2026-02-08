import sys, requests, re
sys.stdout.reconfigure(encoding='utf-8')
r = requests.get('https://jimeng.jianying.com/ai-tool/home', headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
urls = re.findall(r'https?://[^\s"\']+\.exe[^\s"\']*', r.text)
print('EXE links:', urls[:5])
urls2 = re.findall(r'https?://[^\s"\']+download[^\s"\']*', r.text, re.IGNORECASE)
print('Download links:', urls2[:10])
# Check for Windows client links
urls3 = re.findall(r'https?://[^\s"\']+(?:win|windows|client|desktop|setup|install)[^\s"\']*', r.text, re.IGNORECASE)
print('Client links:', urls3[:10])
