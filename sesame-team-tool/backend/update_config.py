import json
import io
import sys
from pathlib import Path

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 使用 Path 处理路径
base_dir = Path(r'C:\Users\Administrator\.openclaw\workspace\sesame-team-tool\backend')
cookies_file = base_dir / 'cookies.txt'
config_file = Path(r'C:\Users\Administrator\.openclaw\video-analysis-python\config.json')

print("=" * 50)
print("  Update Backend Config")
print("=" * 50)
print()

# 读取 cookies
if cookies_file.exists():
    with open(cookies_file, 'r', encoding='utf-8') as f:
        cookies = f.read().strip()

    print(f"Read cookies (length: {len(cookies)})")
    print()
else:
    print(f"Error: cookies.txt not found at {cookies_file}")
    sys.exit(1)

# 读取 config.json
if config_file.exists():
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
else:
    print(f"Error: config.json not found at {config_file}")
    sys.exit(1)

# 更新 cookies
config['cookies'] = cookies

# 保存 config.json
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"Updated cookies in: {config_file}")
print()

print("=" * 50)
print("  Config updated successfully!")
print("=" * 50)
print()

print("New config:")
print(json.dumps(config, indent=2, ensure_ascii=False))
