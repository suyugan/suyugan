import paramiko
import requests
import os

# 新截图文件
local_dir = r'C:\Users\Administrator\.openclaw\workspace\projects\wechat-viewer\uploads\5c021a42-1a6d-4666-b660-c754554bb8a6'
new_files = [
    '189fec3e-122e-4c52-872e-ff6d0a058ff8.png',
    '710310e5-5058-4a07-919d-941711cfab4b.png',
    '6e6eacb7-1854-45dc-8565-5ad60c49942f.png',
    'c87949e3-fa61-4a38-81c9-ff9e31b61bcd.png',
    '84932432-9dbf-4753-b329-2197db7cb44b.png',
]

# 上传到线上服务器
group_id = '5c021a42-1a6d-4666-b660-c754554bb8a6'
url = f'http://106.55.158.137/wechat/api/groups/{group_id}/images'

for i, fname in enumerate(new_files, 1):
    fpath = os.path.join(local_dir, fname)
    with open(fpath, 'rb') as f:
        files = {'images': (f'new_{i}.png', f, 'image/png')}
        r = requests.post(url, files=files)
        print(f'{i}. {fname}: {r.status_code}')

print('Done!')
