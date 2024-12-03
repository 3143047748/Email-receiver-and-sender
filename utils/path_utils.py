import os

class PathUtils:
    @staticmethod
    def ensure_dir(dir_path):
        """确保目录存在，如果不存在则创建"""
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path
    
    @staticmethod
    def get_download_path(filename):
        """获取下载文件的完整路径"""
        download_dir = 'downloads'
        PathUtils.ensure_dir(download_dir)
        return os.path.join(download_dir, filename) 