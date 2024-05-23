import base64, hmac, hashlib
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


def generate_hmac(key: bytes, message: str):
    hmac_hash = hmac.new(key, message.encode('utf-8'), hashlib.sha256)
    return hmac_hash.hexdigest()