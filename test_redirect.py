"""Test redirect"""
import requests

url = "https://v.douyin.com/iF6QvJ2j/"

# Get redirect
r = requests.get(url, allow_redirects=False)

print("Status:", r.status_code)
print("Location:", r.headers.get('Location'))

# Follow redirect
final_url = r.headers.get('Location', url)
print("Final URL:", final_url)
