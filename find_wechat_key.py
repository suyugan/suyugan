"""
Direct memory search for SQLCipher key in WeChatAppEx.exe processes.
New WeChat (xwechat) stores keys differently.
"""
import sys, os, hashlib, hmac, time
sys.stdout.reconfigure(encoding='utf-8')
import pymem

# The active account's DB
DB_PATH = r"C:\Users\Administrator\xwechat_files\wxid_mqiv7irec7ee21_620c\db_storage\message\message_0.db"

with open(DB_PATH, 'rb') as f:
    db_data = f.read(4096)

salt = db_data[:16]
first_page = db_data[16:4096]
mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
expected_mac = first_page[-32:-12]

print(f"DB: {DB_PATH}")
print(f"Salt: {salt.hex()}")
print(f"Expected MAC: {expected_mac.hex()}")

def verify_key(key_bytes):
    """Verify if key_bytes is the correct SQLCipher key"""
    try:
        pk = hashlib.pbkdf2_hmac("sha1", key_bytes, salt, 64000, 32)
        pk2 = hashlib.pbkdf2_hmac("sha1", pk, mac_salt, 2, 32)
        hash_mac = hmac.new(pk2, first_page[:-32], hashlib.sha1)
        hash_mac.update(b'\x01\x00\x00\x00')
        return hash_mac.digest() == expected_mac
    except:
        return False

# Try pymem to read WeChatAppEx memory
import psutil

# Find the main WeChatAppEx process (largest memory)
procs = []
for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
    if proc.info['name'] == 'WeChatAppEx.exe':
        try:
            procs.append((proc.info['pid'], proc.info['memory_info'].rss))
        except:
            pass

procs.sort(key=lambda x: x[1], reverse=True)
print(f"\nFound {len(procs)} WeChatAppEx processes")
for pid, mem in procs[:5]:
    print(f"  PID {pid}: {mem/1024/1024:.1f} MB")

# Try each top process
for pid, mem in procs[:3]:
    print(f"\nScanning PID {pid} ({mem/1024/1024:.1f} MB)...")
    try:
        pm = pymem.Pymem()
        pm.open_process_from_id(pid)
        
        # Try to find the key by scanning for 32-byte high-entropy blocks
        tested = 0
        found = False
        start = time.time()
        
        for region in pm.list_memory_regions():
            if region.State != 0x1000:  # MEM_COMMIT
                continue
            if region.Protect not in (0x02, 0x04, 0x20, 0x40, 0x08):  # readable
                continue
            if region.RegionSize > 100 * 1024 * 1024:  # skip huge regions
                continue
                
            try:
                data = pm.read_bytes(region.BaseAddress, region.RegionSize)
            except:
                continue
            
            # Search for 32-byte key candidates
            for offset in range(0, len(data) - 32, 8):
                chunk = data[offset:offset+32]
                
                # Quick filters
                if chunk[:4] == b'\x00\x00\x00\x00':
                    continue
                if len(set(chunk)) < 16:
                    continue
                    
                tested += 1
                if verify_key(chunk):
                    elapsed = time.time() - start
                    print(f"\n{'='*60}")
                    print(f"KEY FOUND! ({elapsed:.1f}s, {tested} candidates)")
                    print(f"Key: {chunk.hex()}")
                    print(f"PID: {pid}")
                    print(f"{'='*60}")
                    
                    # Save
                    with open(r'C:\Users\Administrator\.openclaw\workspace\wechat_key.txt', 'w') as f:
                        f.write(f"key={chunk.hex()}\n")
                        f.write(f"wxid=wxid_mqiv7irec7ee21\n")
                        f.write(f"pid={pid}\n")
                    
                    found = True
                    break
            
            if found:
                break
            
            if tested > 0 and tested % 5000 == 0:
                elapsed = time.time() - start
                print(f"  Tested {tested} candidates ({elapsed:.1f}s)")
        
        pm.close_process()
        
        if found:
            break
            
        elapsed = time.time() - start
        print(f"  Done: {tested} candidates in {elapsed:.1f}s")
        
    except Exception as e:
        print(f"  Error: {e}")

if not found:
    print("\nKey not found in any process")
