#!/bin/bash
APPID="wx9a447fddc9ba6a59"
SECRET="REDACTED_WECHAT_SECRET"

# Get token
TOKEN=$(curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=$APPID&secret=$SECRET" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
echo "TOKEN: $TOKEN"

# Upload cover image
UPLOAD_RESULT=$(curl -s -F "media=@/tmp/cover.jpg" "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=$TOKEN&type=image")
echo "UPLOAD: $UPLOAD_RESULT"
MEDIA_ID=$(echo "$UPLOAD_RESULT" | python3 -c "import sys,json;print(json.load(sys.stdin)['media_id'])")
echo "MEDIA_ID: $MEDIA_ID"

# Read article HTML
CONTENT=$(python3 -c "
import json
with open('/tmp/article.html','r') as f:
    print(json.dumps(f.read()))
")

# Create draft
DRAFT_DATA=$(python3 -c "
import json
with open('/tmp/article.html','r') as f:
    content = f.read()
data = {
    'articles': [{
        'title': '减肥的5个真相：别再节食了，越饿越胖',
        'author': '苏煜淦',
        'digest': '90%的人减肥失败，不是意志力不够，是方法从一开始就错了。热量缺口、蛋白质、力量训练、睡眠——这篇把真正有效的方法一次说清楚。',
        'content': content,
        'thumb_media_id': '$MEDIA_ID',
        'need_open_comment': 1,
        'only_fans_can_comment': 0
    }]
}
print(json.dumps(data, ensure_ascii=False))
")

DRAFT_RESULT=$(curl -s -X POST "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=$TOKEN" -d "$DRAFT_DATA")
echo "DRAFT: $DRAFT_RESULT"
