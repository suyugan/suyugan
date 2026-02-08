# -*- coding: utf-8 -*-
"""
Extract WeChat key from WeChatAppEx process memory.
"""
import ctypes
import ctypes.wintypes as wintypes
import os
import sys

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_READWRITE = 0x04
PAGE_READONLY = 0x02
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

class MEMORY_BASIC_INFORMATION64(ctypes.Structure):
    _fields_ = [
        ('BaseAddress', ctypes.c_uint64),
        ('AllocationBase', ctypes.c_uint64),
        ('AllocationProtect', ctypes.c_uint32),
        ('__alignment1', ctypes.c_uint32),
        ('RegionSize', ctypes.c_uint64),
        ('State', ctypes.c_uint32),
        ('Protect', ctypes.c_uint32),
        ('Type', ctypes.c_uint32),
        ('__alignment2', ctypes.c_uint32),
    ]

from pywxdump.wx_core.utils import verify_key

def get_process_pids(name):
    import subprocess
    result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {name}', '/FO', 'CSV', '/NH'], 
                          capture_output=True, text=True)
    pids = []
    for line in result.stdout.strip().split('\n'):
        if line.strip():
            parts = line.strip().split(',')
            if len(parts) >= 2:
                pid_str = parts[1].strip('"')
                try:
                    pids.append(int(pid_str))
                except:
                    pass
    return pids

def enum_memory_regions(h_process):
    """Enumerate readable committed memory regions"""
    regions = []
    mbi = MEMORY_BASIC_INFORMATION64()
    address = 0
    readable_protects = {PAGE_READWRITE, PAGE_READONLY, PAGE_EXECUTE_READ, PAGE_EXECUTE_READWRITE, 0x02, 0x04, 0x20, 0x40}
    
    VirtualQueryEx = kernel32.VirtualQueryEx
    
    while address < 0x00007FFFFFFFFFFF:
        result = VirtualQueryEx(
            ctypes.c_void_p(h_process),
            ctypes.c_void_p(address),
            ctypes.byref(mbi),
            ctypes.sizeof(mbi)
        )
        if result == 0:
            break
        
        base = mbi.BaseAddress
        size = mbi.RegionSize
        
        if base == 0 and size == 0:
            break
            
        if mbi.State == MEM_COMMIT and mbi.Protect in readable_protects and size > 0:
            regions.append((base, size))
        
        next_addr = base + size
        if next_addr <= address:
            break
        address = next_addr
    
    return regions

def search_memory_for_key(pid, db_path):
    """Search WeChatAppEx process memory for the encryption key"""
    h_process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h_process:
        print(f"  Cannot open process {pid}")
        return None
    
    print(f"  Opened process {pid}")
    
    regions = enum_memory_regions(h_process)
    print(f"  Found {len(regions)} readable memory regions")
    total_size = sum(s for _, s in regions)
    print(f"  Total readable memory: {total_size / 1024 / 1024:.1f} MB")
    
    # Strategy 1: Search for phone type markers (android/iphone)
    phone_patterns = [b'android\x00', b'iphone\x00', b'ipad\x00']
    found_addrs = []
    
    for base, size in regions:
        if size > 100 * 1024 * 1024:
            continue
        try:
            buf = (ctypes.c_char * size)()
            bytes_read = ctypes.c_size_t(0)
            if kernel32.ReadProcessMemory(ctypes.c_void_p(h_process), ctypes.c_void_p(base), buf, size, ctypes.byref(bytes_read)):
                data = bytes(buf)[:bytes_read.value]
                for pattern in phone_patterns:
                    idx = 0
                    while idx < len(data):
                        pos = data.find(pattern, idx)
                        if pos == -1:
                            break
                        found_addrs.append(base + pos)
                        idx = pos + len(pattern)
        except Exception as e:
            continue
    
    print(f"  Found {len(found_addrs)} phone type markers")
    
    # For each marker, search backwards for key pointer
    for addr in found_addrs:
        for offset in range(0, 2000, 8):
            try:
                ptr_buf = (ctypes.c_char * 8)()
                if kernel32.ReadProcessMemory(ctypes.c_void_p(h_process), ctypes.c_void_p(addr - offset), ptr_buf, 8, None) == 0:
                    continue
                ptr_val = int.from_bytes(bytes(ptr_buf), byteorder='little')
                
                if ptr_val < 0x10000 or ptr_val > 0x7FFFFFFFFFFF:
                    continue
                    
                key_buf = (ctypes.c_char * 32)()
                if kernel32.ReadProcessMemory(ctypes.c_void_p(h_process), ctypes.c_void_p(ptr_val), key_buf, 32, None) == 0:
                    continue
                
                key_bytes = bytes(key_buf)
                if key_bytes == b'\x00' * 32 or len(set(key_bytes)) < 5:
                    continue
                
                if verify_key(key_bytes, db_path):
                    kernel32.CloseHandle(ctypes.c_void_p(h_process))
                    return key_bytes.hex()
            except:
                continue
    
    # Strategy 2: Search for wxid string and look nearby for key
    print("  Phone marker strategy failed, trying wxid search...")
    wxid = 'wxid_izefflwcf2n822'
    wxid_bytes = wxid.encode()
    wxid_addrs = []
    
    for base, size in regions:
        if size > 50 * 1024 * 1024:
            continue
        try:
            buf = (ctypes.c_char * size)()
            bytes_read = ctypes.c_size_t(0)
            if kernel32.ReadProcessMemory(ctypes.c_void_p(h_process), ctypes.c_void_p(base), buf, size, ctypes.byref(bytes_read)):
                data = bytes(buf)[:bytes_read.value]
                idx = data.find(wxid_bytes)
                if idx != -1:
                    wxid_addrs.append((base, idx, size, data))
        except:
            continue
    
    print(f"  Found wxid in {len(wxid_addrs)} regions")
    
    # Strategy 3: Brute force - scan all 32-byte aligned sequences in smaller regions
    # Look for 32-byte sequences that could be keys (high entropy)
    print("  Trying brute force key search in small memory regions...")
    
    candidate_count = 0
    for base, size in regions:
        # Focus on smaller regions that are likely heap/data
        if size > 1 * 1024 * 1024 or size < 4096:
            continue
        try:
            buf = (ctypes.c_char * size)()
            bytes_read = ctypes.c_size_t(0)
            if kernel32.ReadProcessMemory(ctypes.c_void_p(h_process), ctypes.c_void_p(base), buf, size, ctypes.byref(bytes_read)):
                data = bytes(buf)[:bytes_read.value]
                # Scan through data looking for 32-byte sequences with high entropy
                for i in range(0, len(data) - 32, 8):
                    candidate = data[i:i+32]
                    if candidate == b'\x00' * 32:
                        continue
                    # Quick entropy check
                    unique = len(set(candidate))
                    if unique < 10:
                        continue
                    # Check if all bytes are non-zero (typical for keys)
                    if b'\x00' in candidate[:4]:
                        continue
                    candidate_count += 1
                    if candidate_count % 10000 == 0:
                        print(f"  Tested {candidate_count} candidates...")
                    if verify_key(candidate, db_path):
                        kernel32.CloseHandle(ctypes.c_void_p(h_process))
                        return candidate.hex()
        except:
            continue
    
    print(f"  Tested {candidate_count} candidates total, no match in small regions")
    
    # Strategy 4: Try medium-sized regions  
    print("  Trying medium regions (1-10MB)...")
    candidate_count = 0
    for base, size in regions:
        if size > 10 * 1024 * 1024 or size <= 1 * 1024 * 1024:
            continue
        try:
            buf = (ctypes.c_char * size)()
            bytes_read = ctypes.c_size_t(0)
            if kernel32.ReadProcessMemory(ctypes.c_void_p(h_process), ctypes.c_void_p(base), buf, size, ctypes.byref(bytes_read)):
                data = bytes(buf)[:bytes_read.value]
                for i in range(0, len(data) - 32, 32):  # Step by 32 for speed
                    candidate = data[i:i+32]
                    if candidate == b'\x00' * 32:
                        continue
                    unique = len(set(candidate))
                    if unique < 10:
                        continue
                    if b'\x00' in candidate[:4]:
                        continue
                    candidate_count += 1
                    if candidate_count % 50000 == 0:
                        print(f"  Tested {candidate_count} candidates...")
                    if verify_key(candidate, db_path):
                        kernel32.CloseHandle(ctypes.c_void_p(h_process))
                        return candidate.hex()
        except:
            continue
    
    print(f"  Tested {candidate_count} total candidates in medium regions")
    kernel32.CloseHandle(ctypes.c_void_p(h_process))
    return None


# Main
active_account = 'wxid_izefflwcf2n822'
db_path = f'C:/Users/Administrator/Documents/WeChat Files/{active_account}/Msg/MicroMsg.db'

print(f"Target: {active_account}")
print(f"DB: {db_path}")

pids = get_process_pids('WeChatAppEx.exe')
print(f"WeChatAppEx PIDs ({len(pids)}): {pids}")

# Sort by likely main process (larger PID or known PIDs)
for pid in pids:
    print(f"\n=== Trying PID {pid} ===")
    try:
        key = search_memory_for_key(pid, db_path)
        if key:
            print(f"\n{'='*60}")
            print(f"SUCCESS! Key: {key}")
            print(f"Account: {active_account}")
            print(f"{'='*60}")
            
            # Save the key
            with open('wx_key.txt', 'w') as f:
                f.write(f"account={active_account}\nkey={key}\ndb_path={db_path}\n")
            break
    except Exception as e:
        import traceback
        print(f"  Error: {e}")
        traceback.print_exc()
else:
    print("\nFailed to find key in any process.")
    print("The new xwechat architecture may store the key differently.")
    print("Consider trying:")
    print("1. pywxdump's newer versions that support xwechat")
    print("2. Looking at key_info.dat in xwechat login directory")
