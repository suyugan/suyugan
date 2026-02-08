import pefile, sys
sys.stdout.reconfigure(encoding='utf-8')
dll = r'C:\Users\Administrator\AppData\Roaming\Tencent\xwechat\xplugin\Plugins\RadiumWMPF\18163\extracted\runtime\flue.dll'
pe = pefile.PE(dll)
if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
    exports = []
    for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        name = exp.name.decode('utf-8', errors='ignore') if exp.name else f'ordinal_{exp.ordinal}'
        exports.append(name)
    
    # Print ALL sqlite related
    sqlite_exports = [e for e in exports if 'sqlite' in e.lower()]
    print(f"SQLite exports ({len(sqlite_exports)}):")
    for e in sqlite_exports:
        print(f"  {e}")
    
    print(f"\nTotal exports: {len(exports)}")
    
    # Also look for anything with 'key', 'encrypt', 'decrypt', 'cipher'
    crypto_exports = [e for e in exports if any(k in e.lower() for k in ['encrypt', 'decrypt', 'cipher', 'hmac', 'pbkdf'])]
    print(f"\nCrypto exports ({len(crypto_exports)}):")
    for e in crypto_exports:
        print(f"  {e}")
