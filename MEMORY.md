# MEMORY.md - Your Long-Term Memory

This file stores distilled learnings, important decisions, and crucial context that should persist across sessions.

## 重要长期记忆

### 域名与服务器
- **域名**: `weiixxin.com`（不是 .net！），主域名留给官网
- **部署域名**: `bm.weiixxin.com` + 路径后缀（/bookmarks/, /wechat/ 等）
- **服务器**: 腾讯云 106.55.158.137，Nginx 反代
- **GitHub**: https://github.com/suyugan/suyugan (branch: master)

### 微信环境
- 用户使用**新版微信 xwechat**（非传统 PC 微信）
- 传统 PC 微信 3.9.12.51 已安装在 D:\WeChat（给 WeChatFerry 用）
- 微信窗口类: Qt51514QWindowIcon
- 截图默认截置顶群

### 用户兴趣
- 小红书运营
- 产品经理工具
- AI 视频生成（即梦AI）
- 微信群消息采集

## 苏总习惯与要求
- 账号密码双重存储：本地 + 腾讯云 `/home/ubuntu/.credentials/accounts.md`
- 需要账号密码先SSH服务器查，没有再问苏总
- 重要信息立刻写文件，不能靠"记住"
- 说话简洁不废话，回复不要英文翻译
- 所有回复用中文

## 微信插件 WCGroupSync
- 最终版本：v4（去掉设置页hook）
- IPA路径：`D:\wechat-plugin-dev\WeChat-GroupSync-v4.ipa`
- 用巨魔安装，插件静默运行
- 默认推送地址：`http://bm.weiixxin.com/wechat-sync/api/messages`
- GitHub Actions编译，commit触发或手动dispatch
- constructor问题：必须用`-Wl,-init,_函数名` + 非static + `__attribute__((used))`

## 展示页面
- Showcase: http://bm.weiixxin.com/wechat-sync/showcase（仿laolin.ai/showcase）
- Dashboard: http://bm.weiixxin.com/wechat-sync/

## 2026-02-08 Updates

### Key Accomplishments
- **Tencent Cloud Server Fixes:** Successfully debugged and re-deployed `server.js` on Tencent Cloud (106.55.158.137) via SSH+Python, addressing API path and image URL issues. Also updated Nginx `server_name` and verified DNS.
- **"看群" Shortcut Registered:** The shortcut command "看群" is now registered to execute the WeChat screenshot task.
- **ADB Connection & AutoGLM Configured:** Phone (192.168.41.203:39075) is successfully connected via ADB, and AutoGLM is configured for phone control.
- **Automated Tasks via Cron:** Implemented cron jobs for 3-hourly screenshots, daily summaries, hourly file syncing, and 6-hourly screenshot cleanup.

### Ongoing Work
- **GitHub Integration:** Awaiting remote repository URL from the user to push the workspace code.
- **New Text-Based Message System:** Development started on a new text-based WeChat message monitoring system on port 3001, distinct from the existing screenshot system.

### Challenges/Limitations
- **WeChat Image Encryption:** Images downloaded from PC WeChat are encrypted (.dat format) and cannot be directly processed unless manually opened by the user. This limits automated image syncing.