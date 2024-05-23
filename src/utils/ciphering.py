import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def encrypt_aes(key: bytes, plaintext: str) -> bytes:
    cipher = AES.new(key=key, mode=AES.MODE_ECB)
    padded_plaintext = pad(plaintext.encode(), AES.block_size)
    encrypted_text = cipher.encrypt(padded_plaintext)
    return encrypted_text


def decrypt_aes(key: bytes, ciphertext: bytes) -> str:
    cipher = AES.new(key=key, mode=AES.MODE_ECB)
    return unpad(cipher.decrypt(base64.b64decode(ciphertext)), AES.block_size).decode()
