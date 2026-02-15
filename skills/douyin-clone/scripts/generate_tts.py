# -*- coding: utf-8 -*-
"""
TTS配音脚本。
读取script.md文案，提取纯文本，用edge-tts生成音频。
"""

import argparse
import asyncio
import os
import re
import sys


def extract_text(md_content):
    """从markdown文案中提取纯口播文本"""
    lines = md_content.split("\n")
    text_lines = []
    skip_block = False

    for line in lines:
        stripped = line.strip()
        # 跳过代码块
        if stripped.startswith("```"):
            skip_block = not skip_block
            continue
        if skip_block:
            continue
        # 跳过标题行
        if stripped.startswith("#"):
            continue
        # 跳过场景说明（方括号内容）
        if re.match(r'^\[.*\]$', stripped):
            continue
        # 跳过画面描述（常见格式）
        if re.match(r'^(画面|场景|镜头|BGM|配乐|音效|字幕)[：:]', stripped):
            continue
        # 跳过空行和分隔线
        if not stripped or stripped.startswith("---") or stripped.startswith("==="):
            continue
        # 跳过图片/链接标记
        if stripped.startswith("![") or stripped.startswith("<!--"):
            continue

        # 清理markdown格式
        text = stripped
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # 粗体
        text = re.sub(r'\*(.*?)\*', r'\1', text)  # 斜体
        text = re.sub(r'~~(.*?)~~', r'\1', text)  # 删除线
        text = re.sub(r'`(.*?)`', r'\1', text)  # 行内代码
        text = re.sub(r'^\d+\.\s*', '', text)  # 有序列表
        text = re.sub(r'^[-*]\s*', '', text)  # 无序列表

        if text.strip():
            text_lines.append(text.strip())

    return "\n".join(text_lines)


async def generate_tts(text, voice, output_path):
    """用edge-tts生成音频"""
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="TTS配音：读取文案生成语音")
    parser.add_argument("script", help="文案文件路径（script.md）")
    parser.add_argument("-o", "--output", default="narration.mp3", help="输出音频路径（默认 narration.mp3）")
    parser.add_argument("-v", "--voice", default="zh-CN-XiaoyiNeural",
                        help="TTS声音（默认 zh-CN-XiaoyiNeural，可选 zh-CN-YunxiNeural 等）")
    parser.add_argument("--show-text", action="store_true", help="显示提取的纯文本")
    args = parser.parse_args()

    if not os.path.exists(args.script):
        print(f"❌ 文件不存在: {args.script}")
        sys.exit(1)

    with open(args.script, "r", encoding="utf-8") as f:
        md_content = f.read()

    text = extract_text(md_content)
    if not text:
        print("❌ 未提取到有效文本")
        sys.exit(1)

    char_count = len(text)
    est_duration = char_count / 250 * 60  # 约250字/分钟
    print(f"📝 提取文本: {char_count} 字")
    print(f"⏱️ 预计时长: {est_duration:.0f} 秒")
    print(f"🎤 声音: {args.voice}")

    if args.show_text:
        print(f"\n{'='*50}")
        print(text)
        print(f"{'='*50}\n")

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)

    print("🔊 生成音频中...", end="", flush=True)
    asyncio.run(generate_tts(text, args.voice, args.output))
    
    size_mb = os.path.getsize(args.output) / 1024 / 1024
    print(f" ✅ 完成！")
    print(f"💾 输出: {args.output} ({size_mb:.1f}MB)")


if __name__ == "__main__":
    main()
