from models.email_client import EmailClient
from utils.file_utils import FileUtils

def main():
    # 创建邮件客户端实例
    client = EmailClient()
    
    # 尝试加载保存的登录信息
    if client.load_credentials():
        print(f"\n检测到保存的登录信息（{client.email}）")
        use_saved = input("是否使用保存的登录信息？(y/n): ").lower() == 'y'
        if use_saved:
            if client.login(client.email, client.password):
                print("使用保存的登录信息登录成功！")
            else:
                print("使用保存的登录信息登录失败，请重新登录。")
                client.email = ""
                client.password = ""
    
    # 如果没有保存的登录信息或选择不使用
    if not client.email or not client.password:
        if client.select_email_provider():
            email = input("请输入邮箱地址：")
            password = input("请输入密码或授权码：")
            if client.login(email, password):
                save = input("是否保存登录信息？(y/n): ").lower() == 'y'
                if save:
                    client.save_credentials()

    # 主菜单循环
    while True:
        print("\n请选择操作：")
        print("1. 发送邮件")
        print("2. 接收邮件")
        print("3. 查看帮助")
        print("4. 退出")
        
        choice = input("请输入选项（1-4）：")
        
        if choice == "1":
            to_addr = input("请输入收件人地址：")
            subject = input("请输入邮件主题：")
            content = input("请输入邮件内容：")
            has_attachment = input("是否发送附件？(y/n)：").lower() == 'y'
            attachments = []
            if has_attachment:
                while True:
                    file_path = FileUtils.select_file()
                    if file_path:  # 如果选择了文件
                        attachments.append(file_path)
                        if input("是否继续添加附件？(y/n): ").lower() != 'y':
                            break
                    else:  # 如果取消选择
                        break
            client.send_email(to_addr, subject, content, attachments)
        
        elif choice == "2":
            emails = client.receive_emails(limit=30)  # 获取30封邮件
            current_page = 1
            page_size = 10
            
            while True:
                client.display_email_list(emails, current_page, page_size)
                
                if emails:
                    try:
                        choice = input("\n请输入操作：").lower()
                        if choice == "0":
                            break
                        
                        # 处理上一页/下一页
                        if choice == 'n':  # 下一页
                            total_pages = (len(emails) + page_size - 1) // page_size
                            if current_page < total_pages:
                                current_page += 1
                            else:
                                print("已经是最后一页了")
                            continue
                            
                        if choice == 'p':  # 上一页
                            if current_page > 1:
                                current_page -= 1
                            else:
                                print("已经是第一页了")
                            continue
                            
                        # 处理数字输入（只用于查看邮件）
                        num = int(choice)
                        if 1 <= num <= len(emails):
                            # 查看邮件详情
                            client.display_email_content(emails[num-1])
                            # 等待用户按回车返回邮件列表
                            input("\n按回车键返回邮件列表...")
                        else:
                            print("无效的输入！")
                    except ValueError:
                        if choice not in ['n', 'p']:  # 如果不是n/p，则显示错误
                            print("请输入有效的操作！")
        
        elif choice == "3":
            client.show_help()
        
        elif choice == "4":
            print("感谢使用！再见！")
            break
        
        else:
            print("无效的选择，请重试")

if __name__ == "__main__":
    main() 