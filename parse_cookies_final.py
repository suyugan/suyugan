# 整理后的 Douyin Cookie
# 从浏览器导出整理

# 提取所有有效的 cookie
cookies = [
    "biz_trace_id=7bb55ef3",
    "d_ticket=1e00932a8f79c906fa81d4aecd8ca1b09c070",
    "device_web_cpu_core=28",
    "device_web_memory_size=8",
    "download_guide=%222%2F20260205%2F0%22",
    "dy_sheight=1080",
    "dy_swidth=1920",
    "enter_pc_once=1",
    "fg_uid=RID202602051159248C1CA7D5DFC6792AA862",
    "FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAEvufqx9Urjp2omzFQ3t_-rFp1o997laDv-HSsgGGYNM%2F1770307200000%2F0%2F1770289246120%2F0%22",
    "FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAEvufqx9Urjp2omzFQ3t_-rFp1o997laDv-HSsgGGYNM%2F1770307200000%2F0%2F1770264729752%2F0%22",
    "fpk1=U2FsdGVkX1/ACU86TL5fslCEi3ULf2nw3ciyYoJomfzAC7H1TDcRJu7IA3q3eHtiZnMKwr+NNQBCgpfqOQ2qOg==",
    "fpk2=8e253f85246590342756399a57054cb8",
    "gulu_source_res=eyJwX2luIjoiNjU5NTEzOWNiNWY3ZDAzY2U1YmNkZjNlM2M2MDQwZjk0N2JiNGVkYWUzZjc5N2FhNzAzZjczZDcwZjlmODQyMSJ9",
    "hevc_supported=true",
    "home_can_add_dy_2_desktop=%221%22",
    "is_dash_user=1",
    "is_staff_user=false",
    "IsDouyinActive=true",
    "login_time=1770263953355",
    "n_mh=6qq-cGgTT9fkYiwsN45Jh1uyewEXJiS4wSqKokLJKf",
    "odin_tt=420274863de80f3eac93cf4bf40cb73ddee1d5b646aa15d726ae9aba5fafad01252e77ceda62cee289607d17903faa9806e04da4d02511e09a412b4e4f6f2fd",
    "passport_assist_user=CjyVAHuQQT7Z3noeqCb8Fir9VyM8Bsl68PBs27CXHnbCItSXIeis-xX2FaTYOUeCBawf47hHQG29FiriTycaSgo8AAAAAAAAAAAAAFAJy9FLgN2u0PW1tkSTsdCxhSte1GoUSfRge0bzFrXrNDxI3qdsHfjkh6s218U9qkRKEJPmiA4Yia_WVCABIgEDfG2lqA%3D",
    "passport_auth_mix_state=6y4lhqsin3198bi7nlees0sfw5v64tnx",
    "passport_auth_status=041df386e7e0bc720ca917632b40d521%2C",
    "passport_auth_status_ss=041df386e7e0bc720ca917632b40d521%2C",
    "passport_csrf_token=7f27f61d7953c1bc729f3358641e8603",
    "passport_csrf_token_default=7f27f61d7953c1bc729f3358641e8603",
    "passport_mfa_token=CjWB2c3ruZY974tKVp84YXn8HutDP%2FEd1wpjrvkTZhLICx2ahaIz7OXz6JzdL573BXpIBsKwCxpKCjwAAAAAAAAAAAAAUAk4z7emGEwbm%2Fz787DxCKr3ZwoX7nYEwVqPFB2CSXCXmOmn2mkx8rNqAFatknFg6JMQheaIDhj2sdFsIAiAQOvqSv7",
    "publish_badge_show_info=%220%2C0%2C0%2C1770263958500%22",
    "record_force_login=%7B%22timestamp%22%3A1770263838553%2C%22force_login_video%22%3A1%2C%22force_login_live%22%3A0%2C%22force_login_direct_video%22%3A0%7D",
    "s_v_web_id=verify_ml8xdqv2_K5psOyk1_V0q0_4Ha1_8kqM_BPuee0ipb9Lo",
    "sdk_source_info=7e276470716a68645a606960273f276364697660272927676c715a6d6069756077273f27636469766027292762696a6764695a7364776c6467696076273f275e58272927666a6b5a7666776c7571273f2763646976602729276d6a6e5a6b6a716c273f27636469766027292771273f2763646976602729277f6b5a666475273f2763646976602729276c6b6f5a7f6367273f27636469766027292771273f27643c3c3430373c3d3735323234272927676c715a75776a716a666a69273f2763646976602778",
    "sessionid=6qq-cGgTT9fkYiwsN45Jh1uyewEXJiS4wSqKokLJKf"
]

# 转换为 API 需要的格式
cookie_string = "; ".join(cookies)

print("Cookie String:")
print(cookie_string)
