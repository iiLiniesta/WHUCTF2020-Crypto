import gmpy2
from Crypto.Util.number import getRandomInteger, long_to_bytes
import itertools


def get_root_2(index, p, k, c):  # Find m such that m^index=c mod p^k
    # assert index < 1000
    print("p = " + hex(p))
    assert gmpy2.is_prime(p)
    assert p.bit_length() * k <= (2 << 16)
    
    n = p ** k
    phi = (p ** (k - 1)) * (p - 1)
    c %= n
    
    # First, split index into 2 parts, invert-able and un-invert-able.
    un_invert_able = gmpy2.gcd(index, phi)
    invert_able = index // un_invert_able
    while True:
        gcd = gmpy2.gcd(invert_able, phi)
        if gcd == 1:
            break
        invert_able //= gcd
        un_invert_able *= gcd
    assert invert_able * un_invert_able == index
    assert gmpy2.gcd(invert_able, phi) == 1
    print(invert_able, un_invert_able)
    
    # Get rid of the invert-able part.
    d = gmpy2.invert(invert_able, phi)
    c2 = pow(c, d, n)
    assert pow(c2, invert_able, n) == c
    print("c2 = " + hex(c2))
    
    # Next, find m such that m^un_invert_able=c2 mod p^k.
    now_roots = {c2}
    for r in [2, 3, 5, 7]:
        if 0 != un_invert_able % r:
            continue
        s = phi
        t = 1
        while 0 == s % r:
            t *= r
            s //= r
        # now phi=s*t=s*(r**?)
        print("r =", r, ",\tt =", t, ",\ts =", s)
        g, u, k = gmpy2.gcdext(t, s)
        print("g =", hex(g), ",\tu =", hex(u), ",\tk =", hex(k))
        assert g == 1 == u * t + k * s
        print(pow(c2, k*s, n))
        v = 0
        while 1 >= pow(v, s, n):
            v = gmpy2.next_prime(getRandomInteger(20))
        v_s = pow(v, s, n)
        print("v_s =", v_s)
        new_roots = set()
        for c_now in now_roots:
            now = pow(c_now, u, n)
            for _ in range(t):
                if not pow(now, t, n) == c_now:
                    print(hex(pow(now, t, n)))
                new_roots.add(pow(now, t // r, n))
                now = now * v_s % n
        now_roots = new_roots
    
    ans = list(now_roots)
    for m in ans:
        assert pow(m, index, n) == c
    return ans


def get_root(index, p, k, c):  # Find m such that m^index=c mod p^k
    # assert index < 1000
    print("p = " + hex(p))
    assert gmpy2.is_prime(p)
    assert p.bit_length() * k <= (2 << 16)
    
    n = p ** k
    phi = (p ** (k - 1)) * (p - 1)
    c %= n
    
    # First, split index into 2 parts, invert-able and un-invert-able.
    un_invert_able = gmpy2.gcd(index, phi)
    invert_able = index // un_invert_able
    while True:
        gcd = gmpy2.gcd(invert_able, phi)
        if gcd == 1:
            break
        invert_able //= gcd
        un_invert_able *= gcd
    assert invert_able * un_invert_able == index
    assert gmpy2.gcd(invert_able, phi) == 1
    print(invert_able, un_invert_able)

    # Get rid of the invert-able part.
    d = gmpy2.invert(invert_able, phi)
    c2 = pow(c, d, n)
    assert pow(c2, invert_able, n) == c
    print("c2 = " + hex(c2))
    
    # Next, find m such that m^un_invert_able=c2 mod p^k.
    Y = gmpy2.gcd(index, phi)
    X = phi // Y
    while True:
        gcd = gmpy2.gcd(X, un_invert_able)
        if gcd == 1:
            break
        X //= gcd
        Y *= gcd
    assert X * Y == phi
    assert gmpy2.gcd(un_invert_able + X, phi) == 1
    print("X = 0x%x,\nY = %d" % (X, Y))
    # Got a suitable Y.
    
    ans = set()
    counter = 0
    while True:
        g = gmpy2.next_prime(getRandomInteger(p.bit_length()) % p)
        for i in range(Y):
            m_uninv_and_X = c2 * pow(g, i * phi // Y, n) % n
            assert pow(m_uninv_and_X, Y, n) == pow(c2, Y, n)
            m = pow(m_uninv_and_X, gmpy2.invert(un_invert_able + X, phi), n)
            if pow(m, un_invert_able, n) == c2:
                ans.add(m)
        counter += 1
        if len(ans) >= un_invert_able or counter >= 10:
            break
    
    for m in ans:
        assert pow(m, index, n) == c
    return ans


def CRT(a_list, m_list, l):
    assert len(a_list) == len(m_list) == l > 0
    N = 1
    for m in m_list:
        N *= m
    ans = 0
    for i in range(l):
        Mi = N // m_list[i]
        ti = gmpy2.invert(Mi, m_list[i])
        ans = (ans + a_list[i] * ti * Mi) % N
    return ans


def work(index, n, p_list, k_list, c):
    l = len(p_list)
    assert len(k_list) == l
    m_list = []
    for i in range(l):
        m_list.append(p_list[i] ** k_list[i])
        assert gmpy2.is_prime(p_list[i])
    now_N = 1
    for i in range(l):
        now_N *= m_list[i]
    assert now_N == n
    
    root_list_list = []
    ans_num = 1
    for i in range(l):
        root_list = list(get_root(index, p_list[i], k_list[i], c))
        print("len(root_list) =", len(root_list))
        ans_num *= len(root_list)
        root_list_list.append(root_list)
    print("ans_num(total workload) =", hex(ans_num))
    counter = 0
    for a_list in itertools.product(*root_list_list):
        ans = CRT(a_list, m_list, l)
        counter += 1
        if counter % 0x1000 == 0:
            print("counter = " + hex(counter))
        if b'WHUCTF' in long_to_bytes(ans):
            print("counter = " + hex(counter))
            print(hex(ans), long_to_bytes(ans))
            return ans
    return 0
    
   
def solve():
    index = 210
    n = 0x1e7e40e80b73ee3ef68185c83c6dcd332a7b1783d44b6824a3f6ac1e5e55c4793d507f44b628fa7d7d7317ce174aba089463cc866e48ca0c357b1675030f31acc60b15740f3d1a329e7757b6a60521c05fcc724f05fa8320b91346b972be9ed971f725a4b28d12c8487f14aa584b1c7882f39c7a4a56ea214ff03209602f1bfed44e6bd7c41d4b552ad95532ff2ef0acf8df4f168249055bce5869c9ab1ee5c31de244712bd3ce79da4f278f9fa3c9263a2f92f2a1dbc2e5febb6a44487c8d479662928d0338f4b47a8b6c019f3847b1f24669ea394f89583f1620b9dd73715808491ce7e436eeab2f12e3bed8fc15b5f8e7c06cfb209d21f1e7a4f583b4cfc5193ec002f16d3caf4c6b4152f7a35efdfc5200947d2ec5940a7a6dceab7e67878847cc50d
    c = 0xe8327c3df503c84f79768c37a2a0cfa5883172fa6278bce54a1153318a8d4e8f14ac6fc9631f495a7467500fc9035bca3f1fc2b6e200f40f3562e048384e965e89adef49cc9a0c9bf85143a212594225abb9cb1bbdac1fcba7a02f785cc8a190cbdd3d4d3158b1571e98b8c7038d5cc0362dc5b67cfe8e268775714bd32b2b7c9ba4977d9ba4264983f9fbf3805b265d36145532219839a1bf3d0df67c7da889c1f2fb9ae465839b3592a50e93f2d58023723e94270b5b51ea27705c5c7ef9f4cb823cd81bb4a631d06e4c15d9074e3b8f6aef184e85104a5801ae9368fc0bd681db47324097a8562ecb64175c7ece17067543fc01b10edb9d833316aab154cbea361e1410d1be1a46c46c879f7fd800eb752cf77885ff791f40c535d9a3481e2004d6b4
    p_list = [
        81558703883,
        402917989931,
        23928329489,
        127206512233,
        7973312377,
        37359804007,
    ]
    k_list = [
        10, 9, 13, 8, 13, 13,
    ]
    # ans = work(index, n, p_list, k_list, c)
    # print(hex(ans))
    

if __name__ == '__main__':
    solve()
