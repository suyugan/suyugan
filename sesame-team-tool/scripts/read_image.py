#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取图片信息并识别内容
"""

import sys
import os
from PIL import Image
import pytesseract

def read_image_info(image_path):
    """读取图片基本信息"""
    try:
        with Image.open(image_path) as img:
            info = {
                'filename': os.path.basename(image_path),
                'width': img.width,
                'height': img.height,
                'format': img.format,
                'mode': img.mode,
                'size_bytes': os.path.getsize(image_path)
            }
            return info
    except Exception as e:
        return {'error': str(e)}

def extract_text_from_image(image_path):
    """从图片中提取文字（OCR）"""
    try:
        # 使用 tesseract OCR
        text = pytesseract.image_to_string(image_path, lang='chi_sim')
        return text
    except Exception as e:
        return f'OCR Error: {str(e)}'

def main():
    # 图片路径
    image_path = r'C:\Users\Administrator\.openclaw\media\inbound\file_18---5494b48e-a528-4e91-ad17-edcc0eda0adc.jpg'

    print("=" * 50)
    print("  图片识别工具")
    print("=" * 50)
    print()

    # 读取基本信息
    print("[1/2] 读取图片基本信息...")
    info = read_image_info(image_path)

    if 'error' in info:
        print(f"  错误: {info['error']}")
        return

    print(f"  文件名: {info['filename']}")
    print(f"  尺寸: {info['width']} x {info['height']}")
    print(f"  格式: {info['format']}")
    print(f"  模式: {info['mode']}")
    print(f"  大小: {info['size_bytes']} bytes")
    print()

    # OCR 文字识别
    print("[2/2] 文字识别（OCR）...")
    print("  正在提取文字，这可能需要几秒钟...")
    print()

    text = extract_text_from_image(image_path)

    if text.startswith('OCR Error'):
        print(f"  {text}")
        print()
        print("注意：需要安装 tesseract OCR")
        print("下载地址：https://github.com/UB-Mannheim/tesseract/wiki")
        print()
        print("或者直接描述图片内容：")
        print("1. 图片中有什么文字？")
        print("2. 是什么类型的页面？")
        print("3. 有哪些按钮或功能？")
    else:
        print(f"  识别到的文字：")
        print("-" * 50)
        print(text)
        print("-" * 50)

    print()
    print("=" * 50)
    print("  识别完成！")
    print("=" * 50)

if __name__ == "__main__":
    main()
