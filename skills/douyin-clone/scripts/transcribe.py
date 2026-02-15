# -*- coding: utf-8 -*-
"""
批量音频提取+Whisper语音转录。
遍历已下载视频，用ffmpeg提取音频，用openai-whisper转录为文字。
"""

import argparse
import glob
import os
import subprocess
import sys


def extract_audio(video_path, audio_path):
    """用ffmpeg从视频提取音频"""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-ar", "16000", "-ac", "1",
        audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


def transcribe_audio(audio_path, model_name="medium", language="zh"):
    """用whisper转录音频"""
    import whisper
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path, language=language)
    return result["text"]


def main():
    parser = argparse.ArgumentParser(description="批量音频提取+Whisper语音转录")
    parser.add_argument("-d", "--dir", default=".", help="视频根目录（包含各视频ID子文件夹）")
    parser.add_argument("-m", "--model", default="medium", help="Whisper模型（tiny/base/small/medium/large，默认medium）")
    parser.add_argument("--language", default="zh", help="转录语言（默认zh）")
    parser.add_argument("--force", action="store_true", help="强制重新转录已有的")
    args = parser.parse_args()

    # 查找所有video.mp4
    video_files = glob.glob(os.path.join(args.dir, "*/video.mp4"))
    if not video_files:
        print(f"⚠️ 在 {args.dir} 下未找到任何 video.mp4")
        sys.exit(1)

    print(f"📹 找到 {len(video_files)} 个视频")
    print(f"🤖 使用 Whisper 模型: {args.model}")

    # 延迟加载whisper（避免没视频时也加载）
    whisper_model = None
    success = 0
    skipped = 0
    failed = 0

    for i, vpath in enumerate(sorted(video_files), 1):
        video_dir = os.path.dirname(vpath)
        video_id = os.path.basename(video_dir)
        audio_path = os.path.join(video_dir, "audio.wav")
        transcript_path = os.path.join(video_dir, "transcript.txt")

        # 跳过已转录的
        if os.path.exists(transcript_path) and not args.force:
            print(f"  [{i}/{len(video_files)}] ⏭️ 已转录: {video_id}")
            skipped += 1
            continue

        print(f"  [{i}/{len(video_files)}] 🎵 提取音频: {video_id}...", end="", flush=True)

        # 提取音频
        if not os.path.exists(audio_path) or args.force:
            if not extract_audio(vpath, audio_path):
                print(f" ❌ ffmpeg失败")
                failed += 1
                continue
        print(" ✅", end="", flush=True)

        # 转录
        print(" 🗣️ 转录中...", end="", flush=True)
        try:
            if whisper_model is None:
                print("\n  ⏳ 首次加载Whisper模型，请稍候...", end="", flush=True)
                import whisper
                whisper_model = whisper.load_model(args.model)
                print(" ✅ 模型加载完成", end="", flush=True)

            result = whisper_model.transcribe(audio_path, language=args.language)
            text = result["text"].strip()

            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(text)

            char_count = len(text)
            print(f" ✅ {char_count}字")
            success += 1
        except Exception as e:
            print(f" ❌ {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"📊 转录完成: ✅成功 {success} | ⏭️跳过 {skipped} | ❌失败 {failed}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
