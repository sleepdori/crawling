import os
from common.config_loader import ConfigLoader
from cipher.crypto_util import CryptoUtil

config = ConfigLoader()
path_separator = config.get_path_separator()
project_home = config.get("project_home")
key_file_path = config.get('key_file_path')
key_file_name = config.get('key_file_name')

crypto_util = CryptoUtil(f"{project_home}{path_separator}{key_file_path}", key_file_name)

# database_user = "SMIP_SLSI_DEV"
# database_passwd = "1q2w3e4r!"
database_user = "SMIP_SLSI_DWDM_DEV"
database_passwd = "Slsidw2025!"

encrypted_message = crypto_util.encrypt(database_user)
print(crypto_util.decrypt(encrypted_message), encrypted_message)
encrypted_message = crypto_util.encrypt(database_passwd)
print(crypto_util.decrypt(encrypted_message), encrypted_message)

aws_secret_access_key='AVVLFzfAxyZsMfjj6r1/4juNcPPy9N2+uqdnTUSp'
encrypted_message = crypto_util.encrypt(aws_secret_access_key)
print(crypto_util.decrypt(encrypted_message), encrypted_message)
