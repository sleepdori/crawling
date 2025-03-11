import os
from common.config_loader import ConfigLoader
from cipher.crypto_util import crypto_util

config = ConfigLoader()
path_separator = config.get_path_separator()
project_home = config.get("project_home")
key_file_path = config.get('key_file_path')
key_file_name = config.get('key_file_name')

crypto = crypto_util(f"{project_home}{path_separator}{key_file_path}", key_file_name)

database_server_uri = "127.0.0.1:1521/CROW_DB"
database_name = "crow_db"
database_user = "crow"
database_passwd = "again97"

encrypted_message1 = crypto.encrypt(database_user)
print(crypto.decrypt(encrypted_message1), encrypted_message1)
encrypted_message2 = crypto.encrypt(database_passwd)
print(crypto.decrypt(encrypted_message2), encrypted_message2)


encrypted_message3 = crypto.encrypt("crow")
print(crypto.decrypt(encrypted_message3), crypto.decrypt(encrypted_message1), encrypted_message3)
encrypted_message4 = crypto.encrypt("again97")
print(crypto.decrypt(encrypted_message4), encrypted_message4)


aws_access_key_id='admin'
encrypted_message = crypto.encrypt(aws_access_key_id)
print(encrypted_message)
aws_secret_access_key='minioadmin'
encrypted_message = crypto.encrypt(aws_secret_access_key)
print(encrypted_message)
