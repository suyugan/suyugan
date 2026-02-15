# -*- coding: utf-8 -*-
"""
即梦API批量生图脚本。
读取prompts.json，通过火山引擎即梦API生成场景图片。
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import requests
from datetime import datetime, timezone


class VolcSigner:
    """火山引擎API签名"""
    def __init__(self, ak, sk):
        self.ak = ak
        self.sk = sk

    def sign(self, method, url, headers, body=""):
        from urllib.parse import urlparse, parse_qs, urlencode
        parsed = urlparse(url)
        
        # 简化：使用volcengine SDK如果可用
        return headers


def submit_task(ak, sk, prompt, width=1080, height=1920):
    """提交即梦生图任务"""
    try:
        from volcengine.visual.VisualService import VisualService
        visual_service = VisualService()
        visual_service.set_ak(ak)
        visual_service.set_sk(sk)

        form = {
            "req_key": "jimeng_t2i_v40",
            "prompt": prompt,
            "width": width,
            "height": height,
            "return_url": True,
            "logo_info": {"add_logo": False},
        }

        resp = visual_service.cv_sync2_async_submit_task(form)
        if resp and resp.get("code") == 10000:
            task_id = resp.get("data", {}).get("task_id", "")
            return task_id
        else:
            print(f"  ❌ 提交失败: {resp}")
            return None
    except ImportError:
        print("❌ 需要安装 volcengine SDK: pip install volcengine")
        sys.exit(1)


def poll_task(ak, sk, task_id, max_wait=120):
    """轮询任务结果"""
    from volcengine.visual.VisualService import VisualService
    visual_service = VisualService()
    visual_service.set_ak(ak)
    visual_service.set_sk(sk)

    start = time.time()
    while time.time() - start < max_wait:
        form = {
            "req_key": "jimeng_t2i_v40",
            "task_id": task_id,
        }
        resp = visual_service.cv_sync2_async_get_result(form)
        if resp and resp.get("code") == 10000:
            data = resp.get("data", {})
            status = data.get("status", "")
            if status == "done":
                return data
            elif status == "failed":
                print(f"  ❌ 任务失败")
                return None
        time.sleep(3)

    print(f"  ❌ 超时 ({max_wait}s)")
    return None


def download_image(url, save_path):
    """下载图片"""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    with open(save_path, "wb") as f:
        f.write(resp.content)


def main():
    parser = argparse.ArgumentParser(description="即梦API批量生图")
    parser.add_argument("prompts", help="prompts.json文件路径（场景号→prompt映射）")
    parser.add_argument("-o", "--output", default="images", help="输出目录（默认 images）")
    parser.add_argument("--ak", default=None, help="火山引擎AK（也可用环境变量VOLC_AK）")
    parser.add_argument("--sk", default=None, help="火山引擎SK（也可用环境变量VOLC_SK）")
    parser.add_argument("--width", type=int, default=1080, help="图片宽度（默认1080）")
    parser.add_argument("--height", type=int, default=1920, help="图片高度（默认1920）")
    parser.add_argument("--timeout", type=int, default=120, help="单任务超时秒数（默认120）")
    args = parser.parse_args()

    ak = args.ak or os.environ.get("VOLC_AK", "")
    sk = args.sk or os.environ.get("VOLC_SK", "")
    if not ak or not sk:
        print("❌ 需要火山引擎AK/SK，通过参数或环境变量(VOLC_AK/VOLC_SK)传入")
        sys.exit(1)

    if not os.path.exists(args.prompts):
        print(f"❌ 文件不存在: {args.prompts}")
        sys.exit(1)

    with open(args.prompts, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    os.makedirs(args.output, exist_ok=True)
    print(f"🎨 共 {len(prompts)} 个场景待生成")
    print(f"📐 尺寸: {args.width}x{args.height}")

    success = 0
    failed = 0

    for scene_key in sorted(prompts.keys()):
        prompt = prompts[scene_key]
        # 统一文件名格式
        if scene_key.isdigit():
            filename = f"scene_{int(scene_key):02d}.png"
        else:
            filename = f"{scene_key}.png"
        save_path = os.path.join(args.output, filename)

        # 跳过已存在的
        if os.path.exists(save_path):
            print(f"  ⏭️ 已存在: {filename}")
            success += 1
            continue

        print(f"  🎨 [{scene_key}] 提交生图: {prompt[:50]}...", end="", flush=True)

        task_id = submit_task(ak, sk, prompt, args.width, args.height)
        if not task_id:
            failed += 1
            continue

        print(f" 轮询中...", end="", flush=True)
        result = poll_task(ak, sk, task_id, args.timeout)
        if not result:
            failed += 1
            continue

        # 下载图片
        image_urls = result.get("image_urls", [])
        if not image_urls:
            # 尝试base64
            binary_data = result.get("binary_data_base64", [])
            if binary_data:
                img_data = base64.b64decode(binary_data[0])
                with open(save_path, "wb") as f:
                    f.write(img_data)
                print(f" ✅ {filename}")
                success += 1
                continue
            print(f" ❌ 无图片数据")
            failed += 1
            continue

        download_image(image_urls[0], save_path)
        print(f" ✅ {filename}")
        success += 1

    print(f"\n{'='*50}")
    print(f"📊 生图完成: ✅成功 {success} | ❌失败 {failed}")
    print(f"📁 输出目录: {args.output}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
