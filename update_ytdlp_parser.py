"""
更新 video_analyzer_api.py 的 yt-dlp 提取逻辑
"""

ytdlp_update_code = '''
    def _parse_yt_dlp_data(self, data):
        """Parse yt-dlp returned data - Enhanced version"""
        info = {}

        # Basic video info
        info['title'] = data.get('title', '')
        info['description'] = data.get('description', '')

        # Author information
        info['uploader'] = data.get('uploader', '')
        info['uploader_id'] = data.get('uploader_id', '')
        info['uploader_url'] = data.get('uploader_url', '')
        info['channel'] = data.get('channel', '')
        info['channel_url'] = data.get('channel_url', '')
        info['channel_follower_count'] = data.get('channel_follower_count', 0)
        info['channel_like_count'] = data.get('channel_like_count', 0)

        # Statistics (MOST IMPORTANT!)
        info['view_count'] = int(data.get('view_count', 0))
        info['like_count'] = int(data.get('like_count', 0))
        info['comment_count'] = int(data.get('comment_count', 0))
        info['repost_count'] = int(data.get('repost_count', 0))  # Douyin specific
        info['share_count'] = int(data.get('share_count', 0))
        info['favorite_count'] = int(data.get('favorite_count', 0))  # Douyin specific

        # Video metadata
        if 'duration' in data:
            info['duration'] = data['duration']
        if 'timestamp' in data:
            info['upload_date'] = data['timestamp']
        if 'upload_date' in data:
            info['upload_date_str'] = data['upload_date']

        # Resolution/Format
        if 'width' in data and 'height' in data:
            info['resolution'] = f"{data['width']}x{data['height']}"

        # Tags/Hashtags
        if 'tags' in data:
            info['tags'] = data['tags']

        # BGM/Music info
        if 'track' in data:
            info['bgm'] = data.get('track', '')
            if 'artist' in data:
                info['bgm'] = f"{info['bgm']} - {data['artist']}"
        elif 'music' in data:
            music = data['music']
            if isinstance(music, dict):
                info['bgm'] = music.get('title', '')
                if 'author' in music:
                    info['bgm'] = f"{info['bgm']} - {music['author']}"

        # Video URL (thumbnail)
        if 'thumbnail' in data:
            info['thumbnail'] = data['thumbnail']

        return info
'''

print("=" * 50)
print("  Enhanced yt-dlp Parser")
print("=" * 50)
print()
print("Updated data extraction includes:")
print()
print("1. Basic Info:")
print("   - title (标题)")
print("   - description (视频描述)")
print()
print("2. Author Info:")
print("   - uploader (作者昵称)")
print("   - uploader_id (作者ID)")
print("   - channel_follower_count (粉丝数)")
print("   - channel_like_count (获赞总数)")
print()
print("3. Statistics (MOST IMPORTANT):")
print("   - view_count (播放量) ⭐")
print("   - like_count (点赞数)")
print("   - comment_count (评论数)")
print("   - repost_count (转发数)")
print("   - share_count (分享数)")
print("   - favorite_count (收藏数)")
print()
print("4. Video Metadata:")
print("   - duration (时长)")
print("   - upload_date (发布时间)")
print("   - resolution (分辨率)")
print()
print("5. Extra Info:")
print("   - tags (话题标签)")
print("   - thumbnail (缩略图URL)")
print("   - bgm (背景音乐)")
print()
print("=" * 50)
