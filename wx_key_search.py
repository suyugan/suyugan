# -*- coding: utf-8 -*-
"""
Direct key search in WeChatAppEx process memory
Uses pywxdump's verify_key to validate candidates
With unbuffered output
"""
import sys
sys.stdout.reconfigure(line_buffering=True)
import ctypes
import ctypes.wintypes as wintypes
import os
import subprocess
import time

print(f"[{time.strftime('%H:%M:%S')}] Starting WeChat key extraction...")

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

# Import verify_key
from pywxdump.wx_core.utils import verify_key

# Target
active_account = 'wxid_izefflwcf2n822'
db_path = os.path.join('C:/Users/Administrator/Documents/WeChat Files', active_account, 'Msg', 'MicroMsg.db')
print(f"Target: {active_account}")
print(f"DB: {db_path} (exists: {os.path.exists(db_path)})")

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

print(f"PIDs: {pids}")

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

VirtualQueryEx = kernel32.VirtualQueryEx

def try_pid(pid):
    print(f"\n[{time.strftime('%H:%M:%S')}] === PID {pid} ===")
    h = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        print(f"  Cannot open")
        return None
    
    # Enumerate regions
    mbi = MBI64()
    addr = 0
    regions = []
    total = 0
    
    while addr < 0x7FFFFFFFFFFF:
        ret = VirtualQueryEx(ctypes.c_void_p(h), ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
        if ret == 0:
            break
        base = mbi.BaseAddress
        size = mbi.RegionSize
        if base == 0 and size == 0:
            break
        if mbi.State == MEM_COMMIT and size > 0 and size <= 50*1024*1024:
            prot = mbi.Protect
            # Readable pages
            if prot in (0x02, 0x04, 0x20, 0x40, 0x08):
                regions.append((base, size))
                total += size
        nxt = base + size
        if nxt <= addr:
            break
        addr = nxt
    
    print(f"  Regions: {len(regions)}, Total: {total/1024/1024:.1f}MB")
    
    # Search for key
    tested = 0
    for ri, (base, size) in enumerate(regions):
        try:
            buf = (ctypes.c_char * size)()
            br = ctypes.c_size_t(0)
            ok = kernel32.ReadProcessMemory(ctypes.c_void_p(h), ctypes.c_uint64(base), buf, size, ctypes.byref(br))
            if not ok:
                continue
            data = bytes(buf)[:br.value]
            
            # Scan for 32-byte key candidates
            # Step by 8 bytes (pointer-aligned)
            for i in range(0, len(data) - 32, 8):
                candidate = data[i:i+32]
                # Quick filters
                if candidate[0] == 0:
                    continue
                if candidate == b'\x00' * 32:
                    continue
                unique = len(set(candidate))
                if unique < 8:
                    continue
                    
                tested += 1
                if tested % 100000 == 0:
                    print(f"  [{time.strftime('%H:%M:%S')}] Tested {tested} candidates (region {ri}/{len(regions)})...")
                
                if verify_key(candidate, db_path):
                    kernel32.CloseHandle(ctypes.c_void_p(h))
                    return candidate.hex()
        except Exception as e:
            if ri < 3:
                print(f"  Region {ri} error: {e}")
            continue
    
    print(f"  Tested {tested} candidates, no match")
    kernel32.CloseHandle(ctypes.c_void_p(h))
    return None

# Try each PID
for pid in pids:
    key = try_pid(pid)
    if key:
        print(f"\n{'='*60}")
        print(f"SUCCESS! Key found: {key}")
        print(f"Account: {active_account}")
        print(f"{'='*60}")
        
        with open('wx_key.txt', 'w') as f:
            f.write(f"account={active_account}\nkey={key}\ndb_path={db_path}\n")
        
        sys.exit(0)

print(f"\n[{time.strftime('%H:%M:%S')}] No key found in any WeChatAppEx process.")
print("The new xwechat may not hold the key in plain memory.")
