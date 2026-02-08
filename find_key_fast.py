"""
Fast key extraction for new WeChat (xwechat/WeChatAppEx)
Uses pymem for faster memory operations
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import hashlib
import hmac
import os
import time
import psutil
import pymem
import pymem.process

KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096
DEFAULT_ITER = 64000

def verify_key(key_bytes, db_path):
    """Verify if key is correct for the given db"""
    try:
        with open(db_path, "rb") as f:
            blist = f.read(5000)
        salt = blist[:16]
        pk = hashlib.pbkdf2_hmac("sha1", key_bytes, salt, DEFAULT_ITER, KEY_SIZE)
        first = blist[16:DEFAULT_PAGESIZE]
        mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
        pk = hashlib.pbkdf2_hmac("sha1", pk, mac_salt, 2, KEY_SIZE)
        hash_mac = hmac.new(pk, first[:-32], hashlib.sha1)
        hash_mac.update(b'\x01\x00\x00\x00')
        return hash_mac.digest() == first[-32:-12]
    except:
        return False

def find_key_in_pid(pid, db_path):
    """Search a specific PID for the key using pymem"""
    print(f"  Scanning PID {pid}...")
    try:
        pm = pymem.Pymem()
        pm.open_process_from_id(pid)
    except Exception as e:
        print(f"  Cannot open PID {pid}: {e}")
        return None
    
    try:
        # Get all readable memory regions
        regions = []
        for module in pm.list_modules():
            regions.append((module.lpBaseOfDll, module.SizeOfImage, module.name))
        
        # Also scan non-module heap memory
        import ctypes
        import ctypes.wintypes as wintypes
        
        class MEMORY_BASIC_INFORMATION(ctypes.Structure):
            _fields_ = [
                ("BaseAddress", ctypes.c_void_p),
                ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", wintypes.DWORD),
                ("RegionSize", ctypes.c_size_t),
                ("State", wintypes.DWORD),
                ("Protect", wintypes.DWORD),
                ("Type", wintypes.DWORD),
            ]
        
        MEM_COMMIT = 0x1000
        PAGE_READWRITE = 0x04
        
        mbi = MEMORY_BASIC_INFORMATION()
        address = 0
        heap_regions = []
        
        while address < 0x7FFFFFFFFFFF:
            result = ctypes.windll.kernel32.VirtualQueryEx(
                pm.process_handle, ctypes.c_void_p(address), 
                ctypes.byref(mbi), ctypes.sizeof(mbi))
            
            if result == 0:
                address += 0x10000
                continue
            
            if mbi.BaseAddress is None:
                address += 0x10000
                continue
                
            region_size = mbi.RegionSize if mbi.RegionSize else 0x10000
            
            # Only scan committed read-write memory (heap)
            if (mbi.State == MEM_COMMIT and 
                mbi.Protect == PAGE_READWRITE and
                region_size > 0 and region_size <= 10 * 1024 * 1024):  # Max 10MB
                heap_regions.append((mbi.BaseAddress, region_size))
            
            address = mbi.BaseAddress + region_size
            if address <= mbi.BaseAddress:
                address += 0x10000
        
        print(f"  Found {len(heap_regions)} heap regions to scan")
        
        # Read db salt for pre-filtering
        with open(db_path, 'rb') as f:
            db_header = f.read(5000)
        
        scanned = 0
        start_time = time.time()
        
        for base, size in heap_regions:
            scanned += 1
            if scanned % 200 == 0:
                elapsed = time.time() - start_time
                print(f"    Scanned {scanned}/{len(heap_regions)} regions ({elapsed:.1f}s)")
            
            try:
                data = pm.read_bytes(base, size)
            except:
                continue
            
            # Strategy: scan every 8 bytes for 32-byte key candidates
            for offset in range(0, len(data) - 32, 8):
                candidate = data[offset:offset+32]
                
                # Quick filter: skip zero/repetitive/ascii-only
                if candidate[:4] == b'\x00\x00\x00\x00':
                    continue
                unique = len(set(candidate))
                if unique < 10:
                    continue
                
                # Verify key
                if verify_key(candidate, db_path):
                    key_hex = candidate.hex()
                    print(f"  *** FOUND KEY at PID {pid}, base=0x{base:x}+0x{offset:x}: {key_hex}")
                    pm.close_process()
                    return key_hex
        
        elapsed = time.time() - start_time
        print(f"  Scanned all {len(heap_regions)} regions in {elapsed:.1f}s, no key found")
        
    except Exception as e:
        print(f"  Error scanning PID {pid}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            pm.close_process()
        except:
            pass
    
    return None

def main():
    # Find all WeChatAppEx PIDs sorted by memory
    pids = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        if proc.info['name'] == 'WeChatAppEx.exe':
            try:
                mem = proc.info['memory_info'].rss
                pids.append((proc.info['pid'], mem))
            except:
                pass
    
    pids.sort(key=lambda x: x[1], reverse=True)
    print(f"Found {len(pids)} WeChatAppEx processes")
    for pid, mem in pids[:5]:
        print(f"  PID {pid}: {mem/1024/1024:.1f} MB")
    
    # DB paths to try
    db_paths = [
        ("xwechat contact.db", r"C:\Users\Administrator\xwechat_files\wxid_mqiv7irec7ee21_620c\db_storage\contact\contact.db"),
        ("xwechat message_0.db", r"C:\Users\Administrator\xwechat_files\wxid_mqiv7irec7ee21_620c\db_storage\message\message_0.db"),
        ("traditional MicroMsg.db", r"C:\Users\Administrator\Documents\WeChat Files\wxid_mqiv7irec7ee21\MSG\MicroMsg.db"),
    ]
    
    for db_name, db_path in db_paths:
        if not os.path.exists(db_path):
            continue
        print(f"\nSearching key for: {db_name}")
        
        # Try top 3 PIDs by memory
        for pid, mem in pids[:3]:
            key = find_key_in_pid(pid, db_path)
            if key:
                print(f"\n{'='*60}")
                print(f"SUCCESS! Key found: {key}")
                print(f"DB: {db_name}")
                print(f"Path: {db_path}")
                print(f"{'='*60}")
                return key
    
    print("\nNo key found in any process")
    return None

if __name__ == '__main__':
    main()
