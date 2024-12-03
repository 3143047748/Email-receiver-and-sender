from cryptography.fernet import Fernet
import os

class Encryption:
    @staticmethod
    def load_or_create_key(key_file):
        """加载或创建新的加密密钥"""
        try:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(key)
                return key
        except Exception as e:
            print(f"处理加密密钥时出错：{str(e)}")
            return None

    @staticmethod
    def encrypt(key, data):
        """加密数据"""
        if key:
            f = Fernet(key)
            return f.encrypt(data.encode()).decode()
        return data

    @staticmethod
    def decrypt(key, data):
        """解密数据"""
        if key:
            f = Fernet(key)
            return f.decrypt(data.encode()).decode()
        return data 