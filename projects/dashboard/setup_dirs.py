import os
from pathlib import Path

# 定义项目路径
base_dir = Path(r'C:\Users\Administrator\.openclaw\workspace\projects\dashboard')

# 创建目录结构
dirs = [
    base_dir,
    base_dir / 'data',
    base_dir / 'static',
    base_dir / 'scripts',
]

for d in dirs:
    d.mkdir(parents=True, exist_ok=True)
    print(f"Created: {d}")

print("\nDirectory structure created!")
