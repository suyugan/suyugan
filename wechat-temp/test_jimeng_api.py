import json, hashlib, hmac, datetime, urllib.request, urllib.parse

AK = "REDACTED_VOLC_AK"
SK = "ZmU3NzE3OGJmMDkwNDgxNWI4MWU5MjBhNTU5MzU0YjY"

# Volcengine Visual API - Jimeng image generation
# Using the visual API endpoint
SERVICE = "cv"
REGION = "cn-north-1"
HOST = "visual.volcengineapi.com"
ACTION = "CVProcess"
VERSION = "2022-08-31"

def sign(key, msg):
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_signature_key(secret_key, date_stamp, region, service):
    k_date = sign(secret_key.encode('utf-8'), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'request')
    return k_signing

now = datetime.datetime.utcnow()
date_stamp = now.strftime('%Y%m%d')
amz_date = now.strftime('%Y%m%dT%H%M%SZ')

# Request body for image generation
body = json.dumps({
    "req_key": "jimeng_high_aes_general_v21",
    "prompt": "A cute cat sitting on a windowsill, flat illustration style",
    "width": 512,
    "height": 512,
    "seed": -1,
    "scale": 3.5,
    "ddim_steps": 16,
    "return_url": True,
})

# Build canonical request
method = "POST"
canonical_uri = "/"
canonical_querystring = f"Action={ACTION}&Version={VERSION}"
content_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
canonical_headers = f"content-type:application/json\nhost:{HOST}\nx-date:{amz_date}\n"
signed_headers = "content-type;host;x-date"
canonical_request = f"{method}\n{canonical_uri}\n{canonical_querystring}\n{canonical_headers}\n{signed_headers}\n{content_hash}"

# Build string to sign
algorithm = "HMAC-SHA256"
credential_scope = f"{date_stamp}/{REGION}/{SERVICE}/request"
string_to_sign = f"{algorithm}\n{amz_date}\n{credential_scope}\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

# Calculate signature
signing_key = get_signature_key(SK, date_stamp, REGION, SERVICE)
signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

# Build authorization header
authorization = f"{algorithm} Credential={AK}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"

url = f"https://{HOST}/?{canonical_querystring}"
headers = {
    "Content-Type": "application/json",
    "Host": HOST,
    "X-Date": amz_date,
    "Authorization": authorization,
}

req = urllib.request.Request(url, data=body.encode('utf-8'), headers=headers, method="POST")
try:
    resp = urllib.request.urlopen(req, timeout=30)
    result = json.loads(resp.read())
    print("SUCCESS!")
    print(json.dumps(result, indent=2, ensure_ascii=False)[:1000])
except urllib.error.HTTPError as e:
    print(f"HTTP {e.code}: {e.read().decode()[:500]}")
except Exception as e:
    print(f"Error: {e}")
