from config.email_config import EMAIL_PROVIDERS
from utils.encryption import Encryption
from utils.file_utils import FileUtils
from services.email_service import EmailService
from services.display_service import DisplayService
import json
import os
import smtplib
import imaplib
from datetime import datetime

class EmailClient:
    def __init__(self):
        """初始化邮件客户端"""
        self.email_providers = EMAIL_PROVIDERS
        self.email = ""
        self.password = ""
        self.smtp_server = ""
        self.smtp_port = 0
        self.imap_server = ""
        self.imap_port = 0
        
        # 配置文件路径
        self.config_dir = os.getcwd()  # 使用当前工作目录
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.key_file = os.path.join(self.config_dir, "key.key")
        
        # 初始化加密密钥
        self.crypto_key = Encryption.load_or_create_key(self.key_file)

    def select_email_provider(self):
        """选择邮箱服务商"""
        print("\n可用的邮箱服务商：")
        for key, provider in self.email_providers.items():
            print(f"{key}: {provider['name']}")
        
        while True:
            choice = input("\n请选择邮箱服务商 (qq/163/gmail): ").lower()
            if choice in self.email_providers:
                provider = self.email_providers[choice]
                self.smtp_server = provider["smtp_server"]
                self.smtp_port = provider["smtp_port"]
                self.imap_server = provider["imap_server"]
                self.imap_port = provider["imap_port"]
                print(f"\n已选择 {provider['name']}")
                print(f"注意：{provider['note']}")
                return True
            else:
                print("无效的选择，请重试")

    def login(self, email, password):
        """登录邮箱"""
        if not self.smtp_server:
            print("请先选择邮箱服务商！")
            if not self.select_email_provider():
                return False
        
        self.email = email
        self.password = password
        
        # 测试登录
        try:
            # 测试SMTP连接
            smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
            smtp.starttls()
            smtp.login(email, password)
            smtp.quit()
            
            # 测试IMAP连接
            imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            imap.login(email, password)
            imap.logout()
            
            print("登录成功！")
            return True
        except Exception as e:
            print(f"登录失败：{str(e)}")
            return False

    def save_credentials(self):
        """保存登录凭证"""
        if not self.email or not self.password:
            return False
        
        try:
            config = {
                "user": {
                    "email": self.email,
                    "password": Encryption.encrypt(self.crypto_key, self.password)
                },
                "provider": {
                    "name": self._get_provider_name(),
                    "smtp_server": self.smtp_server,
                    "smtp_port": self.smtp_port,
                    "imap_server": self.imap_server,
                    "imap_port": self.imap_port
                },
                "settings": {
                    "save_path": "downloads",
                    "email_limit": 30,
                    "page_size": 10,
                    "last_login": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            
            # 创建下载目录
            if not os.path.exists(config["settings"]["save_path"]):
                os.makedirs(config["settings"]["save_path"])
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print("登录信息已保存")
            return True
        except Exception as e:
            print(f"保存登录信息时出错：{str(e)}")
            return False

    def load_credentials(self):
        """加载保存的登录凭证"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 加载用户信息
                user = config.get("user", {})
                self.email = user.get("email", "")
                self.password = Encryption.decrypt(self.crypto_key, user.get("password", ""))
                
                # 加载服务商信息
                provider = config.get("provider", {})
                self.smtp_server = provider.get("smtp_server", "")
                self.smtp_port = provider.get("smtp_port", 0)
                self.imap_server = provider.get("imap_server", "")
                self.imap_port = provider.get("imap_port", 0)
                
                # 创建下载目录
                if not os.path.exists(config["settings"]["save_path"]):
                    os.makedirs(config["settings"]["save_path"])
                
                return bool(self.email and self.password)
            return False
        except Exception as e:
            print(f"加载登录信息时出错：{str(e)}")
            return False

    def _get_provider_name(self):
        """根据SMTP服务器获取服务商名称"""
        for name, provider in self.email_providers.items():
            if provider["smtp_server"] == self.smtp_server:
                return name
        return "unknown"

    def send_email(self, to_addr, subject, content, attachments=None):
        """发送邮件"""
        return EmailService.send_email(self, to_addr, subject, content, attachments)

    def receive_emails(self, folder="INBOX", limit=10):
        """接收邮件"""
        return EmailService.receive_emails(self, folder, limit)

    def display_email_list(self, emails, page=1, page_size=10):
        """显示邮件列表"""
        DisplayService.display_email_list(emails, page, page_size)

    def display_email_content(self, email):
        """显示邮件详细内容"""
        DisplayService.display_email_content(email)

    def show_help(self):
        """显示帮助信息"""
        DisplayService.show_help()