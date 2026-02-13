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
- **当前状态：调试闪退中**（v8测试：空操作hook，等结果）
- IPA基础：秋名山版WeChat 8.0.69，用lief注入LOAD_WEAK_DYLIB
- 用巨魔(TrollStore)安装
- 默认推送地址：`http://bm.weiixxin.com/wechat-sync/api/messages`
- GitHub Actions编译(macOS-14)，commit触发或手动dispatch
- constructor问题：必须用`-Wl,-init,_函数名` + 非static + `__attribute__((used))`
- **闪退排查进度**：空dylib不崩，空操作hook待测，怀疑方法签名不匹配
- 测试版用 WCGroupSync_minimal.m，正式版用 WCGroupSync.m
- workflow当前编译minimal版本（记得改回来！）

## 展示页面
- Showcase: http://bm.weiixxin.com/wechat-sync/showcase（仿laolin.ai/showcase）
- Dashboard: http://bm.weiixxin.com/wechat-sync/

## 工作流程配置（切换模型后必须保持）

### 视频制作→发布抖音 流程
1. 分析参考视频：用视频分析API (http://localhost:18810) 下载+抽帧+转录
2. 写文案：模仿风格，原创内容，画面精确匹配文案
3. 生成配图：优先用 Replicate FLUX / Google Imagen / HuggingFace FLUX Space
4. 配音：用TTS生成语音
5. 合成视频：FFmpeg或Remotion
6. **发布抖音**：浏览器自动化打开 creator.douyin.com，上传+填写信息+发布（网页版，非headless）

### KOL舆情监控
- topic-monitor skill，每天9:00自动运行（cron job）
- 监控：宝玉(@dotey)、乔木/归藏(@op7418)
- 搜索引擎：Tavily（key: REDACTED_TAVILY_KEY）
- topic-monitor已修复Windows兼容（python3→python, encoding=utf-8, 系统环境变量）

### 子代理任务规则
- **任务失败必须立即通知用户！不能静默失败！**
- 定期检查子代理状态（每5-10分钟）
- 发现卡住/失败立即告知并提供解决方案
- 多步骤任务先spawn准备工作（如登录），再spawn主任务

### API Keys
- Tavily: REDACTED_TAVILY_KEY
- Google Gemini: REDACTED_GEMINI_KEY

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