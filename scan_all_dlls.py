import sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')

runtime_dir = r'C:\Users\Administrator\AppData\Roaming\Tencent\xwechat\xplugin\Plugins\RadiumWMPF\18163\extracted\runtime'

# Search all DLLs and executables for sqlcipher
terms = [b'sqlcipher', b'SQLCipher', b'sqlite3_key', b'PRAGMA key', b'cipher_page_size', b'kdf_iter']

for root, dirs, files in os.walk(runtime_dir):
    for f in files:
        if not (f.endswith('.dll') or f.endswith('.exe') or f.endswith('.node')):
            continue
        fpath = os.path.join(root, f)
        try:
            with open(fpath, 'rb') as fh:
                data = fh.read()
            for term in terms:
                idx = data.find(term)
                if idx >= 0:
                    context = data[max(0,idx-20):idx+60]
                    printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)
                    print("{}: Found '{}' at 0x{:x}".format(f, term.decode('utf-8', errors='ignore'), idx))
                    print("  Context: {}".format(printable))
        except:
            pass

# Also check flue.dll more carefully
flue_path = os.path.join(runtime_dir, 'flue.dll')
with open(flue_path, 'rb') as f:
    data = f.read()
print("\nflue.dll size: {:.1f} MB".format(len(data)/1024/1024))

# Search for more generic terms
for term in [b'sqlite3_open', b'sqlite3_exec', b'PRAGMA', b'sqlcipher_export']:
    idx = data.find(term)
    if idx >= 0:
        context = data[max(0,idx-10):idx+40]
        printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)
        print("flue.dll: Found '{}' at 0x{:x}: {}".format(term.decode(), idx, printable))
