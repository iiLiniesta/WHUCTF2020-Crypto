key = "Let_5 H4V3 Fun p1ayin9 WHUCTF Crypt0"
all = list(range(ord('A'), ord('Z') + 1)) + list(range(ord('0'), ord('9') + 1)) + [ord('_')]


def get_book(key):
    now = 0
    enc_book = dict()
    dec_book = dict()
    for c in key.upper():
        if c not in enc_book and ord(c) in all:
            enc_book[c] = chr(all[now])
            now += 1
    for i in all:
        c = chr(i)
        if c in enc_book:
            continue
        enc_book[c] = chr(all[now])
        now += 1
    for c in enc_book:
        dec_book[enc_book[c]] = c
    return enc_book, dec_book


def dec(cipher):
    enc_book, dec_book = get_book(key)
    plaintext = ""
    for c in cipher.upper():
        if ord(c) not in all:
            plaintext += c
        else:
            plaintext += dec_book[c]
    print(plaintext)
    
    
if __name__ == '__main__':
    cipher = input("Input cipher:")
    dec(cipher)
