# 邮箱服务商配置
EMAIL_PROVIDERS = {
    "qq": {
        "name": "QQ邮箱",
        "smtp_server": "smtp.qq.com",
        "smtp_port": 587,
        "imap_server": "imap.qq.com",
        "imap_port": 993,
        "note": "请使用QQ邮箱授权码作为密码"
    },
    "163": {
        "name": "163邮箱",
        "smtp_server": "smtp.163.com",
        "smtp_port": 587,
        "imap_server": "imap.163.com",
        "imap_port": 993,
        "note": "请使用163邮箱授权码作为密码"
    },
    "gmail": {
        "name": "Gmail",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "imap_server": "imap.gmail.com",
        "imap_port": 993,
        "note": "请确保已开启两步验证并使用应用专用密码"
    }
} 