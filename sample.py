from common.config_loader import ConfigLoader
from cipher.ras_cipher import generate_and_save_keys, encrypt_message, load_key, decrypt_message
# ConfigLoader 인스턴스 생성
config = ConfigLoader()

if __name__ == "__main__":
    try:
        # 설정 값을 실시간으로 가져옴
        base_mode = config.get("Environment")
        log_level = config.get("logLevel", default="INFO")
        app_name = config.get("AppName")
        key_file_path = config.get("key_file_path")
        public_key_file = config.get("public_key_file")
        private_key_file = config.get("private_key_file")

        print(f"base_mode: {base_mode}")
        print(f"Log Level: {log_level}")
        print(f"App Name: {app_name}")
        print(f'key file: {config.get("key_file_name")}')
        print(f'public_key_file: {config.get("public_key_file")}')
        print(f'private_key_file: {config.get("private_key_file")}')

        print(f'oracle uri : {config.get("databases", "smip_slsi", "host")}:{config.get("databases", "smip_slsi", "port")}/{config.get("databases", "smip_slsi", "database")}')
        print(f'user  : {config.get("databases", "smip_slsi", "user")}, passwd : {config.get("databases", "smip_slsi", "password")}')
        print(f'postgresql uri : {config.get("databases", "crow_pg", "host")}:{config.get("databases", "crow_pg", "port")}/{config.get("databases", "crow_pg", "database")}')
        print(f'user  : {config.get("databases", "crow_pg", "user")}, passwd : {config.get("databases", "crow_pg", "password")}')    

    except FileNotFoundError as e:
        print(e)


    path = key_file_path
    private_key_file_nm = private_key_file
    public_key_file_nm = public_key_file

    # 키 생성 및 저장
    generate_and_save_keys(path, private_key_file_nm, public_key_file_nm)

    # 키 로드
    private_key = load_key(f"{path}/{private_key_file_nm}", is_private=True)
    public_key = load_key(f"{path}/{public_key_file_nm}", is_private=False)

    # 암호화할 메시지
    message = b"This is a secret message."

    # 암호화
    ciphertext = encrypt_message(public_key, message)
    print("Ciphertext:", ciphertext)

    # 복호화
    plaintext = decrypt_message(private_key, ciphertext)
    print("Plaintext:", plaintext.decode())        
