from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def generate_and_save_keys(path, private_key_file_nm, public_key_file_nm):
    # RSA 키 쌍 생성 (4096비트)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096
    )

    # 비공개 키를 PEM 형식으로 직렬화하여 파일에 저장
    private_key_path = f"{path}/{private_key_file_nm}"
    with open(private_key_path, 'wb') as private_file:
        private_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # 공개 키를 PEM 형식으로 직렬화하여 파일에 저장
    public_key = private_key.public_key()
    public_key_path = f"{path}/{public_key_file_nm}"
    with open(public_key_path, 'wb') as public_file:
        public_file.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

def load_key(file_path, is_private):
    # PEM 형식의 키 파일 로드
    with open(file_path, 'rb') as key_file:
        if is_private:
            return serialization.load_pem_private_key(key_file.read(), password=None)
        else:
            return serialization.load_pem_public_key(key_file.read())

def encrypt_message(public_key, message):
    # 메시지 암호화
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def decrypt_message(private_key, ciphertext):
    # 메시지 복호화
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

if __name__ == "__main__":
    # 키 파일 경로 및 이름
    path = "./keys"
    private_key_file_nm = "private_key.pem"
    public_key_file_nm = "public_key.pem"

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
