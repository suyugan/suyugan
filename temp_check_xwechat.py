import sys
sys.stdout.reconfigure(encoding='utf-8')

# Try pywxdump's wx_core for new WeChat
from pywxdump import wx_core
print("wx_core functions:", [x for x in dir(wx_core) if not x.startswith('_')])

# Try BiasAddr for new WeChat
from pywxdump import BiasAddr
print("\nBiasAddr functions:", [x for x in dir(BiasAddr) if not x.startswith('_')])

# Check if there's xwechat support
import pywxdump
src_dir = pywxdump.__path__[0]
import os
for root, dirs, files in os.walk(src_dir):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
            if 'xwechat' in content.lower() or 'wechatappex' in content.lower():
                print(f'\nFound xwechat reference in: {fp}')
                for i, line in enumerate(content.split('\n')):
                    if 'xwechat' in line.lower() or 'wechatappex' in line.lower():
                        print(f'  Line {i}: {line.strip()[:100]}')
