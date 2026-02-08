import sys, os, psutil
sys.stdout.reconfigure(encoding='utf-8')
for proc in psutil.process_iter(['pid', 'name', 'exe']):
    name = proc.info['name'] or ''
    exe = proc.info['exe'] or ''
    if 'wechat' in name.lower() or 'wechat' in exe.lower():
        pid = proc.info['pid']
        print(f"PID {pid}: {name}")
        print(f"  exe: {exe}")
        try:
            for mod in proc.memory_maps():
                if 'wechat' in mod.path.lower() and mod.path.endswith('.dll'):
                    print(f"  DLL: {mod.path}")
        except:
            pass
