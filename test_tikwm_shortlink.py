"""
Test TikWM API with short link format
"""

import requests
import json

print("=" * 50)
print("  Testing TikWM API with Short Link")
print("=" * 50)
print()

# Test with short link
short_url = "https://v.douyin.com/iF6QvJ2j/"

print(f"Testing with short link: {short_url}")
print()

try:
    # Test TikWM API
    url = "https://www.tikwm.com/api/"
    params = {'url': short_url}

    print(f"Request: {url}")
    print(f"Params: {params}")
    print()

    response = requests.get(url, params=params, timeout=10)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    print()

    if response.status_code == 200:
        data = response.json()

        print(f"JSON Keys: {list(data.keys())}")
        print()

        if 'code' in data:
            print(f"Code: {data['code']}")
            print(f"Message: {data.get('msg', '')}")

            if data['code'] == 0 and 'data' in data:
                print("\nSUCCESS! Data received:")
                print(json.dumps(data['data'], indent=2, ensure_ascii=False))
            else:
                print("\nAPI returned an error")

except Exception as e:
    print(f"Error: {e}")

print()
print("=" * 50)
