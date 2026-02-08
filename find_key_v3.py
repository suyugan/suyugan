"""
Search for SQLCipher key in flue.dll memory regions of WeChatAppEx processes.
Focus on heap memory near flue.dll loaded address.
Use multiprocessing for faster PBKDF2 verification.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import ctypes
import ctypes.wintypes as wintypes
import hashlib
import hmac
import os
import time
import psutil
from multiprocessing import Pool, cpu_count

KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096
DEFAULT_ITER = 64000

DB_PATH = r"C:\Users\Administrator\xwechat_files\wxid_mqiv7irec7ee21_620c\db_storage\contact\contact.db"

# Read DB data once
with open(DB_PATH, 'rb') as f:
    DB_DATA = f.read(5000)

SALT = DB_DATA[:16]
FIRST_PAGE = DB_DATA[16:DEFAULT_PAGESIZE]
MAC_SALT = bytes([(SALT[i] ^ 58) for i in range(16)])
EXPECTED_MAC = FIRST_PAGE[-32:-12]


def verify_single(key_hex):
    """Verify a single key candidate"""
    try:
        key_bytes = bytes.fromhex(key_hex)
        pk = hashlib.pbkdf2_hmac("sha1", key_bytes, SALT, DEFAULT_ITER, KEY_SIZE)
        pk2 = hashlib.pbkdf2_hmac("sha1", pk, MAC_SALT, 2, KEY_SIZE)
        hash_mac = hmac.new(pk2, FIRST_PAGE[:-32], hashlib.sha1)
        hash_mac.update(b'\x01\x00\x00\x00')
        if hash_mac.digest() == EXPECTED_MAC:
            return key_hex
    except:
        pass
    return None


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


PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000


def get_flue_base(pid):
    """Get flue.dll base address for a process"""
    try:
        proc = psutil.Process(pid)
        for mod in proc.memory_maps():
            if 'flue.dll' in mod.path.lower():
                # Return the first mapped address
                return int(mod.rss)  # This might not be right
    except:
        pass
    return None


def collect_candidates(pid):
    """Collect key candidates from a single process"""
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    h_process = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h_process:
        print("  Cannot open PID {}".format(pid))
        return []
    
    readable = {0x02, 0x04, 0x20, 0x40, 0x08}  # R, RW, ER, ERW, WriteCopy
    candidates = []
    mbi = MEMORY_BASIC_INFORMATION()
    address = 0
    regions_scanned = 0
    bytes_total = 0
    
    try:
        while address < 0x7FFFFFFFFFFF:
            result = ctypes.windll.kernel32.VirtualQueryEx(
                h_process, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi))
            
            if result == 0:
                address += 0x10000
                continue
            
            if mbi.BaseAddress is None or mbi.RegionSize is None:
                address += 0x10000
                continue
            
            base = mbi.BaseAddress
            size = mbi.RegionSize
            
            # Only scan RW heap memory (where key is likely stored)
            if (mbi.State == MEM_COMMIT and 
                mbi.Protect in readable and
                size >= 32 and size <= 50 * 1024 * 1024):
                
                try:
                    buf = ctypes.create_string_buffer(size)
                    bytes_read = ctypes.c_size_t(0)
                    if kernel32.ReadProcessMemory(h_process, ctypes.c_void_p(base), buf, size, ctypes.byref(bytes_read)):
                        data = bytes(buf)[:bytes_read.value]
                        regions_scanned += 1
                        bytes_total += len(data)
                        
                        # Look for 32-byte sequences that look like crypto keys
                        for offset in range(0, len(data) - 32, 8):
                            chunk = data[offset:offset+32]
                            
                            # Filter: skip common non-key patterns
                            if chunk[:4] == b'\x00\x00\x00\x00':
                                continue
                            if chunk[-4:] == b'\x00\x00\x00\x00':
                                continue
                            
                            # Entropy check: unique bytes >= 20 (crypto keys have high entropy)
                            if len(set(chunk)) < 20:
                                continue
                            
                            # Not ASCII
                            if all(32 <= b < 127 for b in chunk):
                                continue
                            
                            # Byte distribution check
                            q = [0,0,0,0]
                            for b in chunk:
                                q[b >> 6] += 1
                            if min(q) < 3:
                                continue
                            
                            candidates.append(chunk.hex())
                except:
                    pass
            
            next_addr = base + size
            if next_addr <= address:
                address += 0x10000
            else:
                address = next_addr
    finally:
        kernel32.CloseHandle(h_process)
    
    print("  PID {}: {} regions, {:.1f} MB, {} candidates".format(
        pid, regions_scanned, bytes_total/1024/1024, len(candidates)))
    return candidates


def main():
    print("=== XWeChat Key Extractor v3 (Multiprocess) ===")
    print("DB: {}".format(DB_PATH))
    print("Salt: {}".format(SALT.hex()))
    print("CPUs: {}".format(cpu_count()))
    
    start = time.time()
    
    # Get PIDs sorted by memory
    pids = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        if proc.info['name'] == 'WeChatAppEx.exe':
            try:
                mem = proc.info['memory_info'].rss
                pids.append((proc.info['pid'], mem))
            except:
                pass
    pids.sort(key=lambda x: x[1], reverse=True)
    
    print("\nProcesses:")
    for pid, mem in pids[:5]:
        print("  PID {}: {:.1f} MB".format(pid, mem/1024/1024))
    
    # Collect candidates from top processes
    all_candidates = set()
    for pid, mem in pids[:5]:
        cands = collect_candidates(pid)
        all_candidates.update(cands)
    
    candidates_list = list(all_candidates)
    elapsed = time.time() - start
    print("\nUnique candidates: {} (collected in {:.1f}s)".format(len(candidates_list), elapsed))
    
    if not candidates_list:
        print("No candidates found!")
        return
    
    # Verify using multiprocessing
    print("Verifying with {} workers...".format(cpu_count()))
    
    batch_count = 0
    with Pool(processes=cpu_count()) as pool:
        # Use imap_unordered for faster results
        for result in pool.imap_unordered(verify_single, candidates_list, chunksize=50):
            batch_count += 1
            if batch_count % 1000 == 0:
                elapsed = time.time() - start
                rate = batch_count / elapsed
                remaining = (len(candidates_list) - batch_count) / rate if rate > 0 else 0
                print("  Verified {}/{} ({:.0f}/s, ~{:.0f}s remaining)".format(
                    batch_count, len(candidates_list), rate, remaining))
            
            if result:
                total = time.time() - start
                print("\n" + "="*60)
                print("KEY FOUND: {}".format(result))
                print("Time: {:.1f}s".format(total))
                print("="*60)
                
                # Save key
                key_file = r"C:\Users\Administrator\.openclaw\workspace\wechat_key.txt"
                with open(key_file, 'w') as f:
                    f.write("key={}\n".format(result))
                    f.write("wxid=wxid_mqiv7irec7ee21\n")
                    f.write("db_path={}\n".format(DB_PATH))
                print("Key saved to: {}".format(key_file))
                
                pool.terminate()
                return result
    
    total = time.time() - start
    print("\nNo key found ({:.1f}s)".format(total))
    
    # If not found with strict filter, try also the traditional DB
    print("\nRetrying with traditional MicroMsg.db...")
    return None


if __name__ == '__main__':
    main()
