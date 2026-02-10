# 微信 8.0.69 插件开发完整参考手册

> 基于 IPA 大礼包（秋名山版）11 个 dylib 插件 + 微信主程序二进制逆向分析
> 分析日期: 2026-02-10 | 目标: WeChat 8.0.69 TestFlight (arm64, iOS 15+)

---

## 目录

1. [插件生态总览](#1-插件生态总览)
2. [Hook 引擎: libellekit](#2-hook-引擎-libellekit)
3. [插件注册系统: wcplugins+](#3-插件注册系统-wcplugins)
4. [核心 Hook 点速查表](#4-核心-hook-点速查表)（消息/联系人/群聊/红包/会话/媒体/UI/登录/同步/朋友圈/支付/小程序/数据库/CDN/表情/视频号/通话）
5. [CMessageWrap 消息模型](#5-cmessagewrap-消息模型)
6. [CContact 联系人模型](#6-ccontact-联系人模型)
7. [ChatRoomData 群聊数据模型](#7-chatroomdata-群聊数据模型)
8. [WCPayInfoItem 支付模型](#8-wcpayinfoitem-支付模型)
9. [MMSessionInfo 会话模型](#9-mmsessioninfo-会话模型)
10. [XML 消息结构参考](#10-xml-消息结构参考)
11. [功能实现参考](#11-功能实现参考)（防撤回/红包/广告屏蔽/步数/定位/AI/TTS/视频保存/群管理/推送/暗色模式/版本伪装/自动下载/备份/定时发送/字体/隐私/键盘/斗图/自动回复/好友验证）
12. [NSUserDefaults 配置键速查](#12-nsuserdefaults-配置键速查)
13. [设置页 UI 构建模式](#13-设置页-ui-构建模式)
14. [常用工具方法](#14-常用工具方法)
15. [微信内部 UI 组件](#15-微信内部-ui-组件)
16. [开发最佳实践](#16-开发最佳实践)
17. [附录](#17-附录)

---

## 1. 插件生态总览

IPA 中包含 11 个 dylib，各自角色如下：

| 插件 | 大小 | 语言 | 功能定位 |
|------|------|------|----------|
| **libellekit.dylib** | — | Swift/C | Hook 引擎，替代 CydiaSubstrate，提供 `MSHookMessageEx` 兼容层 |
| **wcplugins+.dylib** | 125 KB | ObjC | 插件管理框架，提供统一设置入口和注册 API |
| **MikotoHelper.dylib** | 75 MB | ObjC | 全功能插件（红包/防撤回/群管理/AI/定时任务/朋友圈/语音/美化） |
| **PKCWeChatTools.dylib** | 3.7 MB | ObjC | 全功能插件（防撤回/群管理/AI多模型/TTS/步数修改/自动化/暗色模式） |
| **HBWechatHelper.dylib** | 39 MB | ObjC | 全功能插件（防撤回/红包/群管理/语音中心/键盘增强/FFmpeg内嵌） |
| **WCPulse.dylib** | — | ObjC | 增强插件（防撤回/暗色主题/自定义字体/Finder视频/群管理/AI/备份） |
| **WCEhance.dylib** | — | ObjC | 轻量插件（防撤回/暗色主题/版本伪装/美化） |
| **MiYou.dylib** | 12.5 MB | ObjC | 全功能插件（防撤回/虚拟定位/步数/ChatGPT/自动下载/文件管理） |
| **HBB9.1.1.dylib** | 18 MB | Swift | 高度混淆插件（登录控制/推送通知拦截/URL Scheme劫持） |
| **DouTu.dylib** | 3.6 MB | ObjC | 斗图/表情包专用（批量下载/收藏/自定义API） |
| **FuckWeChatAdBlocker.dylib** | 103 KB | ObjC | 广告屏蔽专用（开屏/信息流/视频号/公众号/朋友圈广告） |

---

## 2. Hook 引擎: libellekit

所有插件统一使用 **ellekit** 作为 Hook 框架（现代 CydiaSubstrate 替代品）。

### 2.1 链接方式

```
@executable_path/Frameworks/libellekit.dylib
```

### 2.2 Hook 实现机制

1. **直接分支重写** — 修改函数开头指令跳转到 hook 函数
2. **异常处理器方式** — 设置 Mach exception handler
3. **JIT hook** — 通过 `task_set_state` 修改线程状态
4. **小函数特殊处理** — 对过短函数有专门策略

### 2.3 兼容 API

```c
// CydiaSubstrate 兼容
MSHookMessageEx()       // ObjC method hook

// libhooker 兼容
LHHookFunctions()       // 批量 hook
```

### 2.4 推荐 Hook 方式（无需 ellekit 依赖）

```objc
#import <objc/runtime.h>

static IMP orig_method = NULL;

void hooked_method(id self, SEL _cmd, NSString *arg1, id arg2) {
    // 调用原始方法
    ((void(*)(id, SEL, NSString*, id))orig_method)(self, _cmd, arg1, arg2);
    // 自定义逻辑
}

__attribute__((constructor))
static void init() {
    Class cls = NSClassFromString(@"CMessageMgr");
    if (!cls) return;
    SEL sel = NSSelectorFromString(@"AsyncOnAddMsg:MsgWrap:");
    Method m = class_getInstanceMethod(cls, sel);
    if (!m) return;
    orig_method = method_setImplementation(m, (IMP)hooked_method);
}
```

---

## 3. 插件注册系统: wcplugins+

### 3.1 注册 API

```objc
// 通过 wcplugins+ 注册插件到统一管理界面
Class pluginsMgr = NSClassFromString(@"WCPluginsMgr");
SEL registerSel = NSSelectorFromString(@"registerControllerWithTitle:version:controller:");
// 调用注册
```

### 3.2 核心类

| 类名 | 作用 |
|------|------|
| `WCPluginsMgr` | 插件管理器单例 |
| `WCPluginModel` | 插件数据模型 |
| `WCPluginsViewController` | 插件列表界面 |

### 3.3 密码保护

- `WCPLUGINHIDE` — 隐藏插件入口
- `WCPLUGINHIDEPASS` / `WCPLUGINLOCKPASS` — 密码锁定

### 3.4 设置页注入（不依赖 wcplugins+）

直接 Hook 微信设置页：

```objc
// 方式 1: Hook NewSettingViewController.reloadTableData
// 方式 2: Hook MoreViewController.viewDidLoad
// 方式 3: Hook SettingMyAccountExtInfoLogic
```

---

## 4. 核心 Hook 点速查表

### 4.1 消息系统

这是所有插件最核心的 Hook 区域。

#### 消息接收链（按调用顺序）

| 方法 | 类 | 用途 | 使用该 Hook 的插件 |
|------|-----|------|-------------------|
| `AsyncOnPreAddMsg:MsgWrap:` | `CMessageMgr` | 消息进入前预处理（最早拦截点） | PKC, WCPulse, HBWechatHelper |
| `AddMsg:MsgWrap:` | `CMessageMgr` | 消息写入数据库 | MikotoHelper, PKC, WCPulse, WCEhance, HBWechatHelper |
| `AsyncOnAddMsg:MsgWrap:` | `CMessageMgr` | 消息已添加通知（最常用） | **所有插件** |
| `BatchAddMsg:ShowPush:` | `CMessageMgr` | 批量消息同步（含离线消息） | MiYou |
| `AsyncOnAddMsgListForSession:NotifyUsrName:` | `CMessageMgr` | 会话列表更新 | MikotoHelper |
| `OnAddMsg:MsgWrap:` | `BaseMsgContentLogicController` | 聊天界面消息到达 | 微信主程序 |

#### 消息发送

| 方法 | 类 | 用途 |
|------|-----|------|
| `AddSendMsg:MsgWrap:` | `CMessageMgr` | 拦截自己发送的消息 |
| `SendTextMessage:replyingMessage:isPasted:` | `BaseMsgContentLogicController` | 发送文本消息 |
| `SendImageMessage:withData:ImageInfo:` | `BaseMsgContentLogicController` | 发送图片消息 |

#### 消息撤回（防撤回）

**所有** 6 个功能型插件都 Hook 了撤回系统：

| 方法 | 类 | 用途 |
|------|-----|------|
| `onRevokeMsg:` | `CMessageMgr` | **核心撤回入口**，拦截此方法即可防撤回 |
| `OnRevokeMsg:MsgWrap:ResultCode:ResultMsg:EducationMsg:` | `BaseMsgContentLogicController` | 撤回完整回调 |
| `BatchRevokeMsg:withReportInterval:` | `BaseMsgContentLogicController` | 批量撤回 |
| `reloadRevokeMsg:after:` | `CMessageMgr` | 重新加载撤回消息 |
| `onRevokeRoomHistory:msg:` | `CMessageMgr` | 群历史消息撤回 |
| `InsertRevokeMessage:` | `CMMDB(RevokeMessage)` | 撤回记录写入DB |

#### VoIP 消息

| 方法 | 类 | 用途 |
|------|-----|------|
| `HandleVoipMsg:MsgWrap:` | `CMessageMgr` | 处理 VoIP 消息 |
| `voipBubbleMsg` | `CMessageWrap(Voip)` | 生成 VoIP 气泡消息 |

### 4.2 联系人系统

| 方法 | 类 | 用途 |
|------|-----|------|
| `getContactByName:` | `CContactMgr` | 按 userName 查联系人（**全部插件使用**） |
| `getContactByAlias:` | `CContactMgr` | 按微信号查联系人 |
| `getContactList:contactType:` | `CContactMgr` | 获取联系人列表 |
| `getContactFromDic:` | `CContactMgr` | 从字典创建联系人 |
| `getContactsFromServer:chatContact:withScene:withTicket:usrData:` | `CContactMgr` | 从服务器拉取完整资料 |
| `getContactAvatarWithUsername:` | — | 获取联系人头像 |
| `deleteContact:listType:andScene:sync:local:` | `CContactMgr` | 删除联系人 |

### 4.3 群聊管理

| 方法 | 类 | 用途 |
|------|-----|------|
| `addMembers:toGroup:withScene:` | `WCGroupMgr` | 添加群成员 |
| `removeMembers:fromGroup:withScene:` | `WCGroupMgr` | 移除群成员 |
| `deleteGroup:` | `WCGroupMgr` | 删除群 |
| `doGroupOp:onGroup:withGroupName:` | `WCGroupMgr` | 群操作 |
| `doGroupMemberOp:onGroup:withGroupName:withMemberList:` | `WCGroupMgr` | 群成员操作 |
| `loadMemberList` | `ChatRoomInfoViewController` | 加载群成员列表 |
| `parseData:` | `ChatRoomData` | 解析群数据 |
| `getDataForUserName:key:` | `ChatRoomData` | 获取群内用户数据 |

### 4.4 红包系统

| 方法 | 类 | 用途 |
|------|-----|------|
| `OpenRedEnvelopesRequest:` | `WCRedEnvelopesReceiveControlLogic` | 拆红包请求（主方案） |
| `OnWCToHongbaoCommonResponse:Request:` | — | 红包响应回调 |
| `openNativeUrl:` | `WCBizUtil` | 打开原生URL（降级方案B） |
| `handleScheme:` | `WCSchemeLinker` | 处理URL Scheme（降级方案C） |

**红包检测**: msg_type=49，XML 中 `<type>2001</type>`，nativeUrl 从 `<wcpayinfo><nativeurl>` 提取。

### 4.5 会话管理

| 方法 | 类 | 用途 |
|------|-----|------|
| `GetSessionByUserName:` | `MMNewSessionMgr` | 按用户名获取会话 |
| `AddSessionToTop:` | `MMNewSessionMgr` | 置顶会话 |
| `DeleteSessionOfUser:` | `MMNewSessionMgr` | 删除会话 |
| `ChangeSessionUnReadCount:to:` | `MMNewSessionMgr` | 修改未读数 |
| `hideSession:` / `showSession:` | `MMNewSessionMgr` | 隐藏/显示会话 |
| `TopSessionByName:` / `UntopSessionByName:needSync:` | `MMNewSessionMgr` | 置顶/取消置顶 |
| `getUnreadCountInSession:` | `MMNewSessionMgr` | 获取未读计数 |
| `rebuildMainSessions` | `MainSessionMgr` | 重建会话列表 |

### 4.6 图片/媒体下载

| 方法 | 类 | 用途 |
|------|-----|------|
| `StartDownloadImage:HD:AutoDownload:SaveAlbum:Silent:` | `CMessageMgr` | 下载图片（5参数） |
| `StartDownloadImage:HD:AutoDownload:SaveAlbum:Silent:behavior:` | `CMessageMgr` | 下载图片（6参数） |
| `StartDownloadImage:HD:AutoDownload:` | `CMessageMgr` | 下载图片（3参数） |
| `StartDownloadVideo:MsgWrap:Priority:` | `CMessageMgr` | 下载视频 |
| `StartDownloadAppAttach:MsgWrap:` | `CMessageMgr` | 下载附件 |

**WXAM 图片解码**（微信私有格式）:

```objc
// magic bytes: 0x77786766 ("wxgf")
Class animDecCls = NSClassFromString(@"WxAMAnimatedImageDecoder");
SEL imgSel = NSSelectorFromString(@"imageWithWxAMData:scale:");
// NSInvocation 调用，scale=1.0，返回 UIImage
// 注意: decodeWxAMToJpg:scene: 会崩溃，不要用
```

### 4.7 UI / ViewController 生命周期

| 方法 | 类 | 用途 |
|------|-----|------|
| `viewDidLoad` | 多个 VC | 注入自定义 UI 元素（**全部插件**） |
| `viewWillAppear:` | 多个 VC | 页面即将显示时修改 |
| `reloadTableData` | `NewSettingViewController` | 刷新设置页表格（注入入口） |
| `setBadgeValue:` | `UITabBarItem` | 修改角标 |
| `pushViewController:animated:` | `UINavigationController` | 页面跳转 |

### 4.8 登录/账号系统

| 方法 | 类 | 用途 |
|------|-----|------|
| `startIPadLoginLogic` | `WCAccountManualLoginControlMgr` | iPad 登录逻辑 |
| `startLoginLogic:Data:` | `WCAccountLoginControlLogic` | 通用登录逻辑 |
| `onGetQRCodeImg:` | `WCAccountLoginByQRCodeViewController` | 二维码登录图片 |
| `startGatewayLogin:mobile:callback:` | `WCAccountLoginTypeControlMgr` | 网关登录 |

### 4.9 同步系统

| 方法 | 类 | 用途 |
|------|-----|------|
| `HandleNewSyncPush:` | `NewSyncService` | **核心**——处理所有入站同步推送 |
| `HandleSyncResp:handleResult:` | `NewSyncService` | 同步响应处理 |
| `HandleOplog:Event:` | `NewSyncService` | 操作日志处理 |
| `ProcessStartSync` | `NewSyncService` | 开始同步 |
| `BackGroundToForeGroundSync` | `NewSyncService` | 前后台切换同步 |

### 4.10 朋友圈/发现页

| 方法 | 类 | 用途 |
|------|-----|------|
| `doSelectCell:` | `FindFriendEntryViewController` | 发现页 cell 点击 |
| `requestForSnsTimeLineRequest:minId:lastRequestTime:pageType:isUnReadJump:` | `WCTimelineDataProvider` | 请求朋友圈数据 |
| `responseForSnsTimeLineResponse:Event:` | `WCTimelineDataProvider` | 处理朋友圈响应 |
| `startRequest` | `WCTimelineBatchGetFeedsCGI` | 批量获取朋友圈 |
| `createDraft` / `setDraftText:` / `setDraftImages:needCopyImageToFile:` | `WCTimelineEnhanceDraftController` | 发朋友圈草稿 |
| `tryToPullSnsAd:` / `delAdWithSnsId:SnsId:` | `WCTimelineDataProvider(AD)` | 朋友圈广告拉取/删除 |

### 4.11 服务中心（获取任意服务）

```objc
// MMServiceCenter 是获取微信内部服务的核心 API
MMServiceCenter *center = [MMServiceCenter defaultCenter];

// 获取消息管理器
CMessageMgr *msgMgr = [center getService:[NSClassFromString(@"CMessageMgr") class]];

// 获取联系人管理器
CContactMgr *contactMgr = [center getService:[NSClassFromString(@"CContactMgr") class]];

// 获取群管理器
WCGroupMgr *groupMgr = [center getService:[NSClassFromString(@"WCGroupMgr") class]];

// 获取会话管理器
MMNewSessionMgr *sessionMgr = [center getService:[NSClassFromString(@"MMNewSessionMgr") class]];
```

### 4.12 支付/转账系统

| 方法 | 类 | 用途 |
|------|-----|------|
| `doAuthenticationPayWithPwd:isTouchIDAuth:` | `WCPayPayMoneyLogic` | 执行支付 |
| `_cancelPay` | `WCPayPayMoneyLogic` | 取消支付 |
| `call:` | `WCPayTransferMoneyControlLogic` | 发起转账 |
| `GetTransferPrepayRequest:isSencondRequest:placeOrderAttatch:` | `WCPayTransferMoneyControlLogic` | 转账预支付 |
| `onPayMoneyLogicSuccess` | `WCPayTransferMoneyControlLogic` | 转账成功回调 |
| `handlePayResult:` | `WCPayOfflinePayMainLogic` | 离线支付结果 |
| `updateCodeImageWithPayCodeStyle:` | `WCPayOfflinePayCodeView` | 更新付款码 |
| `launchActivityAARequestWithActivityTheme:totalAmount:payerItems:` | `WCPayGPLaunchControlLogic` | 发起 AA 付款 |
| `startBalanceDetailLogic` | `WCPayBalanceDetailControlLogic` | 余额详情 |
| `call:` | `WCPayBalanceFetchMoneyControlLogic` | 提现 |
| `checkIsCanSendRedEnvelopesLogic` | `WCRedEnvelopesControlMgr` | 检查能否发红包 |

### 4.13 小程序系统

| 方法 | 类 | 用途 |
|------|-----|------|
| `openApp:taskExtInfo:handlerWrapper:` | `WAAppContactPreLoader` | 打开小程序 |
| `openAppWithQRFullUrl:fromScene:...` | `WAAppContactPreLoader` | 扫码打开小程序 |
| `injectJavaScript` | `WAJSCoreService` | 注入 JS 代码 |
| `evaluateJavascript:withSourceURL:` | `WAJSCoreService` | 执行 JS |
| `jSCore_invokeHandler:param:callbackID:contextID:` | `WAJSCoreService` | JS→Native 调用 |
| `jSCore_publishHandler:param:webViewIDs:` | `WAJSCoreService` | Native→JS 推送 |
| `startAppBrand:packageConfig:extraInfo:` | `WAJSCoreService` | 启动小程序运行时 |
| `webviewDidReceiveScriptMessage:handler:rawMessage:` | `WAWebViewController` | 接收 JS 消息 |

**常用 JSAPI Handler**（392 个中的关键项）:

| Handler | 用途 |
|---------|------|
| `WAJSEventHandler_requestPayment` | 小程序内支付 |
| `WAJSEventHandler_login` | 小程序登录 |
| `WAJSEventHandler_getLocation` | 获取 GPS 位置 |
| `WAJSEventHandler_scanCode` | 扫码 |
| `WAJSEventHandler_chooseImage` / `chooseMedia` | 选择图片/媒体 |
| `WAJSEventHandler_navigateToMiniProgram` | 跳转其他小程序 |
| `WAJSEventHandler_shareAppMessageDirectly` | 直接分享 |
| `WAJSEventHandler_createRequestTask` | HTTP 请求 |
| `WAJSEventHandler_createSocketTask` | WebSocket |
| `WAJSEventHandler_startSoterAuthentication` | 生物认证 |

### 4.14 数据库系统 (CMMDB)

| 方法 | 类 | 用途 |
|------|-----|------|
| `InitMMDB:UsrName:NewUser:` | `CMMDB` | 初始化消息数据库 |
| `CreateMessageTable:` | `CMMDB` | 创建消息表 |
| `InsertMessage:withChatName:onProperty:` | `CMMDB(Message)` | 插入消息 |
| `GetMessagesByChatName:onProperty:where:order:limit:hasError:` | `CMMDB(Message)` | 按会话查询消息 |
| `DeleteMessageByChatName:localId:` | `CMMDB(Message)` | 删除消息 |
| `UpdateMessageStatus:byChatName:localId:` | `CMMDB(Message)` | 更新消息状态 |
| `GetContactByUserName:property:` | `CMMDB(Contact)` | 查询联系人 |
| `InsertHelloMessage:withChatName:onProperty:` | `CMMDB(HelloMessage)` | 插入好友请求 |
| `InsertBackupMessages:withChatName:onProperty:` | `CMMDB(Message)` | 批量插入备份消息 |

### 4.15 CDN / 网络层

| 方法 | 类 | 用途 |
|------|-----|------|
| `StartDownloadVideo:AutoDownload:Silent:behavior:` | `CdnComMgr` | CDN 下载视频 |
| `StartDownloadSnsImage:` | `CdnComMgr` | 下载朋友圈图片 |
| `StartDownloadFinderImage:retCode:` | `CdnComMgr` | 下载视频号图片 |
| `StartUploadImage:enableHitCheck:disableHevc:...` | `CdnComMgr` | CDN 上传图片 |
| `StartUploadEmoji:` | `CdnComMgr` | 上传表情 |
| `StartUploadFinderVideoWithTaskInfo:...` | `CdnComMgr` | 上传视频号视频 |
| `StartHttpVideoStreamingDownload:httpUrl:fileType:...` | `CdnComMgr` | HTTP 视频流下载 |
| `calcFileMd5WithFilePath:` | `CdnComMgr` | 计算文件 MD5 |

### 4.16 表情/Emoji 系统

| 方法 | 类 | 用途 |
|------|-----|------|
| `onGetEmojiList:forResult:reqType:` | `EmoticonListUpdateLogic` | 表情列表更新 |
| `startRequestWithStartPos:buffer:` | `EmojiUploadCgi` | 上传自定义表情 |
| `requestAllEmojiInfoList` | `EmoticonDownloadMd5ListCgi` | 请求全部表情 MD5 列表 |
| `addBackupEmoticonOkWithAddEmoticonWrap:validEmojiInfoObj:` | `EmoticonBackupOperateMgr` | 表情备份 |
| `getAllLocalEmojiOcrResult` | `EmoticonInputRecommendMgr` | 本地表情 OCR |
| `getFramesForAnimateEmojiNode:` | `AnimateEmojiCacheMgr` | 获取动画表情帧 |
| `getRecentUseKeyArray` | `ExpressionMgr` | 最近使用表情 |

### 4.17 视频号/Finder

| 方法 | 类 | 用途 |
|------|-----|------|
| `clickLikeFeedActionWithScene:reportScene:isPrivateLike:` | `WCFinderFeedContentVM` | 点赞 |
| `shareMessageWrapWithLiveShareSceneIfLive:` | `WCFinderFeedContentVM` | 分享视频号内容 |
| `shareToMomentInMainWindow` | `WCFinderFeedContentVM` | 分享到朋友圈 |
| `start` | `WCFinderBaseCgi` | 发起视频号 CGI 请求 |
| `didGetResponse:` | `WCFinderLikeCGI` / `WCFinderCommentCGI` / `WCFinderFollowCGI` | 各操作响应 |
| `postChangeFollowStateRequest` | `WCFinderFollowBtnViewModel` | 关注/取消关注 |
| `addDownloadTask:` | `WCFinderAccessoryDownloadManager` | 下载视频号附件 |

### 4.18 群通话 / VoIP

| 方法 | 类 | 用途 |
|------|-----|------|
| `doCreateMultiTalkWithContacts:withChatroomUsername:` | `MultiTalkMgr` | 创建群通话 |
| `acceptWithRoomID:` | `MultiTalkMgr` | 接听 |
| `MultiTalkReject:` | `MultiTalkMgr` | 拒绝 |
| `_hangupMultiTalkByCallEnd` | `MultiTalkMgr` | 挂断 |
| `isMultiTalkActive` | `MultiTalkMgr` | 是否正在通话 |
| `canShareScreen` | `MultiTalkMgr` | 是否支持屏幕共享 |
| `broadcastCmdMsgData:toSpecifyMemberIDs:` | `MultiTalkMgr` | 广播指令消息 |
| `onHangupButtonClick` / `onMicrophoneButtonClick` / `onVideoButtonClick` | `MultiTalkBottomOperatePanel` | 操作面板按钮 |

---

## 5. CMessageWrap 消息模型

### 5.1 核心属性

```objc
@property NSString *m_nsFromUsr;        // 发送者（收到群消息时=群ID）
@property NSString *m_nsToUsr;          // 接收者（自己发群消息时=群ID）
@property NSString *m_nsRealChatUsr;    // 群聊中实际发送者 wxid
@property NSString *m_nsContent;        // 消息内容
@property NSString *m_nsFromUsrName;    // 发送者昵称
@property NSString *m_nsContentUrl;     // 内容 URL
@property unsigned int m_uiMessageType; // 消息类型
@property unsigned int m_uiStatus;      // 消息状态
@property unsigned int m_uiMesLocalID;  // 本地消息 ID（用于去重）
@property long long m_n64MesSvrID;      // 服务器消息 ID（用于去重）
@property unsigned int m_uiImgStatus;   // 图片下载状态（0=未下载, 2=已完成）
```

### 5.2 扩展属性

```objc
// 消息元数据
@property NSString *m_nsMsgSource;           // 消息来源 XML（含 @列表、静默标志等）
@property NSString *m_nsAtUserList;          // 逗号分隔的 @-wxid 列表
@property unsigned int m_uiCreateTime;       // 消息创建时间戳
@property unsigned int m_uiAppMsgInnerType;  // AppMsg 子类型（type=49 时的内部类型）

// 媒体相关
@property NSString *m_nsThumbImgPath;        // 缩略图本地路径
@property NSString *m_nsImageAesKey;         // 图片 AES 解密密钥
@property unsigned int m_uiVoiceLen;         // 语音时长(ms)
@property unsigned int m_uiImageLength;      // 图片数据长度

// AppMsg 字段
@property NSString *m_nsTitle;               // 消息标题（富媒体消息）
@property NSString *m_nsDesc;                // 消息描述
@property NSString *m_nsUrl;                 // 消息 URL
@property NSString *m_nsAppId;               // 来源 App ID

// 引用回复
@property long long m_i64ReferMsgSvrId;      // 被引用消息的服务器 ID

// 布尔标志
@property BOOL m_bIsSenderFromSelf;          // 是否自己发送
@property BOOL m_bHD;                        // 高清媒体标志
@property BOOL m_bContainsEmoji;             // 包含表情

// 嵌套对象
@property WCPayInfoItem *m_oWCPayInfoItem;                 // 支付信息
@property WCFinderFeedMediaWrap *m_oFinderMediaItem;       // 视频号媒体
@property WCFinderMessageShareNameCard *m_finderShareNameCard; // 视频号名片
```

### 5.3 收发消息的字段差异

| 字段 | 收到的群消息 | 自己发的群消息 |
|------|-------------|---------------|
| `m_nsFromUsr` | 群聊 ID (`xxx@chatroom`) | 自己的 wxid |
| `m_nsToUsr` | 自己的 wxid | 群聊 ID (`xxx@chatroom`) |
| `m_nsRealChatUsr` | 实际发送者 wxid | 空 |

### 5.4 消息类型常量 (m_uiMessageType)

| 值 | 类型 | 说明 |
|----|------|------|
| 1 | 文本消息 | 纯文本 |
| 3 | 图片消息 | WXAM 格式，需解码 |
| 34 | 语音消息 | SILK 格式 |
| 42 | 名片消息 | |
| 43 | 视频消息 | XML 含 `<videomsg>` |
| 47 | 表情/贴图 | XML 含 `<emoji>` |
| 48 | 位置消息 | |
| 49 | 富媒体消息 | 链接/小程序/文件/红包/转账/引用回复 |
| 10000 | 系统消息 | 撤回提示/进退群等 |
| 10002 | 系统通知 | 群通知等 |

### 5.5 type=49 子类型 (m_uiAppMsgInnerType)

| 子类型 | 含义 |
|--------|------|
| 1 | 文章链接 |
| 5 | URL 链接分享 |
| 6 | 文件 |
| 7 | 公众号文章 |
| 8 | GIF 表情（商店） |
| 33/36 | 小程序分享 |
| 40 | 合并转发聊天记录 |
| 51 | 视频号分享 |
| 57 | 引用回复 |
| 63 | 视频号直播 |
| 74 | 文件消息（新版） |
| 87 | 群公告 |
| 88 | 群待办 |
| 2000 | 转账 |
| 2001 | 微信红包 |

### 5.6 关键方法

```objc
+ (CMessageWrap *)FormMessageWrapFromAddMsg:(id)addMsg;
- (void)ChangeForChatRoom;       // 群消息必须调用才能正确获取群信息
- (void)ChangeForDisplay;
- (BOOL)IsAtMe;
- (void)parseWCPayInfoItemIfNeed;    // 懒加载解析支付信息
- (void)AddOrModifyTagInMsgSource:value:removeOnEmpty:; // 修改 MsgSource XML 标签
- (NSString *)getThumbImagePath;
- (NSString *)GetAppAttachmentPath;
```

### 5.7 图片状态重置技巧

```objc
// 微信下载完成后 m_uiImgStatus=2，再调用下载 API 会被忽略
// 必须先重置为 0 才能重新触发下载
SEL setImgStatusSel = NSSelectorFromString(@"setM_uiImgStatus:");
((void (*)(id, SEL, unsigned int))objc_msgSend)(msgWrap, setImgStatusSel, 0);
```

---

## 6. CContact 联系人模型

### 6.1 核心属性

```objc
// 身份
@property NSString *m_nsUsrName;         // wxid（唯一标识）
@property NSString *m_nsEncodeUserName;  // 加密用户名(v3)
@property NSString *m_nsNickName;        // 昵称
@property NSString *m_nsRemark;          // 备注名
@property NSString *alias;               // 微信号
@property unsigned int m_uiType;         // 联系人类型
@property unsigned int m_uiConType;      // 联系类型

// 个人资料
@property unsigned int m_uiSex;          // 性别：0=未知, 1=男, 2=女
@property NSString *m_nsCountry;         // 国家
@property NSString *m_nsProvince;        // 省份
@property NSString *m_nsCity;            // 城市
@property NSString *m_nsSignature;       // 个性签名

// 头像
@property NSString *m_nsHeadImgUrl;      // 头像 URL（132x132）
@property NSString *m_nsHeadHDImgUrl;    // 高清头像 URL（640x640）
@property NSString *m_nsHeadHDMd5;       // 高清头像 MD5

// 搜索
@property NSString *m_nsFullPY;          // 全拼音
@property NSString *m_nsRemarkPYFull;    // 备注全拼音
@property NSString *m_nsLabelIDList;     // 标签 ID 列表（逗号分隔）

// 验证信息
@property NSString *m_nsPhoneNumber;     // 绑定手机号
@property NSString *m_nsVerifyContent;   // 好友请求验证消息
@property unsigned int m_uiVerifyFlag;   // 验证类型标志
@property unsigned int m_uiFriendScene;  // 添加好友场景

// 群聊
@property ChatRoomData *m_ChatRoomData;  // 群聊数据对象
@property BOOL m_bIgnoreChatRoom;        // 忽略群聊
```

### 6.2 获取联系人信息

```objc
CContactMgr *contactMgr = [[NSClassFromString(@"MMServiceCenter") defaultCenter]
                            getService:NSClassFromString(@"CContactMgr")];
CContact *contact = [contactMgr getContactByName:wxid];

// 读取性别
unsigned int sex = [[contact valueForKey:@"m_uiSex"] unsignedIntValue];
// 0 = 未设置/未知, 1 = 男, 2 = 女

// 读取地区
NSString *country  = [contact valueForKey:@"m_nsCountry"];
NSString *province = [contact valueForKey:@"m_nsProvince"];
NSString *city     = [contact valueForKey:@"m_nsCity"];

// 读取个性签名
NSString *signature = [contact valueForKey:@"m_nsSignature"];
```

### 6.3 从服务器拉取完整资料

本地缓存的 CContact 可能只有基础字段，性别/地区等字段为空。需要主动请求：

```objc
CContactMgr *contactMgr = [[NSClassFromString(@"MMServiceCenter") defaultCenter]
                            getService:NSClassFromString(@"CContactMgr")];

[contactMgr getContactsFromServer:@[wxid]
                      chatContact:nil
                        withScene:0
                       withTicket:nil
                          usrData:nil];
```

> **注意**: 异步请求，需等回调后再读取。频繁请求可能触发风控，建议做缓存和限流。

### 6.4 群成员遍历示例

```objc
WCGroupMgr *groupMgr = [[NSClassFromString(@"MMServiceCenter") defaultCenter]
                         getService:NSClassFromString(@"WCGroupMgr")];
CContactMgr *contactMgr = [[NSClassFromString(@"MMServiceCenter") defaultCenter]
                            getService:NSClassFromString(@"CContactMgr")];

NSArray *memberList = [groupMgr getMemberListFromChatRoom:chatRoomId];

for (NSString *memberWxid in memberList) {
    CContact *member = [contactMgr getContactByName:memberWxid];
    unsigned int sex = [[member valueForKey:@"m_uiSex"] unsignedIntValue];
    NSString *nick = [member valueForKey:@"m_nsNickName"];
    NSString *sexStr = (sex == 1) ? @"男" : (sex == 2) ? @"女" : @"未知";
    NSLog(@"%@ (%@): %@", nick, memberWxid, sexStr);
}
```

> **提示**: 群成员如果不是好友，本地缓存可能缺少性别等详细信息。可先调用 `getContactsFromServer:` 批量拉取后再读取。

---

## 7. ChatRoomData 群聊数据模型

`ChatRoomData` 挂载在 `CContact.m_ChatRoomData` 上，存储群聊元数据。

### 7.1 核心属性

```objc
@property NSString *m_nsChatRoomUserName;       // 群 wxid（xxx@chatroom）
@property NSString *m_nsChatRoomMemList;        // 分号分隔的成员 wxid 列表
@property NSString *m_nsChatRoomAdminList;      // 分号分隔的管理员 wxid 列表
@property NSString *m_nsChatRoomDesc;           // 群公告
@property NSString *m_nsChatRoomDescModer;      // 公告最后修改者
@property unsigned int m_uiChatRoomMaxCount;    // 最大成员数（默认500）
@property unsigned int m_uiChatRoomVersion;     // 群版本号
@property unsigned int m_uiChatRoomStatus;      // 群状态
@property unsigned int m_uiChatRoomAccessType;  // 进群方式限制
@property unsigned int m_uiChatRoomQRCodeAccessType; // 二维码进群限制
@property unsigned int m_uiChatRoomDescTime;    // 公告更新时间戳
@property NSString *m_nsAssociateChatRoomUserName;   // 关联群
@property NSString *m_nsOpenIMChatRoomUserName;      // 企业微信关联群
```

### 7.2 关键方法

```objc
-[ChatRoomData parseData:]                  // 解析群数据（从 protobuf/XML）
-[ChatRoomData getDataForUserName:key:]     // 获取群内指定用户数据
-[ChatRoomData updateChatRoomData:]         // 更新群数据
-[ChatRoomData getDataXml]                  // 获取原始 XML 数据
```

---

## 8. WCPayInfoItem 支付模型

`WCPayInfoItem` 嵌套在 `CMessageWrap.m_oWCPayInfoItem`，从 type=49 消息的 XML 中懒加载解析。

### 8.1 核心属性

```objc
@property NSString *m_nsTransferID;       // 转账交易 ID
@property NSString *m_nsTransferDesc;     // 转账描述
@property NSString *m_nsFeeDesc;          // 金额描述
@property NSString *m_nativeUrl;          // 点击跳转的 NativeUrl
@property NSString *m_payMemo;            // 转账备注
@property NSString *m_senderTitle;        // 发送方标题
@property NSString *m_receiverTitle;      // 接收方标题

@property unsigned int m_uiPaySubType;    // 支付子类型: 1=转账, 3=红包, 4=AA
@property unsigned int m_total_fee;       // 金额（分）
@property unsigned int m_uiInvalidTime;   // 过期时间戳
@property unsigned int m_uiBeginTransferTime; // 发起时间戳
@property unsigned int m_redEnvelopeType;     // 红包类型

@property BOOL m_bIsSenderFromSelf;       // 自己是发送方
```

### 8.2 解析方法

```objc
// 在 CMessageWrap 上调用，懒加载解析
[msgWrap parseWCPayInfoItemIfNeed];
WCPayInfoItem *payInfo = [msgWrap valueForKey:@"m_oWCPayInfoItem"];
```

---

## 9. MMSessionInfo 会话模型

### 9.1 核心属性

```objc
@property CContact *m_contact;              // 会话对应的联系人
@property CMessageWrap *m_msgWrap;          // 最后一条消息

@property NSString *m_nsUserName;           // 会话目标 wxid
@property NSString *m_nsDisplayName;        // 显示名称
@property NSString *m_nsDraft;              // 未发送的草稿
@property unsigned int m_uiDraftTime;       // 草稿时间
@property BOOL m_isSessionTop;              // 是否置顶
@property BOOL m_ignoreSession;             // 是否免打扰
```

### 9.2 常用操作

```objc
MMNewSessionMgr *sessionMgr = [[NSClassFromString(@"MMServiceCenter") defaultCenter]
                                getService:NSClassFromString(@"MMNewSessionMgr")];

// 获取会话
id session = [sessionMgr GetSessionByUserName:wxid];

// 置顶 / 取消置顶
[sessionMgr TopSessionByName:wxid];
[sessionMgr UntopSessionByName:wxid needSync:YES];

// 隐藏 / 显示
[sessionMgr hideSession:session];
[sessionMgr showSession:session];

// 清除各类计数
[sessionMgr clearAtMeCount:wxid];
[sessionMgr clearTransferCount:wxid];
[sessionMgr clearExclusiveHbMessageCount:wxid];
```

---

## 10. XML 消息结构参考

### 10.1 基础 AppMsg 结构 (type=49)

```xml
<msg>
    <appmsg appid="%@" sdkver="%u">
        <title>%@</title>
        <des>%@</des>
        <type>%u</type>
        <url>%@</url>
        <appattach>
            <attachid>%@</attachid>
            <aeskey>%@</aeskey>
        </appattach>
    </appmsg>
    <fromusername>%@</fromusername>
    <appinfo>
        <version>%u</version>
        <appname>%@</appname>
    </appinfo>
</msg>
```

### 10.2 转账/红包 XML (`<wcpayinfo>`)

```xml
<appmsg>
    <type>2000</type>
    <wcpayinfo>
        <paysubtype>1</paysubtype>         <!-- 1=转账, 3=红包, 4=AA -->
        <feedesc>金额描述</feedesc>
        <transcationid>%@</transcationid>
        <transferid>%@</transferid>
        <invalidtime>%u</invalidtime>
        <nativeurl>%@</nativeurl>
        <total_fee>%u</total_fee>          <!-- 金额（分） -->
        <pay_memo>%@</pay_memo>
        <sendertitle>%@</sendertitle>
        <receivertitle>%@</receivertitle>
    </wcpayinfo>
</appmsg>
```

### 10.3 小程序分享 XML (`<weappinfo>`)

```xml
<appmsg>
    <type>33</type>
    <weappinfo>
        <username>gh_xxxxx</username>      <!-- 小程序原始 ID -->
        <appid>wx123456</appid>            <!-- 小程序 AppID -->
        <pagepath>pages/index</pagepath>
        <weappiconurl>%@</weappiconurl>
        <shareId>%@</shareId>
    </weappinfo>
</appmsg>
```

### 10.4 引用回复 XML (`<refermsg>`)

```xml
<appmsg>
    <title>回复内容</title>
    <type>57</type>
    <refermsg>
        <type>%u</type>                    <!-- 原消息类型 -->
        <svrid>%lld</svrid>                <!-- 原消息服务器 ID -->
        <fromusr>%@</fromusr>              <!-- 原发送者 wxid -->
        <chatusr>%@</chatusr>              <!-- 会话 wxid -->
        <displayname>%@</displayname>      <!-- 原发送者显示名 -->
        <content>%@</content>              <!-- 原消息内容 -->
    </refermsg>
</appmsg>
```

提取正则（PKC 方案）: `<fromusr>(.*?)</fromusr>.*?<displayname>(.*?)</displayname>.*?<content>(.*?)</content>`

### 10.5 图片消息 XML (type=3)

```xml
<msg>
    <img hdlength="%u" length="%u" aeskey="%@" md5="%@"
         filekey="%@" imgsourceurl="%@" />
</msg>
```

### 10.6 视频消息 XML (type=43)

```xml
<msg>
    <videomsg playlength="%u" length="%u" aeskey="%@"
              cdnvideourl="%@" cdnthumburl="%@"
              cdnthumbwidth="%u" cdnthumbheight="%u"
              cdnthumbaeskey="%@" rawlength="%llu"
              cdnrawvideourl="%@" cdnrawvideoaeskey="%@" />
</msg>
```

### 10.7 语音消息 XML (type=34)

```xml
<msg>
    <voicemsg voicelength="%u" voiceformat="%u" forwardflag="%u" />
</msg>
```

### 10.8 表情消息 XML (type=47)

```xml
<msg>
    <emoji fromusername="%@" tousername="%@" type="%u"
           md5="%@" len="19922" cdnurl="%@" />
    <gameext type="%u" content="%u" />
</msg>
```

---

## 11. 功能实现参考（各插件方案汇总）

### 11.1 防撤回

**最简方案**（WCEhance）：Hook `onRevokeMsg:` 不调用原始方法。

**完整方案**（MikotoHelper / PKC / WCPulse）：

1. Hook `onRevokeMsg:` 拦截撤回
2. 保存原始消息内容
3. 替换撤回提示文本（可自定义格式、颜色、日期格式）
4. 支持区分"自己撤回"和"别人撤回"
5. 支持批量撤回拦截（`disableBatchRevokeMsg`）
6. 可选：撤回后自动回复（PKC: `revokeReplyEnable`）

**WCPulse 特色**: 生成可点击链接 `WCPulseRevokeFrom://LocalID=%d,%@` 跳转查看原始消息。

**WCEhance 特色**: 自定义撤回文本 `enableCustomMyRevokeText` / `enableCustomOtherRevokeText`。

### 11.2 自动抢红包

**三重降级策略**（已验证可用）：

```
Plan A: WCRedEnvelopesReceiveControlLogic.OpenRedEnvelopesRequest:
Plan B: WCBizUtil.openNativeUrl:
Plan C: WCSchemeLinker.handleScheme:
```

**检测红包**: msg_type=49, XML 含 `<type>2001</type>`
**延迟抢**: 所有插件都支持 1-5 秒延迟，模拟人工操作

### 11.3 广告屏蔽

**FuckWeChatAdBlocker 方案**：

Hook 微信广告基础类：
- `WCAdvertiseDataHelper` / `WCAdvertiseInfo` / `WCAdvertisePushService`
- `WCAdvertiseStatMgr` / `WCAdvertiseStorage`
- `WCADBodyWrap` / `WCADPageWrap` / `WCAdXmlParser`
- 拦截 `canShowSplashADWindow`（开屏广告）
- 拦截 `FinderObjectAdInfo`（视频号广告）
- 拦截 `BrandAdDataItem`（品牌广告）
- 朋友圈广告：Hook `WCTimelineDataProvider(AD)` 的 `tryToPullSnsAd:` / `delAdWithSnsId:SnsId:`

### 11.4 步数修改

**PKC 方案**：Hook `WCDeviceStepObject`，修改步数值：
- `pkcChangeStepsEnable` — 开关
- `pkcStepNum1` / `pkcStepNum2` — 步数范围
- `pkcStepTime` — 修改时间

**MiYou 方案**: `_mIsFakeStep` + `_mDayStepValue`

**底层原理**: Hook `WCDeviceBrandMgr.onGotDeviceStepObject:` 修改 HKStepCount / M7StepCount 值，再通过 `WCDeviceNetworkLogicMgr.sendUploadDeviceStepReq:` 上报。

### 11.5 虚拟定位

**MiYou 方案**：

```objc
@property BOOL mIsFakeLocation;
@property double mFakeLocationX;       // 纬度
@property double mFakeLocationY;       // 经度
@property NSString *mFakeLocationName; // 位置名称
```

Hook `CLLocationManager` 返回自定义坐标，集成 `MMPickLocationViewController` 地图选点。
影响范围：附近的人、聊天共享位置、朋友圈位置标签。

### 11.6 AI 集成

| 插件 | AI 服务 | 端点 |
|------|---------|------|
| MikotoHelper | DeepSeek | 自定义端点/Key/角色/模式 |
| PKCWeChatTools | DeepSeek + OpenAI + SiliconFlow + Volcengine | 多模型切换 |
| WCPulse | OpenAI + 阿里灵积 + 自建 | `api.openai.com`, `dashscope.aliyuncs.com` |
| MiYou | ChatGPT | `_mChatGPTAPIKey` |
| HBWechatHelper | NewBing | — |

### 11.7 语音/TTS

**PKC 方案**（TTS 后端最丰富）：
- 讯飞语音合成 (`peiyin.xunfei.cn`)
- Fish Audio (`api.fish.audio/v1/tts`)
- ACGN TTS (`acgn.ttson.cn`)
- FineShare 语音克隆 (`dlaudio.fineshare.net`)

**HBWechatHelper / MiYou**：内嵌完整 SILK 编解码器 + LAME MP3 编码器。

### 11.8 Finder 视频保存

**WCPulse 方案**：

```objc
// Hook WCFinderTimelineTabViewController / WCFinderShareFeedCellView
wcpulse_forwardVideo              // 转发视频
wcpulse_saveVideoToAlbum          // 保存到相册
wcpulse_showFinderVideoOptionsWithURL:  // 显示选项菜单
// 配置: finderVideoAutoSaveToAlbum — 自动保存
```

### 11.9 群管理增强

**各插件共有功能汇总**：
- 群成员退出监控（WCPulse: `WCPulseGroupMemberLeft://wxid=%@`）
- 群消息转发/广播
- 批量退群 / 批量改群名
- 群 VIP 成员系统（PKC: 有效期/自动续期）
- 群内容过滤（PKC: 按消息类型——图片/链接/二维码/语音/视频/表情/文件/小程序）
- 群欢迎消息（MiYou: `_mIsWelcomeToGroup` + `_mWelcomeGroupList`）
- 群成员管理（踢人/拉人/黑名单/管理员标识）
- 显示群内真实昵称（PKC: `_pkcDisplayRNameEnable`）

### 11.10 消息推送转发

**PKC 方案**：通过 Bark API 推送到其他设备：
```
pushMsgEnable   — 开关
pushApi         — Bark/webhook API 端点（如 https://api.day.app/xxx/）
pushSetting     — 推送过滤设置
```

### 11.11 暗色模式/主题系统

**WCPulse — ThemeBox 引擎（最完整）**：
- `ThemeBoxMgr` 单例管理主题状态
- 预设调色板 + 自定义十六进制颜色
- 每群独立颜色配置
- 通过 NSNotification 广播颜色变更：`WCPulseGroupBackgroundColorSettingChanged` / `WCPulseGroupFontColorSettingChanged`
- Hook `UIColor` 的 `+colorWithDynamicProvider:` 响应 trait collection 切换

**WCEhance — 菜单/水印美化**：
- 菜单模糊/边框/阴影/圆角（`menuBlurEffectEnable` / `menuBorderEnable` / `menuShadowEnable`）
- 水印系统（`enableAppInfoWatermark` / `customWatermarkText` / `watermarkColor`）
- SVG 图标跟随主题色（`svgColorFollowEnable`）

**PKC — Tab 标签美化**：
- 每个 Tab 独立配置：文本/颜色/大小/位置/透明度/圆角
- 深色模式背景图：`diyPKCBgDark.png` / `diyWxBgDark.png` 等

### 11.12 版本伪装

**WCEhance 方案**：

```objc
// 预设版本目标
+[WCEhanceConfig fakeVersionEnable8_0_33]
+[WCEhanceConfig fakeVersionEnable8_0_49]
+[WCEhanceConfig fakeVersionEnable8_0_54]
+[WCEhanceConfig fakeVersionEnableLatest]

// 动态获取最新版本号
+[WCEhanceHelper fetchFakeVersionWithCompletion:]
```

Hook `CFBundleVersion` / `CFBundleShortVersionString`。`WCVersionFakeController` 提供设置 UI。

### 11.13 自动下载媒体

**MiYou**: `mIsAutoDownloadImage` / `mIsAutoDownloadVideo` / `mIsAutoDownloadFiles`，支持每群独立配置 `mAutoDownloadRoomList`。

**PKC**: `pkcAutoDownloadImgEnable` / `pkcAutoDownloadVideoEnable`，额外支持 `SaveAlbum` 参数直接保存到相册，`Silent` 参数静默下载，后台队列 `com.pkc.download`。

### 11.14 聊天备份/导出

**WCPulse 方案**：

备份目的地：Documents / 文件传输助手 / Google Drive / OneDrive / 自定义路径
- `WCPulseBackupMgr` 管理备份生命周期
- `WCPulseBackup_%@.dat` 格式存储
- 支持定时备份（`backupCycleMinutes`）、启动时备份（`enableBackupOnAppLaunch`）、静默备份

### 11.15 定时发送

**MikotoHelper 方案**：

- `PJTimerTaskModel` — 任务数据模型
- `PJTimerTaskListVC` / `PJTimerTaskGroupListVC` — 管理界面
- `NSTimer` (bgTaskTimer) 定期检查 `checkTimerTask` 触发到期任务
- 支持：文本/图片/文件/引用回复/转发消息
- 批量群发：`pjMasssendapp`

### 11.16 自定义字体

**WCPulse 方案**：

- Hook `UIFont` 系统字体方法返回自定义字体
- 自定义字体文件（TTF/OTF）通过 `CTFontManagerRegisterFontsForURL` 注册
- `WCPulseFontMapping.json` 维护文件名↔字体名映射
- `WCPulseFontSettingVC` 提供选择界面
- 支持每群独立字号

### 11.17 隐私功能

**隐藏输入状态**：
- WCEhance: `enableCustomTypingStatus` / `enableRandomTypingText` 自定义输入中文本
- MiYou: `mIsUnSendTyping` Hook `trySendTyping:` 阻止发送

**免打扰**：
- MiYou: `mDonotdisturbList` 每联系人配置 + `mDonotdisturbWorkingTime` 工作时段
- HBWechatHelper: `enableAutoMuteGroup` 自动静音新群

**隐藏静音图标**: WCEhance `hideMuteIcon`

### 11.18 键盘增强

**HBWechatHelper 方案**：

`KeyBoardButtonManager` 管理可配置工具栏：
- 快捷操作可拖拽排序（`enabledShortcuts` / `disabledShortcuts`）
- 自定义图标（`setCustomIcon:forShortcut:`）
- 触觉反馈（`keyboardEnhanceVibration`）
- 与 MiYou 工具栏兼容（`fixMiYouToolBar:`）

### 11.19 斗图/表情包管理

**DouTu.dylib 方案**：

多后端搜索聚合：
- 百度图片搜索（`DTBaiduAPI`）
- 搜狗表情搜索（`DTSogouAPI`）
- ChunBao 表情库（`DTChunBaoAPI`）
- 自定义 API（`DTCustomAPIUrl` + `DTCustomAPIs`）

集成到聊天输入栏的自定义按钮，`DouTuExpressionView` 嵌入聊天界面。
支持收藏管理（`DouTuFavViewController`）和表情制作（`DouTuMakerViewController`）。

### 11.20 自动回复

**MiYou — 完整自动回复引擎**：
- `mIsAutoReplyMessage` — 全局开关
- `mAutoReplyMessage` — 默认回复内容
- `mIsAutoReplyOnlineTime` — 仅在线时段回复
- `mIsKeywordReplyMessage` — 关键词匹配
- `mKeywordReplyMessage` — 关键词→回复映射 (NSDictionary)
- `AutoReplyMessage:MsgWrap:` — 核心处理入口

**MikotoHelper — 关键词系统 + 群管理**：
- `PJKeyWordModel` / `PJKeyWordListViewController` — 关键词管理
- `keywordWithMessage:WithUsrName:` — 消息匹配
- 支持 @-关键词、跟读关键词、管理员关键词命令

### 11.21 好友验证自动通过

**MikotoHelper — 高级方案**：
- 支持按群来源自动通过（`friendAddPassGroupAction`）
- 支持按关键词匹配（`friendAddPassKeywordAction`）
- 支持按标签过滤（`friendAddPassTagAction`）
- 通过后自动回复（`friendAddPassTextAction`）
- 统计功能（`addFriendCountAction`）

**MiYou — 简单方案**：
- `mIsAutoVerifyFriend` — 开关
- `mAutoVerifyKeyword` — 验证消息关键词
- `mAutoVerifyContent` — 通过后自动回复内容

---

## 12. NSUserDefaults 配置键速查

各插件的命名前缀约定：

| 插件 | 前缀 | 示例 |
|------|------|------|
| MikotoHelper | `*Enable`, `pj*` | `revokeEnable`, `pjRedPacketEnable` |
| PKCWeChatTools | `_pkc*`, `create*Enable` | `_pkcExitGroupEnable`, `createDyJxEnable` |
| HBWechatHelper | `msg*`, `wc*Enable` | `msgChatEnable`, `wcAutoRedPrivateEnable` |
| WCPulse | `WCPulse*`, `handle*Setting` | `WCPulseBackupKey`, `enableGlobalRevoke` |
| WCEhance | `*Enable`, `WCEhance*` | `roundAvatarEnable`, `menuBlurEffectEnable` |
| MiYou | `_mIs*`, `_m*` | `_mIsAutoReplyMessage`, `_mIsFakeLocation` |
| DouTu | `DT*` | `DTEnabled`, `DTCustomAPIUrl` |

### 12.1 MikotoHelper 常用键

| 键 | 类型 | 功能 |
|----|------|------|
| `revokeEnable` | BOOL | 防撤回 |
| `chatingEnable` | BOOL | 聊天增强主开关 |
| `pjRedPacketEnable` | BOOL | 红包自动化 |
| `pjKeywordReplyEnable` | BOOL | 关键词自动回复 |
| `timeLineForwardEnable` | BOOL | 朋友圈转发 |
| `dkChatBgEnable` | BOOL | 深色模式聊天背景 |

### 12.2 MiYou 常用键

| 键 | 类型 | 功能 |
|----|------|------|
| `_mIsRevokeMsg` | BOOL | 防撤回 |
| `_mIsAutoReplyMessage` | BOOL | 自动回复 |
| `_mIsAutoDownloadImage` | BOOL | 自动下载图片 |
| `_mIsFakeLocation` | BOOL | 虚拟定位 |
| `_mIsUnSendTyping` | BOOL | 隐藏输入状态 |
| `_mIsChatGPTEnabled` | BOOL | ChatGPT |
| `_mIsAutoVerifyFriend` | BOOL | 自动通过好友 |

### 12.3 PKC 常用键

| 键 | 类型 | 功能 |
|----|------|------|
| `_revokeEnable` | BOOL | 防撤回 |
| `_pushMsgEnable` | BOOL | 消息推送 |
| `_pkcChangeStepsEnable` | BOOL | 修改步数 |
| `_pkcDisplayRNameEnable` | BOOL | 显示真实名 |
| `pkcAutoDownloadImgEnable` | BOOL | 自动下载图片 |
| `_dpAIZzHhEnable` | BOOL | AI 助手 |

---

## 13. 设置页 UI 构建模式

### 13.1 方式 A: WCTableViewManager（推荐，PKC/WCPulse/WCEhance/MiYou 使用）

```objc
@property (nonatomic, strong) WCTableViewManager *tableViewMgr;

// 创建分组
WCTableViewSectionManager *section = [tableViewMgr addSection:@"分组标题"];

// 开关 Cell
WCTableViewCellManager *cell = [WCTableViewCellManager switchCellForSel:@selector(handleSwitch:)
                                                                 target:self
                                                                  title:@"功能名称"
                                                                     on:isEnabled];

// 普通 Cell（带右侧值和箭头）
cell = [WCTableViewCellManager normalCellForSel:@selector(handleTap)
                                         target:self
                                          title:@"设置项"
                                     rightValue:@"当前值"
                                  accessoryType:UITableViewCellAccessoryDisclosureIndicator];

[section addCell:cell];
```

### 13.2 方式 B: MMTableViewInfo（MikotoHelper/HBWechatHelper 使用）

```objc
@property (nonatomic, strong) MMTableViewInfo *m_tableViewInfo;

// 直接添加 section 和 cell
[self addSection:sectionIndex];
[self addCell:cellData];
```

### 13.3 各插件设置 ViewController

| 插件 | 主设置 VC |
|------|----------|
| MikotoHelper | `_settingVC` / `newSettingVC` |
| PKCWeChatTools | 内嵌主 VC |
| WCPulse | `WCPulseSettingViewController` |
| WCEhance | `WCEhanceViewController` |
| MiYou | `MiYouSettingViewController` |
| HBWechatHelper | `GotoHbHelperSetting` |
| DouTu | `DouTuSettingViewController` |

---

## 14. 常用工具方法

### 14.1 Toast / Alert

```objc
// PKC — Alert 带文本输入
[PKCTools alertControllerWithTitle:@"标题"
                          message:@"描述"
                          content:@"默认值"
                      placeholder:@"占位符"
                             blk:^(NSString *text) { /* 回调 */ }];

// HBWechatHelper — 自定义 Alert
[self ishbalertControllerWithTitle:@"标题"
                          message:@"内容"
                        leftBlock:^{ /* 取消 */ }
                       rightBlock:^{ /* 确认 */ }];

// MiYou — 自定义组件
MiYouHudView   // HUD
MiYouToastView // Toast
MiYouDanMuView // 弹幕
```

### 14.2 图片保存

```objc
// 所有插件统一使用 PHPhotoLibrary
[self saveImageToPhotoAlbum:image];  // PKC
[self saveToPhotoLibrary];           // MikotoHelper
[self promptSaveToPhotoLibrary:image]; // HBWechatHelper
```

### 14.3 剪贴板

```objc
[UIPasteboard generalPasteboard].string = @"复制内容";

// 插件特色方法
[self copyWxid];      // WCEhance — 复制微信 ID
[self copyNickname];  // WCEhance — 复制昵称
[self copyAlias];     // WCEhance — 复制微信号
```

### 14.4 触觉反馈

```objc
// MikotoHelper
[self triggerHapticFeedback:UIImpactFeedbackStyleMedium];

// PKCWeChatTools
[self triggerEnhancedHapticFeedback];
```

### 14.5 NSNotification 通信模式

```objc
// 发布
[[NSNotificationCenter defaultCenter] postNotificationName:@"WCPulseConfigDidChange"
                                                    object:nil];

// 监听
[[NSNotificationCenter defaultCenter] addObserver:self
                                         selector:@selector(handleConfigChanged:)
                                             name:@"WCPulseConfigChangedNotification"
                                           object:nil];
```

### 14.6 数据持久化

| 方式 | 使用的插件 | 适用场景 |
|------|-----------|---------|
| NSUserDefaults | **全部** | 开关/简单配置 |
| Singleton Config | WCPulse/WCEhance/MiYou/DouTu | 复杂配置包装 |
| Plist 文件 | WCPulse | 字体映射/备份 |
| SQLite | PKC/MikotoHelper/DouTu | 步数/聊天记录统计 |
| NSKeyedArchiver | WCPulse | 复杂对象序列化 |
| 文件读写 | 多个 | 媒体/备份数据 |

---

## 15. 微信内部 UI 组件

### 15.1 TableView 体系

| 类 | 用途 |
|-----|------|
| `WCTableViewManager` | 表格管理器 |
| `WCTableViewSectionManager` | 分组管理器 |
| `WCTableViewCellManager` | Cell 管理器 |
| `WCTableViewNormalCellManager` | 普通 Cell |
| `WCListViewController` | 列表 VC |
| `MMTableView` | 微信定制 TableView |
| `MMTableViewCell` | 微信定制 Cell |
| `MMTableViewInfo` | 表格信息 |

### 15.2 其他常用 UI

| 类 | 用途 |
|-----|------|
| `MMLoadingView` | 加载提示 |
| `MMWebViewController` | 内嵌网页 |
| `MMImagePickerController` | 图片选择器 |
| `MMHeadImageView` / `MMHeadImageCacher` | 头像显示/缓存 |
| `MMInputToolView` / `MMGrowTextView` | 输入框 |
| `MMMenuController` / `MMMenuItem` | 弹出菜单 |
| `MMPageSheetAdapter` / `MMPageSheetConfig` | 底部弹出页 |
| `WCActionSheetItem` | 操作选项 |
| `MMUINavigationController` | 导航控制器 |

---

## 16. 开发最佳实践

### 16.1 防崩溃

```objc
// 所有类名用 NSClassFromString 动态查找
Class cls = NSClassFromString(@"CMessageMgr");
if (!cls) return;  // 微信版本不兼容时静默退出

// 所有方法用 respondsToSelector 检查
if ([obj respondsToSelector:NSSelectorFromString(@"someMethod:")]) {
    // 调用
}
```

### 16.2 线程安全

- `AsyncOnAddMsg:MsgWrap:` 在**后台线程**调用，UI 操作必须 dispatch 到主线程
- 微信大量使用 GCD，Hook 时不要阻塞
- 网络请求使用 `dispatch_async(dispatch_get_global_queue(...))`

### 16.3 消息去重

- 同一条消息可能触发多次回调（`AsyncOnPreAddMsg` → `AddMsg` → `AsyncOnAddMsg`）
- 用 `m_uiMesLocalID` 或 `m_n64MesSvrID` 做去重

### 16.4 群聊消息

- 群消息 `m_nsFromUsr` 是群 ID（`xxx@chatroom`）
- 实际发送者在 `m_nsRealChatUsr`
- 必须调用 `ChangeForChatRoom` 后才能正确获取群聊信息

### 16.5 插件命名

- 自定义类名加统一前缀（如 PJ / PKC / WGM）避免冲突
- 部分插件使用随机字符串混淆类名增加逆向难度

### 16.6 Hook 链兼容

- **务必调用原始方法**（orig 指针），不破坏 Hook 链
- 多个插件可能 Hook 同一方法，确保链不断裂
- 异常处理：任何 Hook 内的异常都应 catch，避免影响微信正常运行

### 16.7 编译部署

```bash
# 使用 clang 直接编译（无需 theos）
clang -shared -o YourPlugin.dylib YourPlugin.m \
    -framework Foundation \
    -framework UIKit \
    -arch arm64 \
    -isysroot $(xcrun --sdk iphoneos --show-sdk-path) \
    -target arm64-apple-ios15.0

# optool 注入
optool install -c load -p @executable_path/Frameworks/YourPlugin.dylib -t WeChat

# 签名（必须与主程序同证书）
codesign -f -s "Your Signing Identity" YourPlugin.dylib
```

---

## 17. 附录

### 17.1 各插件完整 Hook 点对比矩阵

| Hook 点 | MikotoHelper | PKC | HBWechat | WCPulse | WCEhance | MiYou | HBB |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| AsyncOnPreAddMsg:MsgWrap: | | x | x | x | | | |
| AddMsg:MsgWrap: | x | x | x | x | x | | |
| AsyncOnAddMsg:MsgWrap: | x | | x | x | | x | |
| BatchAddMsg:ShowPush: | | | | | | x | |
| onRevokeMsg: | x | x | x | x | x | x | |
| getContactByName: | x | x | x | x | x | x | x |
| reloadTableData | x | x | x | x | x | x | |
| viewDidLoad | x | x | x | x | x | x | x |
| StartDownloadImage (各版本) | | x | x | x | | x | |
| registerControllerWithTitle: | | | | | | x | |

### 17.2 各插件依赖的特殊框架

| 框架 | 用途 | 使用的插件 |
|------|------|-----------|
| AVFoundation | 音视频处理 | MikotoHelper, PKC, HBWechatHelper |
| Photos / PhotosUI | 相册访问 | MikotoHelper, PKC, HBWechatHelper, MiYou |
| LocalAuthentication | Face ID / Touch ID | HBWechatHelper |
| PushKit | VoIP 推送 | HBB |
| CryptoKit | 加密 | HBB |
| CoreMotion | 运动传感器（步数） | MiYou |
| CoreLocation | 定位（虚拟定位） | MiYou (弱链接), HBB (弱链接) |
| WebKit | 内嵌网页 | PKC, HBWechatHelper |
| JavaScriptCore | JS 注入（广告屏蔽） | FuckWeChatAdBlocker |
| libsqlite3 | 本地数据库 | PKC, DouTu |
| VideoToolbox | 视频编解码 | HBWechatHelper |
| libz / libbz2 / libiconv | 压缩/编码 | HBWechatHelper |

### 17.3 内嵌音频编解码库

| 库 | 用途 | 内嵌的插件 |
|----|------|-----------|
| SILK Codec | 微信语音格式编解码 | PKC, HBWechatHelper, MiYou |
| LAME MP3 | MP3 编码 | HBWechatHelper, MiYou |
| FFmpeg | 通用音视频处理 | HBWechatHelper |

### 17.4 PKC 步数分析 SQL 查询参考

```sql
-- 查询指定日期范围的步数数据
SELECT username, score, time FROM sportinfo
WHERE time >= '%@ 21:00:00' AND time <= '%@ 05:00:00'
AND score > 0 AND score <= 40000 AND username = '%@'

-- 按最大步数排名
SELECT username, MAX(score) max_score FROM sportinfo
WHERE time >= '%@ 00:00:00' AND time <= '%@ 05:00:00'
AND score >= 500 AND score <= 6000
GROUP BY 1 ORDER BY 2 DESC

-- 检测异常步数（>=10000）
SELECT DISTINCT username FROM sportinfo
WHERE time >= '%@ 00:00:00' AND time <= '%@ 05:00:00'
AND score >= 10000

-- 统计聊天打开次数
SELECT COUNT(1) openNum FROM huihualog WHERE time >= '%@' AND time <= '%@'

-- 最活跃的 10 个会话
SELECT username, COUNT(1) num FROM huihualog
WHERE time >= '%@' AND time <= '%@'
GROUP BY 1 ORDER BY num DESC LIMIT 10
```

### 17.5 WCPulse 内部通知名称

| 通知 | 用途 |
|------|------|
| `WCPulseConfigChangedNotification` | 通用配置变更 |
| `WCPulseGroupBadgeSettingChanged` | 群角标设置变更 |
| `WCPulseGroupFilterSettingChanged` | 群过滤设置变更 |
| `WCPulseGroupBackgroundColorSettingChanged` | 群背景色变更 |
| `WCPulseGroupFontColorSettingChanged` | 群字体色变更 |
| `WCPulseGroupFontSizeSettingChanged` | 群字号变更 |
| `WCPulseFoldTopSessionSettingChanged` | 折叠置顶会话变更 |
| `WCPulseToolbarCollapseChanged` | 工具栏折叠状态变更 |
| `com.wcpulse.fontConfigChanged` | 字体配置变更 |

### 17.6 Config 架构汇总

| 插件 | Config 类 | 表格管理器 | HUD/Toast |
|------|-----------|-----------|-----------|
| MikotoHelper | (直接 NSUserDefaults) | `MMTableViewInfo` | `YTProgressHUD` |
| PKCWeChatTools | `PKCConfig` | `WCTableViewManager` | `UIAlertController` 封装 |
| HBWechatHelper | `HBConfigUtil` | `MMTableViewInfo` | 自定义 alert + toast |
| WCPulse | `WCPulseConfig.sharedConfig` | `WCTableViewManager` | 标准 alert |
| WCEhance | `WCEhanceConfig.shared` | `WCTableViewManager` | 标准 alert |
| MiYou | `MiYouConfig.sharedConfig` | `WCTableViewManager` | `MiYouHudView` / `MiYouToastView` |
| DouTu | `DouTuConfig.sharedConfig` | 自定义 CollectionView | 标准 alert |
