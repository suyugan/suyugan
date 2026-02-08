"""
Try various approaches to get WeChat DB key:
1. Check if pywxdump has stored keys from previous runs
2. Try to read the key from registry
3. Check for any config files with key info
"""
import os
import winreg
import json
import glob

print("=== Method 1: Check pywxdump cache/config ===")
pywxdump_paths = [
    os.path.expanduser("~/.pywxdump"),
    os.path.expanduser("~/pywxdump"),
    r"C:\Users\Administrator\AppData\Local\pywxdump",
    r"C:\Users\Administrator\AppData\Roaming\pywxdump",
]
for p in pywxdump_paths:
    if os.path.exists(p):
        print(f"Found: {p}")
        for root, dirs, files in os.walk(p):
            for f in files:
                print(f"  {os.path.join(root, f)}")
    else:
        print(f"Not found: {p}")

print("\n=== Method 2: Check WeChat registry keys ===")
reg_paths = [
    (winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tencent\WeChat"),
    (winreg.HKEY_CURRENT_USER, r"Software\Tencent\WXWork"),
]
for hkey, path in reg_paths:
    try:
        key = winreg.OpenKey(hkey, path)
        print(f"\nRegistry: {path}")
        i = 0
        while True:
            try:
                name, value, type_ = winreg.EnumValue(key, i)
                print(f"  {name} = {value} (type={type_})")
                i += 1
            except OSError:
                break
        winreg.CloseKey(key)
    except FileNotFoundError:
        print(f"Not found: {path}")

print("\n=== Method 3: Check for xInfo.db (may contain version info) ===")
xinfo_path = r"C:\Users\Administrator\Documents\WeChat Files\wxid_mqiv7irec7ee21\Msg\xInfo.db"
try:
    with open(xinfo_path, 'rb') as f:
        header = f.read(32)
        print(f"xInfo.db header (hex): {header.hex()}")
        print(f"xInfo.db header (ascii): {header}")
except Exception as e:
    print(f"Error reading xInfo.db: {e}")

print("\n=== Method 4: Check WeChat version from exe ===")
wechat_exe_paths = [
    r"C:\Program Files\Tencent\WeChat\WeChat.exe",
    r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
]
for p in wechat_exe_paths:
    if os.path.exists(p):
        print(f"Found WeChat exe: {p}")
        print(f"Size: {os.path.getsize(p)} bytes")

# Also check install dir from registry
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat")
    install_path, _ = winreg.QueryValueEx(key, "InstallPath")
    print(f"Install path from registry: {install_path}")
    winreg.CloseKey(key)
except:
    pass

print("\n=== Method 5: Check DB file headers ===")
db_files = [
    r"C:\Users\Administrator\Documents\WeChat Files\wxid_mqiv7irec7ee21\Msg\MicroMsg.db",
    r"C:\Users\Administrator\Documents\WeChat Files\wxid_mqiv7irec7ee21\Msg\Multi\MSG0.db",
]
for db_path in db_files:
    try:
        with open(db_path, 'rb') as f:
            header = f.read(16)
            print(f"{os.path.basename(db_path)} header: {header.hex()}")
            # SQLite magic: 53514C69746520666F726D617420330000
            # SQLCipher: random bytes (encrypted)
            if header[:6] == b'SQLite':
                print("  -> Standard SQLite (not encrypted)")
            else:
                print("  -> Encrypted (SQLCipher)")
    except Exception as e:
        print(f"Error: {e}")
