import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import email.utils
from bs4 import BeautifulSoup
import os
from utils.file_utils import FileUtils
from utils.path_utils import PathUtils

class EmailService:
    @staticmethod
    def send_email(client, to_addr, subject, content, attachments=None):
        """发送邮件"""
        msg = MIMEMultipart()
        msg['From'] = client.email
        msg['To'] = to_addr
        msg['Subject'] = subject
        
        # 添加发送时间
        msg['Date'] = email.utils.formatdate(localtime=True)
        
        # 在邮件内容中添加时间信息
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_content = f"发送时间：{current_time}\n\n{content}"
        
        # 添加邮件正文
        msg.attach(MIMEText(full_content, 'plain', 'utf-8'))

        # 添加附件
        if attachments:
            for file_path in attachments:
                try:
                    with open(file_path, 'rb') as f:
                        attachment = MIMEApplication(f.read())
                        filename = os.path.basename(file_path)
                        attachment.add_header('Content-Disposition', 'attachment', 
                                           filename=filename)
                        msg.attach(attachment)
                except Exception as e:
                    print(f"添加附件 {file_path} 失败：{str(e)}")

        # 发送邮件
        try:
            server = smtplib.SMTP(client.smtp_server, client.smtp_port)
            server.starttls()
            server.login(client.email, client.password)
            server.send_message(msg)
            server.quit()
            print("邮件发送成功！")
            return True
        except Exception as e:
            print(f"发送邮件时出错：{str(e)}")
            return False

    @staticmethod
    def get_email_content(email_message):
        """获取邮件内容，支持多种格式"""
        content = ""
        html_content = ""
        
        # 处理邮件内容
        for part in email_message.walk():
            # 处理文本内容
            if part.get_content_maintype() == 'text':
                text = part.get_payload(decode=True)
                if part.get_content_type() == 'text/plain':
                    content = EmailService.decode_text_content(text)
                elif part.get_content_type() == 'text/html' and not content:
                    try:
                        html = EmailService.decode_text_content(text)
                        soup = BeautifulSoup(html, 'html.parser')
                        html_content = soup.get_text()
                    except:
                        html_content = "（HTML内容解析失败）"
        
        # 如果没有纯文本内容，使用处理过的HTML内容
        if not content and html_content:
            content = html_content
        
        return content or "（没有可显示的内容）"

    @staticmethod
    def get_attachments_info(email_message):
        """获取邮件的附件信息,不下载"""
        attachments = []
        
        for part in email_message.walk():
            if part.get_content_maintype() != 'multipart' and part.get_content_maintype() != 'text':
                filename = part.get_filename()
                if filename:
                    try:
                        filename = EmailService.decode_email_field(filename)
                        content_type = part.get_content_type()
                        size = len(part.get_payload(decode=True))
                        attachments.append({
                            'filename': filename,
                            'type': content_type,
                            'size': size,
                            'part': part  # 保存part对象以供后续下载使用
                        })
                    except:
                        continue
        
        return attachments

    @staticmethod
    def download_attachment(attachment):
        """下载指定的附件"""
        try:
            filename = FileUtils.sanitize_filename(attachment['filename'])
            file_path = PathUtils.get_download_path(filename)
            
            with open(file_path, 'wb') as f:
                f.write(attachment['part'].get_payload(decode=True))
            
            return file_path
        except Exception as e:
            print(f"下载附件 {attachment['filename']} 失败：{str(e)}")
            return None

    @staticmethod
    def receive_emails(client, folder="INBOX", limit=10):
        """接收邮件"""
        if not client.email or not client.password:
            print("请先登录邮箱！")
            return []
            
        try:
            print("正在连邮件服务器...")
            server = imaplib.IMAP4_SSL(client.imap_server, client.imap_port)
            
            print("正在登录...")
            server.login(client.email, client.password)
            
            print("正在获取邮件列表...")
            status, messages = server.select(folder)
            
            if status != 'OK':
                print("无法访问邮件文件夹")
                return []

            status, message_numbers = server.search(None, "ALL")
            
            if status != 'OK':
                print("搜索邮件失败")
                return []
                
            if not message_numbers[0]:
                print("邮箱为空")
                return []

            email_list = []
            message_ids = message_numbers[0].split()
            
            if not message_ids:
                print("没有找到任何邮件")
                return []

            for num in reversed(message_ids[-limit:]):
                try:
                    status, msg_data = server.fetch(num, '(RFC822)')
                    
                    if status != 'OK':
                        print(f"获取邮件 {num} 失败，跳过")
                        continue
                        
                    email_body = msg_data[0][1]
                    email_message = email.message_from_bytes(email_body)
                    
                    # 解析邮件内容
                    try:
                        subject = EmailService.decode_email_field(email_message["subject"]) or "（无主题）"
                        from_addr = EmailService.decode_email_field(email_message["from"]) or "（未知发件人）"
                    except:
                        subject = "（无主题）"
                        from_addr = "（未知发件人）"
                    
                    email_dict = {
                        "id": num.decode(),
                        "subject": subject,
                        "from": from_addr,
                        "date": email_message["date"] or "（未知日期）",
                        "content": EmailService.get_email_content(email_message),
                        "attachments": EmailService.get_attachments_info(email_message)  # 只获取附件信息,不下载
                    }

                    email_list.append(email_dict)
                except Exception as e:
                    print(f"处理邮件 {num} 时出错：{str(e)}")
                    continue

            server.close()
            server.logout()
            
            if not email_list:
                print("没有获取到任何邮件")
            return email_list

        except imaplib.IMAP4.error as e:
            print(f"IMAP服务器错误：{str(e)}")
            return []
        except Exception as e:
            print(f"接收邮件时出错：{str(e)}")
            return []

    @staticmethod
    def decode_email_field(field_value):
        """解码邮件字段"""
        try:
            value = email.header.decode_header(field_value)[0][0]
            if isinstance(value, bytes):
                try:
                    return value.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        return value.decode('gbk')
                    except:
                        return value.decode('gb2312', errors='ignore')
            return value
        except:
            return "（解码失败）"

    @staticmethod
    def decode_text_content(text, default_msg="（邮件内容解码失败）"):
        """解码文本内容"""
        try:
            return text.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return text.decode('gbk')
            except:
                try:
                    return text.decode('gb2312')
                except:
                    return default_msg