"""
Check for WeChat config files that might contain or help derive the key.
Also check for any previously decrypted databases.
"""
import os
import glob
import json

base_dirs = [
    r"C:\Users\Administrator\Documents\WeChat Files",
    r"C:\Users\Administrator\AppData\Roaming\Tencent",
    r"C:\Users\Administrator\AppData\Local\Tencent",
]

# Check xInfo timestamps - wxid_izefflwcf2n822 has timestamps up to Feb 2026
# That means it's actively syncing/updating

# Look for any config files
print("=== Config files in WeChat Files dir ===")
for root, dirs, files in os.walk(r"C:\Users\Administrator\Documents\WeChat Files"):
    for f in files:
        if f.lower().endswith(('.ini', '.cfg', '.config', '.json', '.xml', '.dat', '.key')):
            full = os.path.join(root, f)
            size = os.path.getsize(full)
            if size < 10000:  # Small config files
                print(f"\n{full} ({size} bytes)")
                try:
                    with open(full, 'r', encoding='utf-8', errors='ignore') as fh:
                        content = fh.read()
                        print(content[:500])
                except:
                    with open(full, 'rb') as fh:
                        content = fh.read()
                        print(content[:200].hex())

print("\n\n=== Looking for WeChat installation in Program Files ===")
for p in [r"C:\Program Files\Tencent", r"C:\Program Files (x86)\Tencent", r"D:\Tencent"]:
    if os.path.exists(p):
        print(f"Found: {p}")
        for item in os.listdir(p):
            print(f"  {item}")

print("\n\n=== WeChat config in AppData ===")
for base in [r"C:\Users\Administrator\AppData\Roaming\Tencent", r"C:\Users\Administrator\AppData\Local\Tencent"]:
    if os.path.exists(base):
        print(f"\n{base}:")
        for root, dirs, files in os.walk(base):
            depth = root.count(os.sep) - base.count(os.sep)
            if depth > 3:
                dirs.clear()
                continue
            for f in files:
                full = os.path.join(root, f)
                try:
                    size = os.path.getsize(full)
                    print(f"  {os.path.relpath(full, base)} ({size} bytes)")
                except:
                    pass

print("\n\n=== Check for WeChatWin.dll (running version) ===")
# Look for DLL in standard install location
wechat_dll_paths = glob.glob(r"C:\Program Files*\Tencent\WeChat\*\WeChatWin.dll")
wechat_dll_paths += glob.glob(r"D:\WeChat\*\WeChatWin.dll")
wechat_dll_paths += glob.glob(r"D:\WeChat\**\WeChatWin.dll", recursive=True)
for p in wechat_dll_paths:
    print(f"Found: {p} ({os.path.getsize(p)} bytes)")
