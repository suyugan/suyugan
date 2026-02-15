import paramiko, json, os, tempfile

APPID = "wx9a447fddc9ba6a59"
APPSECRET = "REDACTED_WECHAT_SECRET"
TITLE = "搭讪这件小事，我研究了三年"
AUTHOR = "苏煜淦"
DIGEST = "搭讪不是套路，是你敢不敢对这个世界主动说一句'你好'。三年踩坑经验，全给你了。"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('106.55.158.137', username='ubuntu', password='REDACTED_SERVER_PWD', timeout=10)
sftp = ssh.open_sftp()

def run(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    return out, err

# Step 1: token
print("1. Getting token...")
out, _ = run(f"curl -s 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}'")
token = json.loads(out)["access_token"]
print(f"   OK: {token[:20]}...")

# Step 2: Generate cover on server via uploaded script
print("2. Generating cover...")
cover_code = '''
import struct, zlib
W, H = 900, 383
pixels = []
for y in range(H):
    row = b''
    for x in range(W):
        t = (x + y) / (W + H)
        r = int(102 + (118 - 102) * t)
        g = int(126 + (75 - 126) * t)
        b = int(234 + (162 - 234) * t)
        row += bytes([r, g, b])
    pixels.append(b'\\x00' + row)
raw = b''.join(pixels)
def chunk(ct, d):
    c = ct + d
    return struct.pack('>I', len(d)) + c + struct.pack('>I', zlib.crc32(c) & 0xffffffff)
png = b'\\x89PNG\\r\\n\\x1a\\n'
png += chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
png += chunk(b'IDAT', zlib.compress(raw))
png += chunk(b'IEND', b'')
with open('/tmp/wx_cover.png', 'wb') as f:
    f.write(png)
print(f"OK {len(png)}")
'''
with sftp.open('/tmp/gen_cover.py', 'w') as f:
    f.write(cover_code)
out, err = run("python3 /tmp/gen_cover.py")
print(f"   {out.strip()} {err.strip()}")

# Step 3: Upload cover
print("3. Uploading cover...")
out, err = run(f"curl -s -X POST 'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=thumb' -F 'media=@/tmp/wx_cover.png;type=image/png'")
print(f"   Raw: {out.strip()}")
upload_result = json.loads(out)
thumb_media_id = upload_result.get("media_id")
if not thumb_media_id:
    # try image type
    out, _ = run(f"curl -s -X POST 'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image' -F 'media=@/tmp/wx_cover.png;type=image/png'")
    upload_result = json.loads(out)
    thumb_media_id = upload_result.get("media_id")
if not thumb_media_id:
    print(f"FAILED: {upload_result}")
    exit(1)
print(f"   thumb_media_id: {thumb_media_id}")

# Step 4: Create draft via uploaded script
print("4. Creating draft...")

CONTENT = """<section style="max-width:680px;margin:0 auto;padding:20px;font-size:16px;line-height:2;color:#333;">
<p>先说个真事。</p>
<p>三年前的一个周六下午，我在星巴克写东西，对面坐了个姑娘，穿白T恤、戴着AirPods，笔记本屏幕上开着Figma——一看就是设计师。</p>
<p>我盯着她看了二十分钟，脑子里排练了八百遍开场白：</p>
<p><em>"你好，我觉得你很有气质……"</em><br/><em>"请问这个座位有人吗？"（明明整排都空着）</em><br/><em>"你也在做设计吗？我也是……"（我明明是写代码的）</em></p>
<p>最后呢？她收拾东西走了。我坐在原地，咖啡都凉了。</p>
<p>那天回家我就想，<strong>搭讪这件事，到底卡在哪儿了？</strong></p>
<hr style="border:none;border-top:1px dashed #ccc;margin:30px 0;"/>
<h2 style="font-size:20px;color:#222;">一、你怕的不是被拒绝，是被"看穿"</h2>
<p>很多人觉得自己不敢搭讪，是因为脸皮薄、怕被拒绝。</p>
<p>其实不是。</p>
<p>你真正怕的是：<strong>对方一眼看穿你的意图，然后用那种"又一个"的眼神看你。</strong></p>
<p>这种恐惧的本质是什么？是你提前给自己贴了个标签——"我在撩人"。</p>
<p>但换个角度想：如果你问路，你会紧张吗？如果你跟同事闲聊，你会紧张吗？不会。因为那些场景你觉得自己"正当"。</p>
<p>所以第一个心法就是——</p>
<p style="font-size:18px;font-weight:bold;color:#e74c3c;text-align:center;">别把搭讪当搭讪，把它当"跟一个有趣的人说句话"。</p>
<p>你不是在追求谁，你只是一个正常的、有社交能力的人，对身边的人表示了友好。仅此而已。</p>
<hr style="border:none;border-top:1px dashed #ccc;margin:30px 0;"/>
<h2 style="font-size:20px;color:#222;">二、三秒定律：别想，冲就完了</h2>
<p>这是我踩了无数坑之后，总结出来最有用的一条：</p>
<p style="font-size:18px;font-weight:bold;color:#e74c3c;text-align:center;">当你想跟一个人说话时，三秒之内开口。</p>
<p>为什么是三秒？因为超过三秒，你的大脑就会启动"风险评估模式"——它会帮你想出一万个不开口的理由：</p>
<p><em>"人家在忙吧……"</em><br/><em>"万一有男朋友呢……"</em><br/><em>"我今天穿得不太行……"</em><br/><em>"算了算了下次吧……"</em></p>
<p>然后就没有下次了。</p>
<p>三秒定律不是让你莽，是让你<strong>跳过那个自我否定的过程</strong>。嘴比脑子快一步，反而更自然。</p>
<hr style="border:none;border-top:1px dashed #ccc;margin:30px 0;"/>
<h2 style="font-size:20px;color:#222;">三、开口说什么？记住一个公式</h2>
<p>很多人卡在"第一句话说啥"。</p>
<p>网上那些话术模板——"你笑起来真好看""你的耳环很特别"——不是不能用，但说出来总有股脚本味。</p>
<p>我总结了一个万能公式：<strong>观察 + 好奇</strong></p>
<p>什么意思？你看到了什么，你对什么好奇，就说什么。</p>
<p><strong>场景一：咖啡店</strong><br/>看到对方在看一本书→"这本书我一直想看，值得买吗？"<br/>看到对方点了一杯很特别的饮品→"你这杯是什么？看起来不错。"</p>
<p><strong>场景二：书店/展览</strong><br/>"你也喜欢XXX？我觉得他的XX作品最好。"<br/>"这个展你看了多久了？有没有特别推荐的？"</p>
<p><strong>场景三：健身房/运动场</strong><br/>"你这个动作做得很标准，练了多久了？"<br/>"你这双鞋不错，跑步穿舒服吗？"</p>
<p>核心逻辑是：<strong>你不是在夸TA，你是在请教、在交流、在分享一个瞬间。</strong></p>
<p>这比"你好漂亮"有效一万倍。因为后者让人尬，前者让人有话可接。</p>
<hr style="border:none;border-top:1px dashed #ccc;margin:30px 0;"/>
<h2 style="font-size:20px;color:#222;">四、被拒绝了？恭喜你，你赢了</h2>
<p>我搭讪过大概……几十次吧。成功率？可能30%都不到。</p>
<p>但我从来不觉得那些"失败"的经历是失败。</p>
<p>有一次在书店，我问一个女生"你觉得加缪好读吗"，她抬头看了我一眼，说"我在等人"，然后就低头了。</p>
<p>尴尬吗？有一丢丢。但就那么两秒钟。我说了句"好的打扰了"就走了，全程不超过十秒。</p>
<p><strong>被拒绝的成本其实极低。</strong>十秒钟的尴尬，换来的是——你证明了自己敢开口。</p>
<p>而且说实话，大多数人被搭讪的反应不是厌恶，而是<strong>意外</strong>。因为在这个人人低头看手机的时代，有人愿意抬头跟你说话，本身就是件稀缺的事。</p>
<hr style="border:none;border-top:1px dashed #ccc;margin:30px 0;"/>
<h2 style="font-size:20px;color:#222;">五、几个雷区，千万别踩</h2>
<p>说完该做的，说说不该做的。这些都是我亲眼见过的翻车现场：</p>
<p>❌ <strong>堵路式搭讪</strong>：拦住人家的去路，逼人跟你对话。这不是搭讪，这是拦截。<br/>❌ <strong>评价身材/外貌</strong>："你身材真好""你腿好长"——你觉得是赞美，人家觉得是骚扰。<br/>❌ <strong>纠缠不放</strong>：对方明显不想聊了，你还在那儿找话题。察言观色，是成年人的基本功。<br/>❌ <strong>立刻要微信</strong>：聊了不到一分钟就"加个微信呗"，目的性太强了。自然地聊，聊开心了再顺势交换联系方式。<br/>❌ <strong>天黑了还搭讪</strong>：晚上在路上被陌生人叫住，换谁都会有警惕心。时间地点要选对。</p>
<hr style="border:none;border-top:1px dashed #ccc;margin:30px 0;"/>
<h2 style="font-size:20px;color:#222;">六、搭讪的终极意义</h2>
<p>说了这么多技巧，但我最想说的其实是——</p>
<p><strong>搭讪的本质不是"撩人"，是"活着"。</strong></p>
<p>我们每天戴着耳机、盯着屏幕，把自己装进一个隐形的壳里。我们用外卖代替逛菜市场，用社交软件代替面对面认识人，用点赞代替真正的交流。</p>
<p>我们越来越安全，也越来越孤独。</p>
<p>搭讪这件事，说到底就是——<strong>你敢不敢对这个世界主动说一句"你好"？</strong></p>
<p>不一定要追谁、撩谁。你跟早餐店老板多聊两句，跟电梯里的邻居打个招呼，跟公园里遛狗的大爷唠几句——这些都是搭讪。</p>
<p>每一次主动开口，你都在练一个能力：<strong>跟这个世界建立连接的能力。</strong></p>
<p>这个能力，比任何话术模板都值钱。</p>
<hr style="border:none;border-top:1px dashed #ccc;margin:30px 0;"/>
<p style="text-align:center;color:#888;font-size:14px;">写这篇的时候，我又想起三年前星巴克那个下午。<br/>如果时间能倒流，我大概会走过去说：<br/><em>"你Figma用的什么字体？挺好看的。"</em><br/><br/>就这么简单。</p>
</section>"""

draft_data = {
    "articles": [
        {
            "title": TITLE,
            "author": AUTHOR,
            "digest": DIGEST,
            "content": CONTENT,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }
    ]
}

# Write draft script to server
draft_json = json.dumps(draft_data, ensure_ascii=False)
draft_script = f'''# -*- coding: utf-8 -*-
import json, urllib.request

data = json.loads(open("/tmp/draft_data.json", "r", encoding="utf-8").read())
url = "https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
body = json.dumps(data, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request(url, data=body, headers={{"Content-Type": "application/json; charset=utf-8"}}, method="POST")
resp = urllib.request.urlopen(req)
print(resp.read().decode("utf-8"))
'''

with sftp.open('/tmp/draft_data.json', 'w') as f:
    f.write(draft_json)
with sftp.open('/tmp/create_draft.py', 'w') as f:
    f.write(draft_script)

out, err = run("python3 /tmp/create_draft.py")
print(f"   Result: {out.strip()}")
if err.strip():
    print(f"   Error: {err.strip()}")

result = json.loads(out.strip())
if "media_id" in result:
    print(f"\n✅ 草稿创建成功！")
    print(f"   标题: {TITLE}")
    print(f"   作者: {AUTHOR}")
    print(f"   草稿media_id: {result['media_id']}")
else:
    print(f"\n❌ 失败: {result}")

ssh.close()
