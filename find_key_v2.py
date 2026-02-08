"""
Direct memory search for SQLCipher key using ctypes Windows API.
"""
import sys, os, hashlib, hmac, time, ctypes, ctypes.wintypes as wt
sys.stdout.reconfigure(encoding='utf-8')
import psutil

DB_PATH = r"C:\Users\Administrator\xwechat_files\wxid_mqiv7irec7ee21_620c\db_storage\message\message_0.db"

with open(DB_PATH, 'rb') as f:
    db_data = f.read(4096)

salt = db_data[:16]
first_page = db_data[16:4096]
mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
expected_mac = first_page[-32:-12]

print(f"Salt: {salt.hex()}")
print(f"Expected MAC: {expected_mac.hex()}")

def verify_key(key_bytes):
    try:
        pk = hashlib.pbkdf2_hmac("sha1", key_bytes, salt, 64000, 32)
        pk2 = hashlib.pbkdf2_hmac("sha1", pk, mac_salt, 2, 32)
        h = hmac.new(pk2, first_page[:-32], hashlib.sha1)
        h.update(b'\x01\x00\x00\x00')
        return h.digest() == expected_mac
    except:
        return False

# Windows API setup
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wt.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wt.DWORD),
        ("Protect", wt.DWORD),
        ("Type", wt.DWORD),
    ]

PROCESS_ALL = 0x0400 | 0x0010  # QUERY_INFO | VM_READ
MEM_COMMIT = 0x1000
READABLE = {0x02, 0x04, 0x20, 0x40, 0x08}

def scan_process(pid):
    handle = kernel32.OpenProcess(PROCESS_ALL, False, pid)
    if not handle:
        print(f"  Cannot open PID {pid}")
        return False
    
    mbi = MEMORY_BASIC_INFORMATION()
    addr = 0
    tested = 0
    start = time.time()
    
    try:
        while addr < 0x7FFFFFFFFFFF:
            ret = kernel32.VirtualQueryEx(handle, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi))
            if ret == 0:
                addr += 0x10000
                continue
            
            base = mbi.BaseAddress or 0
            size = mbi.RegionSize or 0
            
            if size == 0:
                addr += 0x10000
                continue
            
            if (mbi.State == MEM_COMMIT and mbi.Protect in READABLE and 32 <= size <= 50*1024*1024):
                try:
                    buf = ctypes.create_string_buffer(size)
                    read = ctypes.c_size_t(0)
                    if kernel32.ReadProcessMemory(handle, ctypes.c_void_p(base), buf, size, ctypes.byref(read)):
                        data = bytes(buf)[:read.value]
                        
                        for off in range(0, len(data) - 32, 8):
                            chunk = data[off:off+32]
                            if chunk[:4] == b'\x00\x00\x00\x00':
                                continue
                            if len(set(chunk)) < 16:
                                continue
                            
                            tested += 1
                            if verify_key(chunk):
                                elapsed = time.time() - start
                                print(f"\n{'='*60}")
                                print(f"KEY FOUND! ({elapsed:.1f}s, {tested} tested)")
                                print(f"Key: {chunk.hex()}")
                                print(f"PID: {pid}")
                                print(f"{'='*60}")
                                
                                with open(r'C:\Users\Administrator\.openclaw\workspace\wechat_key.txt', 'w') as f:
                                    f.write(f"key={chunk.hex()}\n")
                                    f.write(f"wxid=wxid_mqiv7irec7ee21\n")
                                    f.write(f"pid={pid}\n")
                                return True
                            
                            if tested % 2000 == 0:
                                elapsed = time.time() - start
                                rate = tested / elapsed if elapsed > 0 else 0
                                print(f"  {tested} tested ({rate:.0f}/s, {elapsed:.0f}s)", flush=True)
                except:
                    pass
            
            next_addr = base + size
            addr = next_addr if next_addr > addr else addr + 0x10000
    finally:
        kernel32.CloseHandle(handle)
    
    elapsed = time.time() - start
    print(f"  Done: {tested} tested in {elapsed:.1f}s")
    return False

# Get top WeChatAppEx processes
procs = []
for p in psutil.process_iter(['pid', 'name', 'memory_info']):
    if p.info['name'] == 'WeChatAppEx.exe':
        try:
            procs.append((p.info['pid'], p.info['memory_info'].rss))
        except:
            pass

procs.sort(key=lambda x: x[1], reverse=True)
print(f"Found {len(procs)} processes")

for pid, mem in procs[:5]:
    print(f"\nPID {pid} ({mem/1024/1024:.1f} MB)...")
    if scan_process(pid):
        print("SUCCESS!")
        break
else:
    print("\nKey not found")
