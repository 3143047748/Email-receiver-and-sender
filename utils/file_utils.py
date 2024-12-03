import os
import tkinter as tk
from tkinter import filedialog

class FileUtils:
    @staticmethod
    def sanitize_filename(filename):
        """清理文件名，移除非法字符"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = filename.strip(' \'"')
        if len(filename) > 128:
            name, ext = os.path.splitext(filename)
            filename = name[:124] + ext
        return filename

    @staticmethod
    def select_file():
        """打开文件选择对话框"""
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        return filedialog.askopenfilename(
            title="选择要发送的文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("文本文件", "*.txt"),
                ("图片文件", "*.jpg *.jpeg *.png *.gif"),
                ("PDF文件", "*.pdf"),
                ("Word文件", "*.doc *.docx"),
                ("Excel文件", "*.xls *.xlsx")
            ]
        ) 