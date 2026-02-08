"""
Try to extract WeChat DB key using pywxdump's bias address approach.
WeChat must be running for memory-based extraction.
Alternative: Check if there's a saved key or try brute-force from known offsets.
"""
import os
import sys
import json

# Check pywxdump's available functions
print("=== pywxdump available functions ===")
import pywxdump
print(dir(pywxdump))

# Check for BiasAddr module (version-specific memory offsets)
try:
    from pywxdump import BiasAddr
    print(f"\nBiasAddr available: {dir(BiasAddr)}")
except ImportError as e:
    print(f"BiasAddr not available: {e}")

# Check WX_OFFS for our version
try:
    from pywxdump import WX_OFFS
    print(f"\nWX_OFFS type: {type(WX_OFFS)}")
    if isinstance(WX_OFFS, dict):
        print(f"Available versions: {list(WX_OFFS.keys())}")
        # Check our version
        v = "3.9.12.55"
        if v in WX_OFFS:
            print(f"Offsets for {v}: {WX_OFFS[v]}")
        else:
            # Try close versions
            for k in WX_OFFS:
                if k.startswith("3.9.12"):
                    print(f"Close version {k}: {WX_OFFS[k]}")
except ImportError as e:
    print(f"WX_OFFS not available: {e}")

# Try the newer API
try:
    from pywxdump.api import wx_core
    print(f"\nwx_core available: {dir(wx_core)}")
except ImportError as e:
    print(f"wx_core not available: {e}")

# Check if there's a merge_db or decrypt function
try:
    from pywxdump import decrypt as wx_decrypt
    print(f"\ndecrypt module: {dir(wx_decrypt)}")
except ImportError as e:
    print(f"decrypt not available: {e}")

try:
    from pywxdump.wx_core import decryption
    print(f"\ndecryption: {dir(decryption)}")
except ImportError as e:
    try:
        from pywxdump.wx_core import decrypt
        print(f"\ndecrypt: {dir(decrypt)}")
    except ImportError as e2:
        print(f"decrypt not found: {e2}")

# Check what submodules exist
import pkgutil
print("\n=== pywxdump submodules ===")
for importer, modname, ispkg in pkgutil.walk_packages(pywxdump.__path__, prefix="pywxdump."):
    print(f"  {modname} {'(pkg)' if ispkg else ''}")
