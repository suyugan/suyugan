import sys
sys.stdout.reconfigure(encoding='utf-8')

exe = r'C:\Users\Administrator\AppData\Roaming\Tencent\xwechat\xplugin\Plugins\RadiumWMPF\18163\extracted\runtime\WeChatAppEx.exe'
with open(exe, 'rb') as f:
    data = f.read()
print("Exe size: {:.1f} MB".format(len(data)/1024/1024))

# Search for crypto/sqlite strings
terms = [b'sqlcipher', b'SQLCipher', b'SQLCIPHER', b'sqlite_key', b'PRAGMA key', 
         b'pragma key', b'sqlite3_key', b'sqlite3_rekey', b'PRAGMA cipher',
         b'hmac_check', b'kdf_iter', b'cipher_page_size']

for term in terms:
    idx = 0
    while True:
        idx = data.find(term, idx)
        if idx < 0:
            break
        context = data[max(0,idx-20):idx+60]
        printable = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)
        print("Found '{}' at 0x{:x}: {}".format(term.decode('utf-8', errors='ignore'), idx, printable))
        idx += 1
        break  # Just first occurrence
