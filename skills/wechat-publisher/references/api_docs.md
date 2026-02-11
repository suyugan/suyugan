# WeChat Official Account Publishing API Documentation

## Base Information

- **Base URL**: https://wx.limyai.com/api/openapi
- **Authentication**: X-API-Key header
- **Content-Type**: application/json

## API Endpoints

### 1. Get Account List

Fetch all authorized WeChat Official Accounts.

**Endpoint**: `POST /wechat-accounts`

**Headers**:
```
X-API-Key: your-api-key
Content-Type: application/json
```

**Request**: No body required

**Response** (Success):
```json
{
  "success": true,
  "data": {
    "accounts": [
      {
        "name": "测试公众号",
        "wechatAppid": "wx1234567890",
        "username": "gh_abc123",
        "avatar": "https://...",
        "type": "subscription",
        "verified": true,
        "status": "active",
        "lastAuthTime": "2024-01-01T00:00:00.000Z",
        "createdAt": "2024-01-01T00:00:00.000Z"
      }
    ],
    "total": 1
  }
}
```

### 2. Publish Article

Publish article to WeChat Official Account draft box.

**Endpoint**: `POST /wechat-publish`

**Headers**:
```
X-API-Key: your-api-key
Content-Type: application/json
```

**Request Body**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| wechatAppid | string | Yes | WeChat Official Account AppID |
| title | string | Yes | Article title (max 64 chars) |
| content | string | Yes | Article content (markdown or HTML) |
| summary | string | No | Article summary (max 120 chars) |
| coverImage | string | Conditional | Cover image URL (required for newspic without mainImages) |
| mainImages | string[] | Conditional | Main image URLs (max 20, required for newspic without coverImage) |
| author | string | No | Author name |
| contentFormat | string | No | "markdown" (default) or "html" |
| articleType | string | No | "news" (default) or "newspic" |

**Response** (Success):
```json
{
  "success": true,
  "data": {
    "publicationId": "uuid-here",
    "materialId": "uuid-here",
    "mediaId": "wechat-media-id",
    "status": "published",
    "message": "文章已成功发布到公众号草稿箱"
  }
}
```

**Response** (Error):
```json
{
  "success": false,
  "error": "公众号不存在或未授权",
  "code": "ACCOUNT_NOT_FOUND"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| API_KEY_MISSING | API key not provided |
| API_KEY_INVALID | Invalid API key |
| ACCOUNT_NOT_FOUND | Account not found or unauthorized |
| ACCOUNT_TOKEN_EXPIRED | Account authorization expired |
| INVALID_PARAMETER | Invalid parameters |
| NO_IMAGES | newspic mode requires images |
| IMAGE_UPLOAD_FAILED | All images failed to upload |
| WECHAT_API_ERROR | WeChat API call failed |
| INTERNAL_ERROR | Server internal error |

## Article Types

### Regular Article (news)
- Default type for text-based articles
- Supports markdown and HTML content
- Auto-extracts first image as cover if not specified
- Full formatting support

### Image Post (newspic / 小绿书)
- Image-centric format
- Requires coverImage or mainImages (at least one)
- Text limited to 600 characters (plain text only)
- Max 20 images
- Images merged: coverImage → mainImages (deduplicated)
- Best for visual content

## Examples

### Example 1: Regular Article
```json
{
  "wechatAppid": "wx1234567890",
  "title": "测试文章",
  "content": "# 标题\n\n这是文章内容...",
  "summary": "这是文章摘要",
  "contentFormat": "markdown",
  "articleType": "news"
}
```

### Example 2: Image Post (小绿书)
```json
{
  "wechatAppid": "wx1234567890",
  "title": "小绿书测试",
  "content": "这是纯文本描述，图片通过参数传入",
  "coverImage": "https://example.com/cover.jpg",
  "mainImages": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg"
  ],
  "articleType": "newspic"
}
```
