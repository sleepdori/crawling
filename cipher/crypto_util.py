import os
from cryptography.fernet import Fernet

class CryptoUtil:
    def __init__(self, directory, key_file_name):
        self.key_file_path = os.path.join(directory, key_file_name)
        
        # 지정된 디렉토리가 없으면 생성
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # 키 파일이 있는지 확인
        if not os.path.exists(self.key_file_path):
            # 키 파일이 없으면 새로운 키를 생성하고 파일에 저장
            self.key = Fernet.generate_key()
            with open(self.key_file_path, 'wb') as key_file:
                key_file.write(self.key)
        else:
            # 키 파일이 있으면 키를 읽어옴
            with open(self.key_file_path, 'rb') as key_file:
                self.key = key_file.read()
        
        self.fernet = Fernet(self.key)
    
    def encrypt(self, message):
        """주어진 문자열을 암호화하여 리턴합니다."""
        return self.fernet.encrypt(message.encode()).decode()

    def decrypt(self, encrypted_message):
        """암호화된 문자열을 복호화하여 리턴합니다."""
        return self.fernet.decrypt(encrypted_message.encode()).decode()

# 사용 예
# crypto = CryptoUtil('some_directory', 'my_key.key')
# encrypted_message = crypto.encrypt("Hello World")
# print(encrypted_message)
# decrypted_message = crypto.decrypt(encrypted_message)
# print(decrypted_message)
