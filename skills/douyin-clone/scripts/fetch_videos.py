# -*- coding: utf-8 -*-
"""
批量抓取抖音博主所有视频数据。
支持博主主页链接或sec_uid输入，通过本地API获取视频列表和元数据。
输出 videos.json 到指定目录。
"""

import argparse
import json
import os
import re
import sys
import time
import requests


API_BASE = "http://localhost:18810"


def extract_sec_uid(url_or_uid):
    """从URL提取sec_uid，或直接返回sec_uid"""
    if url_or_uid.startswith("MS4wLjAB") or url_or_uid.startswith("sec_"):
        return url_or_uid
    # 尝试通过API解析URL获取sec_uid
    try:
        resp = requests.get(f"{API_BASE}/api/hybrid/video_data", params={"url": url_or_uid}, timeout=30)
        data = resp.json()
        if "data" in data:
            author = data["data"].get("aweme_detail", {}).get("author", {})
            if not author:
                author = data["data"].get("author", {})
            sec_uid = author.get("sec_uid", "")
            if sec_uid:
                print(f"✅ 从链接解析到 sec_uid: {sec_uid}")
                return sec_uid
    except Exception as e:
        print(f"⚠️ 解析链接失败: {e}")
    return url_or_uid


def fetch_user_videos(sec_uid, max_count=0):
    """批量获取博主所有视频"""
    videos = []
    cursor = 0
    page = 0
    while True:
        page += 1
        print(f"📥 正在获取第 {page} 页 (cursor={cursor})...")
        try:
            resp = requests.get(
                f"{API_BASE}/api/douyin/web/fetch_user_post_videos",
                params={"sec_user_id": sec_uid, "max_cursor": cursor, "count": 20},
                timeout=30
            )
            data = resp.json()
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            break

        aweme_list = data.get("data", {}).get("aweme_list", [])
        if not aweme_list:
            aweme_list = data.get("aweme_list", [])

        if not aweme_list:
            print("📭 没有更多视频了")
            break

        for item in aweme_list:
            video_info = {
                "aweme_id": item.get("aweme_id", ""),
                "desc": item.get("desc", ""),
                "create_time": item.get("create_time", 0),
                "duration": item.get("duration", 0) or item.get("video", {}).get("duration", 0),
                "statistics": item.get("statistics", {}),
                "video_url": "",
                "music_url": "",
                "text_extra": [t.get("hashtag_name", "") for t in item.get("text_extra", []) if t.get("hashtag_name")],
                "author": {
                    "nickname": item.get("author", {}).get("nickname", ""),
                    "sec_uid": item.get("author", {}).get("sec_uid", ""),
                    "uid": item.get("author", {}).get("uid", ""),
                },
            }
            # 提取无水印视频URL
            video_obj = item.get("video", {})
            play_addr = video_obj.get("play_addr", {}) or video_obj.get("play_addr_lowbr", {})
            if play_addr:
                url_list = play_addr.get("url_list", [])
                if url_list:
                    video_info["video_url"] = url_list[0]

            # 提取音乐URL
            music = item.get("music", {})
            if music:
                play_url = music.get("play_url", {})
                if isinstance(play_url, dict):
                    music_urls = play_url.get("url_list", [])
                    if music_urls:
                        video_info["music_url"] = music_urls[0]
                video_info["music_title"] = music.get("title", "")

            videos.append(video_info)

        print(f"  ✅ 获取到 {len(aweme_list)} 个视频，累计 {len(videos)} 个")

        if max_count > 0 and len(videos) >= max_count:
            videos = videos[:max_count]
            print(f"🔢 达到最大数量限制 {max_count}")
            break

        has_more = data.get("data", {}).get("has_more", 0) or data.get("has_more", 0)
        cursor = data.get("data", {}).get("max_cursor", 0) or data.get("max_cursor", 0)

        if not has_more:
            print("📭 已获取所有视频")
            break

        time.sleep(1)

    return videos


def print_stats(videos):
    """打印统计信息"""
    if not videos:
        print("⚠️ 没有视频数据")
        return

    author_name = videos[0].get("author", {}).get("nickname", "未知")
    total_likes = sum(v.get("statistics", {}).get("digg_count", 0) for v in videos)
    total_comments = sum(v.get("statistics", {}).get("comment_count", 0) for v in videos)
    total_shares = sum(v.get("statistics", {}).get("share_count", 0) for v in videos)
    total_collects = sum(v.get("statistics", {}).get("collect_count", 0) for v in videos)

    print(f"\n{'='*50}")
    print(f"📊 博主: {author_name}")
    print(f"📹 视频总数: {len(videos)}")
    print(f"❤️  总点赞: {total_likes:,}")
    print(f"💬 总评论: {total_comments:,}")
    print(f"⭐ 总收藏: {total_collects:,}")
    print(f"🔄 总分享: {total_shares:,}")
    if len(videos) > 0:
        print(f"📈 平均点赞: {total_likes // len(videos):,}")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser(description="批量抓取抖音博主所有视频数据")
    parser.add_argument("input", help="博主主页链接或sec_uid")
    parser.add_argument("-o", "--output", default=".", help="输出目录（默认当前目录）")
    parser.add_argument("-n", "--max-count", type=int, default=0, help="最大抓取数量（0=全部）")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    sec_uid = extract_sec_uid(args.input)
    print(f"🎯 目标 sec_uid: {sec_uid}")

    videos = fetch_user_videos(sec_uid, args.max_count)

    if videos:
        out_path = os.path.join(args.output, "videos.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
        print(f"\n💾 已保存 {len(videos)} 个视频数据到 {out_path}")

    print_stats(videos)


if __name__ == "__main__":
    main()
