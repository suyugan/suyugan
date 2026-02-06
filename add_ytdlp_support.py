"""
Add yt-dlp analyzer as backup
"""

import sys
import os

# Add this section to video_analyzer_api.py
ytdlp_analyzer_code = '''
    def _try_yt_dlp(self, video_url):
        """Try using yt-dlp as backup"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                if info:
                    return self._parse_yt_dlp_data(info)

            return None

        except Exception as e:
            print(f"  Error: {e}")
            return None

    def _parse_yt_dlp_data(self, data):
        """Parse yt-dlp returned data"""
        info = {}

        # Basic info
        info['title'] = data.get('title', '')
        info['uploader'] = data.get('uploader', data.get('channel', ''))

        # Statistics
        info['view_count'] = int(data.get('view_count', 0))
        info['like_count'] = int(data.get('like_count', 0))
        info['comment_count'] = int(data.get('comment_count', 0))

        # Duration
        if 'duration' in data:
            info['duration'] = data['duration']

        # BGM/Music info
        if 'track' in data:
            info['bgm'] = data.get('track', '')
            if 'artist' in data:
                info['bgm'] = f"{info['bgm']} - {data['artist']}"

        return info
'''

print("=" * 50)
print("  Adding yt-dlp support")
print("=" * 50)
print()

print("Code snippet to add to video_analyzer_api.py:")
print()
print(ytdlp_analyzer_code)
print()
print("This will add yt-dlp as a backup when other APIs fail.")
print()
