import sys
sys.stdout.reconfigure(encoding='utf-8')
import ctypes
import ctypes.wintypes as wintypes
import hashlib
import hmac
import os
import psutil

# Constants
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096
DEFAULT_ITER = 64000

kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)


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
    except Exception as e:
        return False


def get_wechat_pids():
    """Get all WeChatAppEx.exe PIDs"""
    pids = []
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'WeChatAppEx.exe':
            pids.append(proc.info['pid'])
    return pids


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


def search_memory_for_key(pid, db_path):
    """Search process memory for valid key"""
    print(f"  Searching PID {pid} memory for key...")
    
    h_process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h_process:
        print(f"  Cannot open process {pid}")
        return None
    
    mbi = MEMORY_BASIC_INFORMATION()
    address = 0
    found_keys = []
    regions_scanned = 0
    
    MEM_COMMIT = 0x1000
    PAGE_READWRITE = 0x04
    PAGE_READONLY = 0x02
    PAGE_EXECUTE_READ = 0x20
    PAGE_EXECUTE_READWRITE = 0x40
    
    readable_protections = {PAGE_READWRITE, PAGE_READONLY, PAGE_EXECUTE_READ, PAGE_EXECUTE_READWRITE}
    
    try:
        while address < 0x7FFFFFFFFFFF:
            result = ctypes.windll.kernel32.VirtualQueryEx(
                h_process, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi))
            
            if result == 0:
                address += 0x1000
                continue
            
            if (mbi.State == MEM_COMMIT and 
                mbi.Protect in readable_protections and
                mbi.RegionSize > 0 and mbi.RegionSize <= 100 * 1024 * 1024):  # Max 100MB per region
                
                regions_scanned += 1
                if regions_scanned % 500 == 0:
                    print(f"    Scanned {regions_scanned} regions...")
                
                # Read the region
                try:
                    buf = ctypes.create_string_buffer(mbi.RegionSize)
                    bytes_read = ctypes.c_size_t(0)
                    if kernel32.ReadProcessMemory(h_process, ctypes.c_void_p(mbi.BaseAddress), buf, mbi.RegionSize, ctypes.byref(bytes_read)):
                        data = bytes(buf)[:bytes_read.value]
                        
                        # Scan for 32-byte sequences that could be keys
                        # Look for non-null 32-byte sequences at aligned positions
                        for offset in range(0, len(data) - 32, 8):  # 8-byte aligned
                            candidate = data[offset:offset+32]
                            # Skip all-zero or all-same-byte sequences
                            if candidate == b'\x00' * 32:
                                continue
                            if len(set(candidate)) < 8:  # Too few unique bytes
                                continue
                            
                            if verify_key(candidate, db_path):
                                key_hex = candidate.hex()
                                print(f"    FOUND KEY at PID {pid}, addr 0x{mbi.BaseAddress + offset:x}: {key_hex}")
                                found_keys.append(key_hex)
                                kernel32.CloseHandle(h_process)
                                return key_hex  # Return first valid key
                except Exception:
                    pass
            
            if mbi.BaseAddress is None or mbi.RegionSize is None:
                address += 0x1000
                continue
            next_addr = mbi.BaseAddress + mbi.RegionSize
            if next_addr <= address:
                address += 0x1000
            else:
                address = next_addr
    
    finally:
        kernel32.CloseHandle(h_process)
    
    print(f"  Scanned {regions_scanned} regions, no key found")
    return None


def main():
    # Database paths to verify against
    db_paths = {
        'xwechat': r'C:\Users\Administrator\xwechat_files\wxid_mqiv7irec7ee21_620c\db_storage\contact\contact.db',
        'traditional': r'C:\Users\Administrator\Documents\WeChat Files\wxid_mqiv7irec7ee21\MSG\MicroMsg.db',
    }
    
    pids = get_wechat_pids()
    print(f"Found {len(pids)} WeChatAppEx processes")
    
    # Try with the largest/main process (usually has the most memory)
    pid_memory = []
    for pid in pids:
        try:
            proc = psutil.Process(pid)
            mem = proc.memory_info().rss
            pid_memory.append((pid, mem))
        except:
            pass
    
    pid_memory.sort(key=lambda x: x[1], reverse=True)
    print("PIDs by memory usage:")
    for pid, mem in pid_memory[:5]:
        print(f"  PID {pid}: {mem / 1024 / 1024:.1f} MB")
    
    for db_name, db_path in db_paths.items():
        print(f"\nTrying to find key for {db_name}: {db_path}")
        if not os.path.exists(db_path):
            print(f"  DB not found, skipping")
            continue
            
        for pid, mem in pid_memory[:5]:  # Try top 5 by memory
            key = search_memory_for_key(pid, db_path)
            if key:
                print(f"\n*** SUCCESS! Key for {db_name}: {key} ***")
                return key
    
    print("\nNo key found in any process")
    return None


if __name__ == '__main__':
    main()
