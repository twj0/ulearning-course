"""
DES 加密模块
"""

import base64
from typing import Union

from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad


class DESCipher:
    def __init__(self, key: bytes = b"12345678"):
        self.key = key
        self.cipher = DES.new(key, DES.MODE_ECB)
    
    def encrypt(self, plaintext: Union[str, bytes]) -> str:
        if isinstance(plaintext, str):
            plaintext = plaintext.encode("utf-8")
        
        padded = pad(plaintext, DES.block_size)
        encrypted = self.cipher.encrypt(padded)
        return base64.b64encode(encrypted).decode("utf-8")
    
    def decrypt(self, ciphertext: str) -> str:
        encrypted = base64.b64decode(ciphertext)
        decrypted = self.cipher.decrypt(encrypted)
        unpadded = unpad(decrypted, DES.block_size)
        return unpadded.decode("utf-8")
