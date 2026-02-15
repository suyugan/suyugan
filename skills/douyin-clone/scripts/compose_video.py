# -*- coding: utf-8 -*-
"""
ffmpeg合成最终视频。
将图片序列+旁白音频+BGM合成为竖屏短视频。
"""

import argparse
import glob
import json
import os
import subprocess
import sys
import tempfile


def get_audio_duration(audio_path):
    """获取音频时长（秒）"""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ ffprobe失败: {result.stderr}")
        return 0
    data = json.loads(result.stdout)
    return float(data.get("format", {}).get("duration", 0))


def main():
    parser = argparse.ArgumentParser(description="ffmpeg合成最终视频（图片+旁白+BGM）")
    parser.add_argument("-i", "--images", default="images", help="图片目录（默认 images）")
    parser.add_argument("-n", "--narration", default="narration.mp3", help="旁白音频路径")
    parser.add_argument("-b", "--bgm", default="bgm.mp3", help="BGM音频路径")
    parser.add_argument("-o", "--output", default="final.mp4", help="输出视频路径（默认 final.mp4）")
    parser.add_argument("--no-bgm", action="store_true", help="不添加BGM")
    parser.add_argument("--bgm-volume", type=float, default=0.11, help="BGM音量（默认0.11）")
    parser.add_argument("--fps", type=int, default=30, help="输出帧率（默认30）")
    parser.add_argument("--width", type=int, default=1080, help="输出宽度（默认1080）")
    parser.add_argument("--height", type=int, default=1920, help="输出高度（默认1920）")
    args = parser.parse_args()

    # 检查旁白文件
    if not os.path.exists(args.narration):
        print(f"❌ 旁白文件不存在: {args.narration}")
        sys.exit(1)

    # 查找图片
    image_files = sorted(glob.glob(os.path.join(args.images, "*.png")) +
                         glob.glob(os.path.join(args.images, "*.jpg")))
    if not image_files:
        print(f"❌ 未找到图片: {args.images}")
        sys.exit(1)

    print(f"🖼️ 找到 {len(image_files)} 张图片")

    # 获取音频时长
    duration = get_audio_duration(args.narration)
    if duration <= 0:
        print("❌ 无法获取旁白时长")
        sys.exit(1)

    per_image = duration / len(image_files)
    print(f"🎵 旁白时长: {duration:.1f}秒")
    print(f"⏱️ 每张图展示: {per_image:.1f}秒")

    # 生成concat列表
    concat_file = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
    for img in image_files:
        abs_path = os.path.abspath(img).replace("\\", "/")
        concat_file.write(f"file '{abs_path}'\n")
        concat_file.write(f"duration {per_image}\n")
    # 最后一张重复（ffmpeg concat要求）
    abs_path = os.path.abspath(image_files[-1]).replace("\\", "/")
    concat_file.write(f"file '{abs_path}'\n")
    concat_file.close()

    # 构建ffmpeg命令
    use_bgm = not args.no_bgm and os.path.exists(args.bgm)

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file.name,
           "-i", args.narration]

    if use_bgm:
        cmd.extend(["-i", args.bgm])
        filter_complex = (
            f"[2:a]volume={args.bgm_volume},aloop=loop=-1:size=2e+09[bgm];"
            f"[1:a][bgm]amix=inputs=2:duration=first[aout]"
        )
        cmd.extend(["-filter_complex", filter_complex, "-map", "0:v", "-map", "[aout]"])
    else:
        cmd.extend(["-map", "0:v", "-map", "1:a"])
        if not os.path.exists(args.bgm) and not args.no_bgm:
            print(f"⚠️ BGM文件不存在({args.bgm})，跳过BGM")

    cmd.extend([
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-r", str(args.fps),
        "-c:a", "aac", "-b:a", "128k",
        "-s", f"{args.width}x{args.height}",
        "-shortest",
        args.output
    ])

    print(f"\n🎬 开始合成视频...")
    if use_bgm:
        print(f"🎵 BGM: {args.bgm} (音量 {args.bgm_volume})")
    else:
        print(f"🔇 无BGM")

    result = subprocess.run(cmd, capture_output=True, text=True)

    # 清理临时文件
    os.unlink(concat_file.name)

    if result.returncode != 0:
        print(f"❌ ffmpeg合成失败:\n{result.stderr[-500:]}")
        sys.exit(1)

    size_mb = os.path.getsize(args.output) / 1024 / 1024
    print(f"\n✅ 视频合成完成！")
    print(f"📁 输出: {args.output} ({size_mb:.1f}MB)")
    print(f"📐 尺寸: {args.width}x{args.height} @ {args.fps}fps")


if __name__ == "__main__":
    main()
