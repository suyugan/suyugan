"""
测试视频分析 API
"""

import requests
import json
import time
from datetime import datetime
import sys

# Fix encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("=" * 50)
print("  Video Analysis API Test")
print("=" * 50)
print()

# API endpoint
api_url = "http://localhost:5000"

# Test videos
test_videos = [
    {
        'name': 'Douyin Popular Video',
        'url': 'https://v.douyin.com/iF6QvJ2j/'
    },
    {
        'name': 'Test Video 2',
        'url': 'https://www.douyin.com/video/7300000000000000000'
    }
]

print(f"[1/5] Checking API health status...")
print()

try:
    health_response = requests.get(f"{api_url}/health", timeout=5)
    health_data = health_response.json()

    print(f"Health Status: {health_data.get('status', 'unknown')}")
    print(f"Service: {health_data.get('service', 'unknown')}")
    print()

    if health_data.get('status') != 'ok':
        print("API health check failed!")
        sys.exit(1)

    print("API health check passed!")
    print()

except Exception as e:
    print(f"Health check failed: {e}")
    sys.exit(1)

print(f"[2/5] Querying API service status...")
print()

try:
    status_response = requests.get(f"{api_url}/api/status", timeout=5)
    status_data = status_response.json()

    print(f"API Status: {status_data.get('status', 'unknown')}")
    print(f"Available APIs: {status_data.get('apis_available', 0)}")
    print(f"Available API services:")
    for api in status_data.get('apis', []):
        print(f"  - {api}")
    print()

    if status_data.get('status') != 'running':
        print("API is not running!")
        sys.exit(1)

    print("API service is running!")
    print()

except Exception as e:
    print(f"Status query failed: {e}")
    sys.exit(1)

print(f"[3/5] Preparing test videos...")
print()

for i, video in enumerate(test_videos, 1):
    print(f"{i}. {video['name']}")
    print(f"   URL: {video['url']}")
    print()

print("=" * 50)
print()

# Select first video for testing
test_video = test_videos[0]

print(f"[4/5] Starting video analysis...")
print(f"Video: {test_video['name']}")
print(f"URL: {test_video['url']}")
print()
print("Analyzing, please wait...")
print()

start_time = time.time()

try:
    # Send analysis request
    analyze_response = requests.post(
        f"{api_url}/api/analyze",
        json={'url': test_video['url']},
        timeout=30
    )

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"Analysis completed! Time: {elapsed:.2f} seconds")
    print()

    if analyze_response.status_code == 200:
        result = analyze_response.json()

        if result.get('success'):
            print("=" * 50)
            print("  Analysis Successful!")
            print("=" * 50)
            print()

            data = result.get('data', {})

            print(f"Title: {data.get('title', 'N/A')}")
            print(f"Author: {data.get('uploader', 'N/A')}")
            print()

            print("Interaction Data:")
            print(f"  Views: {data.get('view_count', 0):,}")
            print(f"  Likes: {data.get('like_count', 0):,}")
            print(f"  Comments: {data.get('comment_count', 0):,}")
            print(f"  Shares: {data.get('share_count', 0):,}")
            print()

            if data.get('bgm'):
                print(f"BGM: {data.get('bgm', 'N/A')}")
                print()

            print(f"API Used: {result.get('api_used', 'Unknown')}")
            print()

            print("=" * 50)
            print("  JSON_OUTPUT_START")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            print("  JSON_OUTPUT_END")
            print("=" * 50)

            print()
            print(f"[5/5] Test completed!")

        else:
            print("=" * 50)
            print("  Analysis Failed")
            print("=" * 50)
            print()
            print(f"Error: {result.get('error', 'Unknown error')}")

    else:
        print("=" * 50)
        print(f"  Request Failed (HTTP {analyze_response.status_code})")
        print("=" * 50)
        print()
        print(f"Response: {analyze_response.text}")

except requests.exceptions.Timeout:
    print(f"Request timeout (exceeded 30 seconds)")

except Exception as e:
    print(f"Analysis failed: {e}")

print()
print("=" * 50)
