from Crypto.Cipher import AES
import base64

from leaked_secret import key
AES_KEYSIZE = 32


def aes_unpad(s):
    n = s[-1]
    if 0 == n:
        n = AES_KEYSIZE
    return s[:-n]


def dec():
    f = open('ciphertext', 'r')
    ciphertext = f.readlines()
    f.close()
    ans = ''
    for i in range(len(ciphertext)):
        aes = AES.new(key, AES.MODE_CBC, b'0'*16)
        m = aes.decrypt(base64.b64decode(ciphertext[i]))
        m = aes_unpad(m)
        print(m)
        ans += chr(m[-1])
    print(ans[::-1])
    

if __name__ == '__main__':
    dec()
