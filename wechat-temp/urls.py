"""
Download all 10 jimeng images by navigating browser to each URL.
Uses 360px URLs but tries to get higher res by clicking through preview.
"""
import json

# 10 thumbnail URLs (360px, from asset page, newest first)
urls_360 = [
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/5d2e8c3c9c4e41f4ace11b7e70d338a9~tplv-tb4s082cfz-aigc_resize:360:360.webp?lk3s=43402efa&x-expires=1772928000&x-signature=p%2F0wtOyJOb1lpGEd0evgWj9G4pQ%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/22763d9f14034eb7a867d5722230d737~tplv-tb4s082cfz-aigc_resize:360:360.webp?lk3s=43402efa&x-expires=1772928000&x-signature=fIqyeVx6Jc3X0e02V6ssG%2BcY2XI%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/1cc6415cdd2b48e9ba564dfe2f0dd23a~tplv-tb4s082cfz-aigc_resize:360:360.webp?lk3s=43402efa&x-expires=1772928000&x-signature=L9qQyKx5hzkgn5YJ3qAPgPqn%2FAw%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/6ecfc36c2e3648abacba36082afab04e~tplv-tb4s082cfz-aigc_resize:360:360.webp?lk3s=43402efa&x-expires=1772928000&x-signature=KDnB7CzQMtdv%2F85jkmXy0eY02rA%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/ba3ad971d0f94395b956233e0db67cfe~tplv-tb4s082cfz-aigc_resize:360:360.webp?lk3s=43402efa&x-expires=1772928000&x-signature=fx01Lwp3%2FD7caImirDrJj5zKubs%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/e7dc77d37f6a41c2ae5b105c0c50bbdb~tplv-tb4s082cfz-aigc_resize:360:360.webp?lk3s=43402efa&x-expires=1772928000&x-signature=CD13xHk7Rh%2BWLu5vkTjNIu3T27o%3D&format=.webp",
    "https://p26-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/d3231a940eae46349e37267479fd28ec~tplv-tb4s082cfz-aigc_resize:360:360.webp?lk3s=43402efa&x-expires=1772928000&x-signature=%2Bawh9lcCwNQTVL4K%2FXaEL%2BhLUAs%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/3d4099c953114a78a171a84e66840b1c~tplv-tb4s082cfz-aigc_resize:360:360.webp?lk3s=43402efa&x-expires=1772928000&x-signature=ZlrCwXD1FuFPCHOCvSatWA%2F04Vs%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/0648de1f4dc1453fb80a7d4bef479043~tplv-tb4s082cfz-aigc_resize:360:360.webp?lk3s=43402efa&x-expires=1772928000&x-signature=R0%2BGLZRIvBfOIfO0eW344YN1SXQ%3D&format=.webp",
    "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/5a8e45657e3143f9b26319df00c27f6c~tplv-tb4s082cfz-aigc_resize:360:360.webp?lk3s=43402efa&x-expires=1772928000&x-signature=RGQuQDkjyLcPNvZ%2Fg99NQKmlCPU%3D&format=.webp",
]

# Scene mapping (asset page newest first → video scene order reversed)
# scene_10 = index 0 (newest), scene_01 = index 9 (oldest in our generation batch)
# But need to verify - not sure if asset page includes older images too
# 
# The 1080px URL for scene_01 (72f39ecb) was already successfully downloaded
# So we need the other 9

# Also include the scene_01 1080 URL we already have
scene01_1080 = "https://p3-dreamina-sign.byteimg.com/tos-cn-i-tb4s082cfz/72f39ecb14164566be50cf659d6f3395~tplv-tb4s082cfz-aigc_resize:1080:1080.webp?lk3s=43402efa&x-expires=1772928000&x-signature=nCYyxOvDzOK488lPqlvsFZVairg%3D&format=.webp"

print(json.dumps({"urls": urls_360, "scene01_1080": scene01_1080}, indent=2))
