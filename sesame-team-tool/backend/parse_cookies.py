#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析抖音 Cookies 并转换为 Cookie 字符串
"""
import json
import sys

# 读取 cookies JSON 文件
cookies_file = r'C:\Users\Administrator\.openclaw\media\inbound\file_21---964ecd8c-90de-41d8-8420-d41abeafab44.json'

print("=" * 50)
print("  Cookies 解析工具")
print("=" * 50)
print()

with open(cookies_file, 'r', encoding='utf-8') as f:
    cookies = json.load(f)

print(f"共读取到 {len(cookies)} 个 cookies")
print()

# 转换为 Cookie 字符串格式
cookie_pairs = []
for cookie in cookies:
    name = cookie['name']
    value = cookie['value']

    # 跳过空 value 的 cookie
    if not value:
        continue

    # 简单的 name=value 格式
    cookie_pairs.append(f"{name}={value}")

# 组合成 Cookie 字符串
cookie_string = "; ".join(cookie_pairs)

print("=" * 50)
print("  Cookie 字符串生成完成")
print("=" * 50)
print()

print("Cookie String:")
print(cookie_string)
print()

print("=" * 50)
print("  保存到文件")
print("=" * 50)
print()

# 保存到文件
output_file = r'C:\Users\Administrator\.openclaw\workspace\sesame-team-tool\backend\cookies.txt'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(cookie_string)

print(f"Cookie 字符串已保存到: {output_file}")
print()

print("=" * 50)
