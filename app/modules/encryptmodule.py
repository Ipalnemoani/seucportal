from Crypto import Random
from Crypto.Cipher import AES
import base64
from hashlib import md5

BLOCK_SIZE = 16

def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + (chr(length)*length).encode()

def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

def bytes_to_key(data, salt, output=48):
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]

def encrypt(message, passphrase):
    salt = Random.new().read(8)
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message)))

def decrypt(encrypted, passphrase):
    encrypted = base64.b64decode(encrypted)
    assert encrypted[0:8] == b"Salted__"
    salt = encrypted[8:16]
    key_iv = bytes_to_key(passphrase, salt, 32+16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    return unpad(aes.decrypt(encrypted[16:]))


if __name__ == "__main__":
    name_str = 'R20191207135256_attachname20191207135307864812.xlsx'
    name_encode  = name_str.encode()
    pwd = "SatanMyMaster".encode()

    uuid = encrypt(name_encode, pwd)
    print(uuid)

    hash(name_str)
    # password = "Satan".encode()
    # ct_b64 = "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"
    # pt = decrypt(ct_b64, password)
    # print("pt", pt.decode('utf8'))

    # print("pt", decrypt(encrypt(pt, password), password).decode('utf8'))
