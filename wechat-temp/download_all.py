import urllib.request
from PIL import Image
import io, os

urls = [
    "https://p26-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/5f5da02751bc4600966e4780925ee3fe~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=M7O%2BZ%2BZKOLXyvRkkvIa2pXDrpzo%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/5d2e8c3c9c4e41f4ace11b7e70d338a9~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=T8VlGiKwFlMEQWSIjniPQBG9XCk%3D&format=.webp",
    "https://p26-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/22763d9f14034eb7a867d5722230d737~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=qykzgEtNpuyUzrLmWxM%2BJ0gLdRM%3D&format=.webp",
    "https://p26-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/1cc6415cdd2b48e9ba564dfe2f0dd23a~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=EgwVDwsg296EpxJUMmnumRdhTXY%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/6ecfc36c2e3648abacba36082afab04e~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=NfYF6wOftsowsU8y7EFoURegsFY%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/ba3ad971d0f94395b956233e0db67cfe~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=0JQanWNJKaAn8UdnxZkKPeJbj6U%3D&format=.webp",
    "https://p26-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/e7dc77d37f6a41c2ae5b105c0c50bbdb~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=2OQ6JQsiA02GrYTBU4JpoJvJTdQ%3D&format=.webp",
    "https://p26-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/d3231a940eae46349e37267479fd28ec~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=HIYwZ0%2BOF0rOjC2NVmmS%2BBooq4A%3D&format=.webp",
    "https://p26-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/3d4099c953114a78a171a84e66840b1c~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=teXtTgP7Yzya5TS2YDoO%2Fu86EKs%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/0648de1f4dc1453fb80a7d4bef479043~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=vcU02FYU7tTzQRoeFWtJZjV2v2M%3D&format=.webp",
]

# Asset page order: newest first (scene_10 at index 0, scene_01 at index 9)
# But the click order was: idx 0,4,8,...36 of thumbnails
# From summary: index 0=scene_10, index 9=scene_01
# So reverse: url[0]->scene_10, url[9]->scene_01
# Actually let's just number them by download order and manually map later

outdir = r"D:\video-analysis\output\原生家庭\images"
os.makedirs(outdir, exist_ok=True)

headers = {"Referer": "https://jimeng.jianying.com/", "User-Agent": "Mozilla/5.0"}

for i, url in enumerate(urls):
    # Reverse order: newest first on page = scene_10 at idx 0
    scene_num = 10 - i
    outpath = os.path.join(outdir, f"scene_{scene_num:02d}.png")
    print(f"Downloading scene_{scene_num:02d}...", end=" ")
    try:
        req = urllib.request.Request(url, headers=headers)
        data = urllib.request.urlopen(req).read()
        img = Image.open(io.BytesIO(data))
        # Resize to 1080x1920 (9:16 portrait)
        img = img.resize((1080, 1920), Image.LANCZOS)
        img.save(outpath, "PNG")
        print(f"OK ({len(data)} bytes -> {os.path.getsize(outpath)} bytes)")
    except Exception as e:
        print(f"FAILED: {e}")

print("\nDone!")
for f in sorted(os.listdir(outdir)):
    if f.endswith('.png'):
        sz = os.path.getsize(os.path.join(outdir, f))
        print(f"  {f}: {sz/1024:.0f}KB")
