# -*- coding: utf-8 -*-
"""
Extract WeChat key from WeChatAppEx process memory.
New WeChat (xwechat) uses WeChatAppEx.exe instead of WeChat.exe + WeChatWin.dll
"""
import ctypes
import ctypes.wintypes as wintypes
import os
import struct
import sys

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
OpenProcess = kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE
OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
CloseHandle = kernel32.CloseHandle
ReadProcessMemory = kernel32.ReadProcessMemory

# Use pywxdump's verify_key to validate
from pywxdump.wx_core.utils import verify_key

def get_process_pids(name):
    """Get PIDs of processes by name"""
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

def search_memory_for_key(pid, db_path, max_results=5):
    """Search process memory for the encryption key"""
    import ctypes
    
    h_process = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h_process:
        return None
    
    print(f"  Opened process {pid}, handle={h_process}")
    
    # Try reading memory in chunks and look for key patterns
    # WeChat key is 32 bytes, we need to validate against db
    
    # First, try to enumerate memory regions
    class MEMORY_BASIC_INFORMATION(ctypes.Structure):
        _fields_ = [
            ('BaseAddress', ctypes.c_void_p),
            ('AllocationBase', ctypes.c_void_p),
            ('AllocationProtect', wintypes.DWORD),
            ('RegionSize', ctypes.c_size_t),
            ('State', wintypes.DWORD),
            ('Protect', wintypes.DWORD),
            ('Type', wintypes.DWORD),
        ]
    
    VirtualQueryEx = kernel32.VirtualQueryEx
    VirtualQueryEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t]
    VirtualQueryEx.restype = ctypes.c_size_t
    
    MEM_COMMIT = 0x1000
    PAGE_READWRITE = 0x04
    PAGE_READONLY = 0x02
    PAGE_EXECUTE_READ = 0x20
    PAGE_EXECUTE_READWRITE = 0x40
    
    readable_protects = {PAGE_READWRITE, PAGE_READONLY, PAGE_EXECUTE_READ, PAGE_EXECUTE_READWRITE}
    
    address = 0
    regions = []
    mbi = MEMORY_BASIC_INFORMATION()
    
    while address < 0x7FFFFFFFFFFF:
        result = VirtualQueryEx(h_process, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi))
        if result == 0:
            break
        
        if mbi.State == MEM_COMMIT and mbi.Protect in readable_protects:
            regions.append((mbi.BaseAddress, mbi.RegionSize))
        
        address = mbi.BaseAddress + mbi.RegionSize
        if address <= mbi.BaseAddress:
            break
    
    print(f"  Found {len(regions)} readable memory regions")
    
    # Search for phone type strings ("android\x00", "iphone\x00") as anchor points
    # Then search backwards for the key
    phone_patterns = [b'android\x00', b'iphone\x00', b'ipad\x00']
    found_addrs = []
    
    for base, size in regions:
        if size > 100 * 1024 * 1024:  # Skip regions > 100MB
            continue
        try:
            buf = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_size_t(0)
            if ReadProcessMemory(h_process, ctypes.c_void_p(base), buf, size, ctypes.byref(bytes_read)):
                data = bytes(buf)[:bytes_read.value]
                for pattern in phone_patterns:
                    idx = 0
                    count = 0
                    while idx < len(data) and count < 5:
                        pos = data.find(pattern, idx)
                        if pos == -1:
                            break
                        found_addrs.append((base + pos, pattern))
                        count += 1
                        idx = pos + len(pattern)
        except Exception as e:
            continue
    
    print(f"  Found {len(found_addrs)} phone type markers")
    
    # For each phone type marker, search backwards for key
    keys_found = []
    for addr, pattern in found_addrs:
        # Search backward from the marker for potential 32-byte keys
        for offset in range(0, 2000, 8):
            try:
                # Read pointer at addr - offset
                ptr_buf = ctypes.create_string_buffer(8)
                if ReadProcessMemory(h_process, ctypes.c_void_p(addr - offset), ptr_buf, 8, 0) == 0:
                    continue
                ptr_val = int.from_bytes(bytes(ptr_buf), byteorder='little')
                
                # Try to read 32 bytes from the pointer
                if ptr_val < 0x10000 or ptr_val > 0x7FFFFFFFFFFF:
                    continue
                    
                key_buf = ctypes.create_string_buffer(32)
                if ReadProcessMemory(h_process, ctypes.c_void_p(ptr_val), key_buf, 32, 0) == 0:
                    continue
                
                key_bytes = bytes(key_buf)
                
                # Quick check - key shouldn't be all zeros or all same byte
                if key_bytes == b'\x00' * 32:
                    continue
                if len(set(key_bytes)) < 5:
                    continue
                
                # Verify against db
                if verify_key(key_bytes, db_path):
                    key_hex = key_bytes.hex()
                    if key_hex not in keys_found:
                        keys_found.append(key_hex)
                        print(f"  *** FOUND KEY: {key_hex} (at offset -{offset} from {hex(addr)})")
                        if len(keys_found) >= max_results:
                            CloseHandle(h_process)
                            return keys_found
            except:
                continue
    
    CloseHandle(h_process)
    return keys_found if keys_found else None


# Main
active_account = 'wxid_izefflwcf2n822'
db_path = f'C:/Users/Administrator/Documents/WeChat Files/{active_account}/Msg/MicroMsg.db'

print(f"Target account: {active_account}")
print(f"DB path: {db_path}")
print(f"DB exists: {os.path.exists(db_path)}")

# Get WeChatAppEx PIDs
pids = get_process_pids('WeChatAppEx.exe')
print(f"\nWeChatAppEx PIDs: {pids}")

# Try with the largest memory-using process first
# PID 39016 had 158MB, likely the main one
priority_pids = [39016, 45412, 38616, 42700] + [p for p in pids if p not in [39016, 45412, 38616, 42700]]

for pid in priority_pids[:5]:  # Try first 5
    print(f"\n--- Searching PID {pid} ---")
    try:
        keys = search_memory_for_key(pid, db_path)
        if keys:
            print(f"\n*** SUCCESS! Found key(s): {keys}")
            break
    except Exception as e:
        print(f"  Error: {e}")
else:
    print("\nNo key found via phone type markers. Trying brute force search...")
    
    # Alternative: try to find key by scanning all memory for 32-byte sequences that validate
    # This is slower but more thorough
    for pid in priority_pids[:3]:
        print(f"\n--- Brute force scanning PID {pid} ---")
        h_process = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if not h_process:
            continue
        
        class MEMORY_BASIC_INFORMATION(ctypes.Structure):
            _fields_ = [
                ('BaseAddress', ctypes.c_void_p),
                ('AllocationBase', ctypes.c_void_p),
                ('AllocationProtect', wintypes.DWORD),
                ('RegionSize', ctypes.c_size_t),
                ('State', wintypes.DWORD),
                ('Protect', wintypes.DWORD),
                ('Type', wintypes.DWORD),
            ]
        
        VirtualQueryEx = kernel32.VirtualQueryEx
        VirtualQueryEx.argtypes = [wintypes.HANDLE, ctypes.c_void_p, ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t]
        VirtualQueryEx.restype = ctypes.c_size_t
        
        MEM_COMMIT = 0x1000
        
        address = 0
        mbi = MEMORY_BASIC_INFORMATION()
        regions_scanned = 0
        
        while address < 0x7FFFFFFFFFFF:
            result = VirtualQueryEx(h_process, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi))
            if result == 0:
                break
            
            if mbi.State == MEM_COMMIT and mbi.RegionSize <= 10 * 1024 * 1024:
                try:
                    buf = ctypes.create_string_buffer(mbi.RegionSize)
                    bytes_read = ctypes.c_size_t(0)
                    if ReadProcessMemory(h_process, ctypes.c_void_p(mbi.BaseAddress), buf, mbi.RegionSize, ctypes.byref(bytes_read)):
                        data = bytes(buf)[:bytes_read.value]
                        # Look for the db file header pattern (first bytes of encrypted db)
                        # The SQLCipher default page size is 4096, we need the key that decrypts it
                        # Actually, let's search for wxid string as anchor
                        wxid_bytes = active_account.encode()
                        idx = data.find(wxid_bytes)
                        if idx != -1:
                            regions_scanned += 1
                            if regions_scanned <= 20:
                                print(f"  Found wxid at region {hex(mbi.BaseAddress)}, offset {idx}")
                except:
                    pass
            
            address = mbi.BaseAddress + mbi.RegionSize
            if address <= mbi.BaseAddress:
                break
        
        CloseHandle(h_process)
        print(f"  Scanned, found wxid in {regions_scanned} regions")
