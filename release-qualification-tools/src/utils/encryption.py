import gzip
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def pack_and_encrypt(content: str, vector: str, key: str):
    text_bytes = content.encode("utf-8")
    encoded_key = base64.b64decode(key)
    encoded_vector = base64.b64decode(vector)

    zipped = gzip.compress(text_bytes)
    encoded_text = base64.b64encode(zipped)
    padded_text = pad(encoded_text, AES.block_size)

    cipher = AES.new(encoded_key, AES.MODE_CBC, encoded_vector)
    cipher_text = cipher.encrypt(padded_text)

    return cipher_text
