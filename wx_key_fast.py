# -*- coding: utf-8 -*-
"""
Fast key search using pywxdump's own get_key_by_mem_search
Modified to work with WeChatAppEx processes
"""
import sys
sys.stdout.reconfigure(line_buffering=True)
import os
import time
import subprocess

print(f"[{time.strftime('%H:%M:%S')}] Starting...")

# Get PIDs
result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq WeChatAppEx.exe', '/FO', 'CSV', '/NH'],
                       capture_output=True, text=True)
pids = []
for line in result.stdout.strip().split('\n'):
    parts = line.strip().split(',')
    if len(parts) >= 2:
        try:
            pids.append(int(parts[1].strip('"')))
        except:
            pass

print(f"WeChatAppEx PIDs: {pids}")

active_account = 'wxid_izefflwcf2n822'
wx_dir = f'C:\\Users\\Administrator\\Documents\\WeChat Files\\{active_account}'
db_path = os.path.join(wx_dir, 'Msg', 'MicroMsg.db')
print(f"Target: {active_account}")
print(f"DB exists: {os.path.exists(db_path)}")

from pywxdump.wx_core.wx_info import get_key_by_mem_search

# The function signature: get_key_by_mem_search(pid, db_path, addr_len)
# db_path should be the wxid directory (it will append MSG/MicroMsg.db internally)
# Actually let me check... it uses os.path.join(db_path, "MSG", "MicroMsg.db")
# So db_path should be the wxid dir

for pid in pids:
    print(f"\n[{time.strftime('%H:%M:%S')}] Trying PID {pid} with get_key_by_mem_search...")
    try:
        key = get_key_by_mem_search(pid, wx_dir, 8)  # 8 = 64-bit address length
        if key:
            print(f"\n*** FOUND KEY: {key} ***")
            with open('wx_key.txt', 'w') as f:
                f.write(f"account={active_account}\nkey={key}\nwx_dir={wx_dir}\n")
            sys.exit(0)
        else:
            print(f"  No key found in PID {pid}")
    except Exception as e:
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()

print(f"\n[{time.strftime('%H:%M:%S')}] get_key_by_mem_search failed for all PIDs.")
print("Trying alternative: direct memory search for key bytes...")

# Alternative: Read the first page of the encrypted DB and try to find key by brute force
# SQLCipher uses PBKDF2, but WeChat uses raw key without PBKDF2
# The first 16 bytes of the encrypted file are salt, followed by encrypted data
# The encryption is AES-256-CBC with HMAC

# Let's try to use the verify_key function directly
from pywxdump.wx_core.utils import verify_key
import ctypes
import ctypes.wintypes as wintypes

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

class MBI64(ctypes.Structure):
    _fields_ = [
        ('BaseAddress', ctypes.c_uint64),
        ('AllocationBase', ctypes.c_uint64),
        ('AllocationProtect', ctypes.c_uint32),
        ('_pad1', ctypes.c_uint32),
        ('RegionSize', ctypes.c_uint64),
        ('State', ctypes.c_uint32),
        ('Protect', ctypes.c_uint32),
        ('Type', ctypes.c_uint32),
        ('_pad2', ctypes.c_uint32),
    ]

# Find the process with the most memory (likely main WeChatAppEx)
for pid in pids:
    print(f"\n[{time.strftime('%H:%M:%S')}] Scanning PID {pid} memory for key...")
    h = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        continue
    
    mbi = MBI64()
    addr = 0
    
    # First pass: find regions that contain "android" or "iphone" or the wxid
    target_regions = []
    
    while addr < 0x7FFFFFFFFFFF:
        ret = kernel32.VirtualQueryEx(ctypes.c_void_p(h), ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
        if ret == 0 or (mbi.BaseAddress == 0 and mbi.RegionSize == 0):
            break
        
        base = mbi.BaseAddress
        size = mbi.RegionSize
        
        if mbi.State == MEM_COMMIT and size > 0 and size <= 50*1024*1024:
            prot = mbi.Protect
            if prot in (0x02, 0x04, 0x20, 0x40, 0x08):
                try:
                    buf = (ctypes.c_char * size)()
                    br = ctypes.c_size_t(0)
                    if kernel32.ReadProcessMemory(ctypes.c_void_p(h), ctypes.c_uint64(base), buf, size, ctypes.byref(br)):
                        data = bytes(buf)[:br.value]
                        # Check if this region contains phone type or wxid markers
                        has_marker = False
                        for marker in [b'android\x00', b'iphone\x00', b'ipad\x00']:
                            if marker in data:
                                has_marker = True
                                # Find marker positions
                                idx = 0
                                while True:
                                    pos = data.find(marker, idx)
                                    if pos == -1:
                                        break
                                    target_regions.append((base, size, data, base + pos, marker))
                                    idx = pos + 1
                                break
                except:
                    pass
        
        nxt = base + size
        if nxt <= addr:
            break
        addr = nxt
    
    print(f"  Found {len(target_regions)} marker positions")
    
    if target_regions:
        # For each marker, search backwards for key pointer
        for base, size, data, marker_addr, marker in target_regions:
            offset_in_data = marker_addr - base
            
            # Search backward from marker for pointer to key
            for off in range(0, min(2000, offset_in_data), 8):
                ptr_pos = offset_in_data - off
                if ptr_pos < 0:
                    break
                    
                # Read 8 bytes as pointer
                ptr_bytes = data[ptr_pos:ptr_pos+8]
                if len(ptr_bytes) < 8:
                    continue
                ptr_val = int.from_bytes(ptr_bytes, 'little')
                
                if ptr_val < 0x10000 or ptr_val > 0x7FFFFFFFFFFF:
                    continue
                
                # Dereference pointer to read 32-byte key
                key_buf = (ctypes.c_char * 32)()
                if kernel32.ReadProcessMemory(ctypes.c_void_p(h), ctypes.c_uint64(ptr_val), key_buf, 32, None) == 0:
                    continue
                
                key_bytes = bytes(key_buf)
                if key_bytes == b'\x00' * 32 or len(set(key_bytes)) < 5:
                    continue
                
                if verify_key(key_bytes, db_path):
                    kernel32.CloseHandle(ctypes.c_void_p(h))
                    key_hex = key_bytes.hex()
                    print(f"\n*** FOUND KEY: {key_hex} ***")
                    with open('wx_key.txt', 'w') as f:
                        f.write(f"account={active_account}\nkey={key_hex}\nwx_dir={wx_dir}\n")
                    sys.exit(0)
        
        print(f"  Key not found near markers")
    
    kernel32.CloseHandle(ctypes.c_void_p(h))

print(f"\n[{time.strftime('%H:%M:%S')}] All methods failed.")
print("The new WeChat (xwechat) architecture may not expose the key in process memory.")
print("Possible alternatives:")
print("1. Use an older WeChat version (3.9.x with WeChat.exe)")
print("2. Use HookWeChatKey or similar injection tool")
print("3. Check if there's a decrypted key cached somewhere on disk")
