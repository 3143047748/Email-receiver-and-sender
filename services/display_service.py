from services.email_service import EmailService

class DisplayService:
    @staticmethod
    def display_email_list(emails, page=1, page_size=10):
        """显示邮件列表，支持分页"""
        if not emails:
            print("\n没有邮件。")
            return
        
        total_pages = (len(emails) + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(emails))
        current_page_emails = emails[start_idx:end_idx]
        
        print("\n邮件列表：")
        print("="*90)
        print(f"{'序号':<6}{'日期':<25}{'发件人':<25}{'主题':<25}{'附件':<8}")
        print("-"*90)
        
        for i, email in enumerate(current_page_emails, start_idx + 1):
            # 处理过长的字段
            subject = email['subject'][:22] + '...' if len(email['subject']) > 25 else email['subject']
            sender = email['from'][:22] + '...' if len(email['from']) > 25 else email['from']
            
            # 添加附件标记 - 更新判断逻辑
            has_attachment = '' if len(email['attachments']) > 0 else ''
            
            print(f"{i:<6}{email['date'][:23]:<25}{sender:<25}{subject:<25}{has_attachment:<8}")
        
        print("="*90)
        print(f"第 {page}/{total_pages} 页 (共 {len(emails)} 封邮件)")
        print("\n操作提示：")
        print("- 输入数字 1-30 查看对应邮件")
        print("- 输入 n 查看下一页")
        print("- 输入 p 查看上一页")
        print("- 输入 0 返回主菜单")

    @staticmethod
    def display_email_content(email):
        """显示邮件详细内容"""
        print("\n" + "="*80)
        print(f"发件人: {email['from']}")
        print(f"日期: {email['date']}")
        print(f"主题: {email['subject']}")
        print("-"*80)
        print("正文:")
        print(email['content'])
        
        # 显示附件信息
        if email['attachments']:
            print("-"*80)
            print("附件列表:")
            for i, att in enumerate(email['attachments'], 1):
                size_mb = att['size'] / (1024 * 1024)
                print(f"{i}. {att['filename']} ({att['type']}, {size_mb:.2f}MB)")
            
            while True:
                choice = input("\n请输入要下载的附件编号(直接回车退出): ")
                if not choice:
                    break
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(email['attachments']):
                        file_path = EmailService.download_attachment(email['attachments'][idx])
                        if file_path:
                            print(f"附件已下载到: {file_path}")
                    else:
                        print("无效的附件编号")
                except ValueError:
                    print("请输入有效的数字")
        
        print("="*80)

    @staticmethod
    def show_help():
        """显示帮助信息"""
        help_text = """
        邮件客户端使用说明：
        
        1. 登录功能：
           - 首次使用需要选择邮箱服务商（QQ邮箱/163邮箱/Gmail）
           - 输入邮箱地址和授权码（不是邮箱密码）
           - 可以选择保存登录信息，方便下次使用
        
        2. 发送邮件：
           - 输入收件人邮箱地址
           - 输入邮件主题
           - 输入邮件内容
           - 可选择是否添加附件
           - 如需添加附件，在文件选择对话框中选择文件
        
        3. 接收邮件：
           - 显示最近10封邮件的列表
           - 包含序号、日期、发件人和主题信息
           - 输入邮件序号可查看详细内容
           - 查看详细内容时会显示：
             * 发件人信息
             * 发送日期
             * 邮件主题
             * 完整正文
             * 附件信息（如果有）
           - 输入0可返回主菜单
        
        4. 退出程序：
           - 选择退出选项即可安全退出程序
        
        注意事项：
        - QQ邮箱需要使用授权码，可在QQ邮箱设置中生成
        - 发送附件时请在文件选择对话框中选择正确的文件
        - 接收到的附件会保存在程序运行目录下
        - 接收到的图片会保存在images目录下
        """
        print(help_text)