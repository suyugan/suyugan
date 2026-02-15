# -*- coding: utf-8 -*-
"""
批量下载抖音视频文件（无水印）。
读取 videos.json，下载到各视频独立文件夹，支持断点续传。
"""

import argparse
import json
import os
import sys
import requests


def download_video(url, save_path):
    """下载单个视频文件"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://www.douyin.com/",
    }
    try:
        resp = requests.get(url, headers=headers, stream=True, timeout=60, allow_redirects=True)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
        return True, downloaded
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="批量下载抖音视频（无水印）")
    parser.add_argument("-i", "--input", default="videos.json", help="视频列表文件路径（默认 videos.json）")
    parser.add_argument("-o", "--output", default=".", help="输出根目录（默认当前目录）")
    parser.add_argument("--skip-no-url", action="store_true", help="跳过没有视频URL的条目")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"❌ 文件不存在: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        videos = json.load(f)

    print(f"📋 共 {len(videos)} 个视频待下载")

    success = 0
    skipped = 0
    failed = 0

    for i, video in enumerate(videos, 1):
        aweme_id = video.get("aweme_id", f"unknown_{i}")
        desc = video.get("desc", "")[:30]
        video_url = video.get("video_url", "")

        video_dir = os.path.join(args.output, aweme_id)
        save_path = os.path.join(video_dir, "video.mp4")

        # 断点续传：跳过已下载的
        if os.path.exists(save_path) and os.path.getsize(save_path) > 10000:
            print(f"  [{i}/{len(videos)}] ⏭️ 已存在: {aweme_id} ({desc})")
            skipped += 1
            continue

        if not video_url:
            if args.skip_no_url:
                print(f"  [{i}/{len(videos)}] ⚠️ 无URL: {aweme_id} ({desc})")
                skipped += 1
                continue
            # 尝试通过API获取
            try:
                resp = requests.get(
                    "http://localhost:18810/api/hybrid/video_data",
                    params={"url": f"https://www.douyin.com/video/{aweme_id}"},
                    timeout=30
                )
                data = resp.json().get("data", {})
                detail = data.get("aweme_detail", data)
                play_addr = detail.get("video", {}).get("play_addr", {})
                url_list = play_addr.get("url_list", [])
                if url_list:
                    video_url = url_list[0]
            except:
                pass

        if not video_url:
            print(f"  [{i}/{len(videos)}] ❌ 无法获取URL: {aweme_id}")
            failed += 1
            continue

        os.makedirs(video_dir, exist_ok=True)
        print(f"  [{i}/{len(videos)}] ⬇️ 下载中: {aweme_id} ({desc})...", end="", flush=True)

        ok, result = download_video(video_url, save_path)
        if ok:
            size_mb = result / 1024 / 1024
            print(f" ✅ {size_mb:.1f}MB")
            success += 1
        else:
            print(f" ❌ {result}")
            failed += 1
            # 删除不完整的文件
            if os.path.exists(save_path):
                os.remove(save_path)

    print(f"\n{'='*50}")
    print(f"📊 下载完成: ✅成功 {success} | ⏭️跳过 {skipped} | ❌失败 {failed}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
