import base64
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def fix_base64_padding(s):
    # Base64 encoded strings need to have a length that is a multiple of 4.
    missing_padding = len(s) % 4
    if missing_padding:
        s += '=' * (4 - missing_padding)
    return s

def aes_decrypt(ciphertext_base64, key_base64, expected_length=20):  # 设置预期的有效数据长度
    ciphertext_base64_fixed = fix_base64_padding(ciphertext_base64)
    key_base64_fixed = fix_base64_padding(key_base64)

    print(f"Fixed Base64 Ciphertext: {ciphertext_base64_fixed}")
    print(f"Fixed Base64 Key: {key_base64_fixed}")

    ciphertext = base64.b64decode(ciphertext_base64_fixed)
    key = base64.b64decode(key_base64_fixed)

    print(f"Decoded Ciphertext (hex): {ciphertext.hex()}")
    print(f"Decoded Key (hex): {key.hex()}")

    iv = b'\x00' * 16  # 128 bits IV for AES

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    plaintext_padded = decryptor.update(ciphertext) + decryptor.finalize()

    print(f"Plaintext Padded (hex): {plaintext_padded.hex()}")

    try:
        # 直接取预期长度的数据，假设这些字节是有效数据
        plaintext = plaintext_padded[:expected_length]

        # 解码为字符串
        return plaintext.decode('utf-8', errors='replace')
    except Exception as e:
        print("An error occurred while decoding plaintext:", str(e))
        return plaintext_padded.hex()  # 返回带填充的明文以便检查

# Given encrypted string and key, starting from the third character as per MySQL substr function
ciphertext_base64 = 'P-gS72xyQRK0yJT5U3+Vy8KsiNPzQ/beHivLPvVYz/+kI'[2:]
key_base64 = 'XDM4Vvla+6kxP++4yOXb5A=='

try:
    decrypted_text = aes_decrypt(ciphertext_base64, key_base64, expected_length=20)  # 根据实际情况调整长度
    print("Decrypted text:", decrypted_text)
except Exception as e:
    print("An error occurred during decryption:", str(e))