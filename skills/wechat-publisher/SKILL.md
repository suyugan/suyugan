---
name: wechat-publisher
description: Publish articles and content to WeChat Official Accounts (微信公众号). Supports regular articles with markdown/HTML and image posts (小绿书). Use when the user requests to publish, post, or upload content to WeChat Official Account, or mentions "公众号", "WeChat article", or "微信发布". Also use when user needs to see available WeChat accounts or choose which account to publish to.
---

# WeChat Official Account Publisher

Publish articles to WeChat Official Accounts via API.

## Quick Start

### 1. List Available Accounts

When user asks to publish but hasn't specified which account:

```bash
python3 scripts/list_accounts.py <api_key>
```

Display the accounts to user with name and wechatAppid, then ask which account to use.

### 2. Publish Article

Create a JSON config file with the article details:

```json
{
  "api_key": "your-api-key",
  "wechat_appid": "wx1234567890",
  "title": "Article Title",
  "content": "# Article Content\n\nMarkdown or HTML...",
  "content_format": "markdown",
  "article_type": "news"
}
```

Then run:

```bash
python3 scripts/publish_article.py config.json
```

## Publishing Workflows

### Regular Article (news)

For text-based articles with full formatting:

1. If user hasn't specified wechatAppid, run `list_accounts.py` and ask user to choose
2. Prepare article data:
   - **title**: Article title (max 64 chars)
   - **content**: Full article content in markdown or HTML
   - **content_format**: "markdown" or "html" (default: markdown)
   - **article_type**: "news"
   - Optional: summary, coverImage, author
3. Create JSON config with all fields
4. Run `publish_article.py` with config file
5. Report publication status to user

**Note**: If coverImage not provided, first image from content is auto-extracted as cover.

### Image Post (newspic / 小绿书)

For image-centric content with up to 20 images:

1. If user hasn't specified wechatAppid, run `list_accounts.py` and ask user to choose
2. Prepare article data:
   - **title**: Post title (max 64 chars)
   - **content**: Plain text description (max 600 chars)
   - **article_type**: "newspic"
   - **coverImage** and/or **mainImages**: At least one required
     - coverImage: Single cover image URL
     - mainImages: Array of up to 20 image URLs
3. Create JSON config with all fields
4. Run `publish_article.py` with config file
5. Report publication status to user

**Important**: newspic requires images via coverImage or mainImages parameters. Images are merged in order: coverImage → mainImages (auto-deduplicated).

## API Configuration

API key is required for all operations. Ask user to provide their API key from https://wx.limyai.com platform.

Store the API key in `~/.claude/skills/wechat-publisher/.api_key` file for reuse:
```bash
echo "your-api-key-here" > ~/.claude/skills/wechat-publisher/.api_key
```

Read the stored API key:
```bash
cat ~/.claude/skills/wechat-publisher/.api_key
```

## Error Handling

Common errors and solutions:

- **ACCOUNT_NOT_FOUND**: Ask user to verify wechatAppid or list accounts again
- **ACCOUNT_TOKEN_EXPIRED**: Account needs re-authorization on the platform
- **NO_IMAGES**: For newspic, must provide coverImage or mainImages
- **INVALID_PARAMETER**: Check title length (≤64 chars), content format, and required fields

## Auto-Publish (Direct Publish, Not Just Draft)

By default, `publish_article.py` only saves to draft box. To auto-publish:

1. Add `"auto_publish": true` to the JSON config
2. The script will: save to draft → get media_id → call WeChat freepublish API → submit for publishing

Or manually after getting media_id:
```bash
python scripts/free_publish.py <media_id>
```

**Note**: Free publish uses WeChat official API with AppID/AppSecret (hardcoded for 苏煜淦 account). The publish is async — WeChat processes it and the article goes live within minutes.

## Resources

### scripts/
- `list_accounts.py`: Fetch all authorized WeChat accounts
- `publish_article.py`: Publish article to specified account (supports auto_publish)
- `free_publish.py`: Submit draft to free publish via WeChat official API

### references/
- `api_docs.md`: Complete API documentation with examples and error codes
