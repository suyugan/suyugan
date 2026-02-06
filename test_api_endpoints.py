"""
测试各个 API 端点
"""

import requests
import json

print("=" * 50)
print("  Testing API Endpoints")
print("=" * 50)
print()

# Test videos
test_url = "https://www.douyin.com/video/7578250796459146597"

# API services
api_services = [
    {
        'name': 'DS720 API',
        'url': 'http://192.168.1.100:18810/api/hybrid/video_data',
        'method': 'GET'
    },
    {
        'name': 'TikWM API',
        'url': 'https://www.tikwm.com/api/',
        'method': 'GET'
    },
    {
        'name': 'Douyin API',
        'url': 'https://api.douyin.wtf/api/v1/video',
        'method': 'GET'
    }
]

for api in api_services:
    print(f"Testing {api['name']}...")
    print(f"URL: {api['url']}")
    print()

    try:
        if api['method'] == 'GET':
            # Try different parameter formats
            params_formats = [
                {'url': test_url, 'minimal': 'true'},
                {'url': test_url},
                {'url': test_url, 'count': 12},
            ]

            for i, params in enumerate(params_formats, 1):
                print(f"  Attempt {i}: params = {params}")
                try:
                    response = requests.get(api['url'], params=params, timeout=10)
                    print(f"  Status Code: {response.status_code}")
                    print(f"  Response (first 500 chars): {response.text[:500]}")

                    if response.status_code == 200:
                        try:
                            data = response.json()
                            print(f"  JSON Keys: {list(data.keys())}")
                            if 'data' in data:
                                print(f"  Data Keys: {list(data['data'].keys())}")
                        except:
                            pass

                except Exception as e:
                    print(f"  Error: {e}")

                print()

    except Exception as e:
        print(f"  Error: {e}")

    print("-" * 50)
    print()
