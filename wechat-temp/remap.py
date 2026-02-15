import shutil, os

src = r"D:\video-analysis\output\原生家庭\images"
# Temp rename to avoid conflicts
mapping = {
    # current_name -> target scene based on content
    "scene_01.png": "s05.png",  # 隔墙触碰双手 → 察言观色/门后偷看
    "scene_02.png": "s03.png",  # 妈妈小男孩开门 → 冷淡家庭
    "scene_03.png": "s04.png",  # 女孩流泪背包 → 恋爱逃避/推开
    "scene_04.png": "s06.png",  # 孩子灵魂安慰母亲 → 讨好型
    "scene_05.png": "s07.png",  # 透明小女孩拥抱 → 内在小孩
    "scene_06.png": "s08a.png", # 三代女性锁链 → 代际传递
    "scene_07.png": "s08.png",  # 祖孙三代锁链 → 代际传递(选这个)
    "scene_08.png": "s09.png",  # 冥想+发光小女孩 → 觉察与治愈
    "scene_09.png": "s10a.png", # 女孩挣脱锁链 → 改写结局(备选)
    "scene_10.png": "s10.png",  # 女孩挣脱锁链夕阳 → 改写结局
}

# First pass: rename to temp names
for old, new in mapping.items():
    oldp = os.path.join(src, old)
    newp = os.path.join(src, new)
    if os.path.exists(oldp):
        shutil.move(oldp, newp)
        print(f"{old} -> {new}")

# We're missing scene_01 (girl curled up) and scene_02 (warm family hug)
# scene_08a is duplicate of scene_08 (pick one)
# scene_10a is duplicate of scene_10 (pick one)

# Final rename
final = {
    # "s01.png": missing - need original scene_01 from earlier
    # "s02.png": missing - warm family hug
    "s03.png": "final_scene_03.png",
    "s04.png": "final_scene_04.png",  
    "s05.png": "final_scene_05.png",
    "s06.png": "final_scene_06.png",
    "s07.png": "final_scene_07.png",
    "s08.png": "final_scene_08.png",
    "s09.png": "final_scene_09.png",
    "s10.png": "final_scene_10.png",
}

for old, new in final.items():
    oldp = os.path.join(src, old)
    newp = os.path.join(src, new)
    if os.path.exists(oldp):
        shutil.move(oldp, newp)

# List results
print("\nFinal files:")
for f in sorted(os.listdir(src)):
    if f.endswith('.png'):
        print(f"  {f}: {os.path.getsize(os.path.join(src, f))//1024}KB")
