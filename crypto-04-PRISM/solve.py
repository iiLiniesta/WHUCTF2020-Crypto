import random
import math
from Crypto.Util.number import long_to_bytes, bytes_to_long
from Crypto.Cipher import AES
from Crypto.Util import Counter
import gmpy2


def Generate_PrimeTable_Sieve(n):  # Eratosthenes
    l = list(range(1, n + 1))
    l[0] = 0
    for i in range(2, n + 1):
        if l[i - 1] != 0:
            for j in range(i * 2, n + 1, i):
                l[j - 1] = 0
    result = [x for x in l if x != 0]
    return result


def p_sub_1_attack(n, e):
    DIFFICULTY1, TRIAL_NUM = 20, 100
    A = 1 << DIFFICULTY1
    PrimesTable = Generate_PrimeTable_Sieve(A)
    r = []
    for prime in PrimesTable:
        a = math.floor(math.log(A, prime))
        r.append(prime ** a)
    p, q = 0, 0
    for _ in range(TRIAL_NUM):
        base = PrimesTable[random.randint(0, len(PrimesTable) - 1)]
        x = base
        for pa in r:
            x = pow(x, pa, n)
        if x != 1:
            p = gmpy2.gcd(x - 1, n)  # p = gcd(x-1,n)
            q = n // p  # q = n / p
            break
    phi = (p - 1) * (q - 1)
    d = gmpy2.invert(e, phi)
    return p, q, d


def FFF_1(food, key):
    K = 0xe238c70fe2d1885a1b12debfa15484cab8af04675c39ff4c633d6177f234ed88
    key = long_to_bytes(key, 32)
    food = long_to_bytes(food, 128)
    aes = AES.new(key, AES.MODE_CTR, counter=Counter.new(128, initial_value=K))
    c = bytes_to_long(aes.decrypt(food))
    return c


def GGG_1(food, key):
    K = 0xfd94d8de73e4aa8f4f452782b98a7870e82ec92a9db606fe4ca41f32d6df90c5
    K = long_to_bytes(K, 32)
    food = long_to_bytes(food, 128)
    aes = AES.new(K, AES.MODE_CTR, counter=Counter.new(128, initial_value=key))
    c = bytes_to_long(aes.decrypt(food))
    return c


def solve0(n, e):
    p, q, d = p_sub_1_attack(n, e)
    return n, d


def solve1(n, e, N, D):
    p = pow(e, D, N)
    assert 0 == n % p
    q = n // p
    phi = (p-1) * (q-1)
    d = gmpy2.invert(e, phi)
    return n, d


def solve2(n, e, N, D):
    Nbit = 1024
    nbit = 2048
    K = 0xb6a022cd2fb960d4b6caa601a0412918fd80656b76c782fa6fe9cf50ef205ffb
    B1 = 8
    B2 = 8
    B3 = 1024
    ntop = n >> Nbit
    d = 0
    for k in range(0, B3):
        if k % 10 == 0:
            print("solve2: k =", k)
        p3 = ntop - k
        for j in range(0, B2):
            p2 = GGG_1(p3, K + j)
            p1 = pow(p2, D, N)
            for i in range(0, B1):
                p = FFF_1(p1, K + i)
                if 0 == n % p:
                    q = n // p
                    phi = (p - 1) * (q - 1)
                    d = gmpy2.invert(e, phi)
                    break
            if d > 0:
                break
        if d > 0:
            break
    assert d > 0
    return n, d


def solve3(p, g, y, N, D):
    Nbit = nbit = 2048
    K = 0xfcec710a0313bb8f93e76e00ae6862b9be72dfd837db3b64ddde344bebfd2f50
    B1 = 8
    B2 = 1024
    x = 0
    for j in range(B2, -1, -1):
        if j % 100 == 0:
            print("solve3: j =", j)
        f = p - j
        for i in range(0, B1):
            x2 = FFF_1(f, K + i)
            maybe_x = pow(x2, D, N)
            if y == pow(g, maybe_x, p):
                x = maybe_x
                break
        if x > 0:
            break
    assert x > 0
    return p, g, y, x


def solve4(p, g, y, P, G, Y, X):
    Nbit = nbit = 2048
    B = 16384
    x = 0
    d = gmpy2.invert(pow(g, X, P), P)
    for i in range(0, B):
        if i % 100 == 0:
            print("solve4: i =", i)
        b = p - i
        maybe_x = b * d % P
        if y == pow(g, maybe_x, p):
            x = maybe_x
            break
    assert x > 0
    return p, g, y, x
    

def solve_all(keys, c1, c2):
    n, e = keys[0]
    N, D = solve0(n, e)
    print("0:", hex(D))

    n, e = keys[1]
    N, D = solve1(n, e, N, D)
    print("1:", hex(D))

    n, e = keys[2]
    N, D = solve2(n, e, N, D)
    print("2:", hex(D))

    p, g, y = keys[3]
    P, G, Y, X = solve3(p, g, y, N, D)
    print("3:", hex(X))

    p, g, y = keys[4]
    P, G, Y, X = solve4(p, g, y, P, G, Y, X)
    print("4:", hex(X))
    
    M = c2 * gmpy2.invert(pow(c1, X, P), P) % P
    
    print(long_to_bytes(M))
    

if __name__ == '__main__':
    keys = [
        [
            0x8405381a3d5579319b4d9fd55224e9ce0b4091f67913c5b94c6ec15829b54e94a01a6d67dcf0fe1b411e9922ddde59bfe2cda9b36069455fd4e1b78ba21e91c532001daf951ab1af79fee2e6626beaa8855da8d6ababedc3632fdeaa9568a9c10f7396bf856753afa8641487db00ce854a5e01f00866306a93eff278f20d2645,
            0x10001, ],
        [
            0x8fd673cf7d987fa5451ac7e77687c841aef9d9b6109613cabce24d6f71c8ff89af5a69698a756c361649dade844e0238e069c857c0850b521810994eac2edce22be0f9fce279ec5e7aa3bcca41b3caa4d6ad8e07a1a5f825f9adccd5888384d92629309f8d962b57b81d16bc8d5c2c08fc5f951bf6c9f2d7c70974dead3e39b7,
            0x63d061be9751f43e223f10386e669312d62f1d11ecfc121b5b6ae99c38d114c86afd43071145953fefbb9b5a0da96e4e95db626449217d6a2529ba597dbf63cb814978782ac7b7e3453d173c6ce975b976917692820e52f8c4cb9fff0144790b88c1a7dffd717c70f8f6a2cfce362ba2002684b9812b6bb5fe4d7cdcaf968dc5, ],
        [
            0xcaec490cea0801761cef4fc444d998537f522e4e880e7ca73dc63ca7fd8cfc2310abccc5ff03618799216f591dd12db5405877a5dc1b066616007a95ff74082e0c5cc2738cf7e452110a88fc8e528b10a924a46ee0cd1237c6937ab0861784cd139c59bf5b01e436e7d4abb4f17a070d728dc16b71602e93c489ec0e26179eff769ca24d8a055fe4f1b00418cb68316d16bb66481eea5af2b0077869ce6e80dd5017c0591c77e7d44e5391d6d9b31252002936b66999375e7cf18fde53e7f652b8b036e68fe6cfb0cda307629d2e54ec400725c1fd99a51b23b52cd27698425d224ae8641f13e22564e9b5702e92a2fce8ca143d825cb4f04d93e03cb2ed64c9,
            0x10001, ],
        [
            0xcc52272693767db147968e81fd75b732d409d08dd347c0fdf0e878c7ce33b9557ed744156d2a889cc30f14603411a7993bd5f4edd6fd4b4d3303eec314f71575787c88a7718c3a27683f5a0e814770344099df4885a5f200aab8734e96d5dce1071e6b695f402a21f152eacdbdeb29ad2b64363472c20448c07bc1e0b9ccc837f096bcb4e7e36cef9901aa9abeeda92cf957498d21662c6cbf78ec1188d2ad7b5f1ba5e307ad5ee08843e41c69bbfc15bf683e8a5ea3f9f25543cd4d93349926c5845ef8c40de31e534b0142279359af2b8cb6ce03d6a2ff5d644ecb79ddb09ca2448419ed9e8d60b00c25a0f5d92d19367b3a8940f358f1f9dcf3f49648e6ed,
            0x547a6bacd423a7bb3b58232f125eb6004b72f89c249a154f858498a9a4c71a0c3851f7bd597761b86fdfa12e40390667a3cc9c051c83de1997829c68879c363b9dcc76e49dfd170926dd07b1cf5468c17232add79a531f27ce321bfb7a7c8946e2b1e9a3fa2815b40e2c537083b41085540838d361ac098aae14eddd20b59b554275afe17318aba9ba01ec9e53b6180b1dac5c3b6f587022e2f80ea304773d817875f70431623cc10e9b0ec004bac88c20014deacdc53fc39fe4524f3cf742e82e81f64f71d39d3cc5812bf0da93ecf929615e503c1ec6c7fe48a2659a04ae2ca3a798ed941a2d08ae4c6727d76cff334b1d36a701b72d93fac6524ea998ab47,
            0x7f4ebdebbe8a6161cec9a5ef9cce864666a6f3f8171aaace2dc0a9f3e765a5321d53f1ab7775f9a4b82bcfc5d7b52a0c9853ea018c30257b00a21f01ebaab556b06e2bad1dc5925759c529da3911552f9272fdac73a3a2c7b2871c877de866297eb8a74ec02873827afe8a122c00cd2945740682715bc6981fe49215740ea400d852ecb8273d4a826199a20ce3ef7a9212731e78a44d22a4c0a1cde2afaa844b332c21acc501433080cc81293aa00573ab88c6e8ffc302cefd739a74ea1c8fce5e9f88bb36a4b6845bf24479b2d7c8a4fe4f59932889fa3d43771e95ad330b5d2c593955e141aaf813441d6ce365b5eca12914db033605838aaed0db033c539c, ],
        [
            0xca15fd070931bc9ed037713c33859a51618ae7994e8b743a78d488431ac859774aa764df10b9d898f0ca5a8ea4f1ceb3b0e153d64e976410f7de524212088378ada1e5945e194bf305e7753816ad36d0ca4a768717bab626c73e2533233518e40e2c693c8a7344b588f978240af0eab18a9bf4d8efdc98b0cec607c4cae49e1a3750f74fcd3919929a0d16c78395c5b428a5bb3c86478712b8fd2c9389f9350ab07bcfd7da857d09767890e295c379f31498be07c8587ad8bb7bf20685655bd8eb82028d6698c1dc1c91ff4de624c8f01b2c0ef3bacb426865e19408d7807df2d38f33e4da83161468d36ef2be3e6f4a87105e899f670aa2aaf9c79dea58f527,
            0x395afa4e1881ea4437ea547c5ad16f379ec6bdf0188ca3e28626157ac6d4cc91200ee31fd3f0cf819c75341ea673ee1eb9c6e509cd9a004eda2f899b207e467d56aae201d18fc12142c4f33ce00d62169d413ad4cc6809fcaee959fb27260ea507859aa570ba1bed71f61b5be2716fa7600c25a1b6ab75b71ad64496bd0251be552d7968c82baf5d32f70fcae1285e4c971d0bcd4d7e069ef63f9e6f3deb90fdb6897e1d9aa08fbd3c78584514e5f132d48f3e432aea848fedb15904a2c0fe8b0ec3bae884726bc3d509cd97e43fb657a0fe0cae174429564bbeda1b37ea120addaa60b3db1c02903fed6b06e55deeae974074ceb080afd073dfbdfb5db9b25a,
            0x329da5818011ed7722285286281fdf0742008761b2d2a477df441e9cac23ad0e346e833729473a0a86c9b4425f772f6fba0d55dac438c979b4a7631ce07559829127ae53ed664403a9098a815fc0bc061280bed2594b7df06e80b8021300bbf7daf788191dcac6710523c18dca8c9567d1a32ea2c27b1d8d847b67f62d9250ced4e11b901b737c8b1da5bc2281d9e0057b39ae7f539e3daa146d2df02da6793efaec197361257315d75933259f826e0dffa036a38e4bd1314cabdc9e6eb7c21a7c23d3c1e7ee60914e7fac58a87e77e28c50875c6e4ab92156bd627ff14f1e27974268f575e546cb729743784a1c3f3fa6c6823a73e6726113a1d7558a19c588, ],
    ]
    c1 = 0x1f4e626597d94539c3b8df060ee00533babddc7155cb1c34b614df4b8aa4a0588fef27f5ee310380ec4f89be0dbe66d8e631aacd97647a0aa9ff3bdb3498b599e303fd5f891e03fa2de2f48967999db8c82f251fefe0ba2e1c212bc19325baa9ab36288969969866ed6bd3c1fcec4669952bf6b00866ed1d88eb6e81da71f2a7069488c359b0c13b34645efdc643e227d1ae0e8c012a26047395ccdff7e923e122fb97ff17fbe754f43d111c7468c5b34547cbbfb076b0831fd68c4582cbae4583365314da5a5e27caa2a4595de544e5d0df1ccaac998111c249604bbea76a6d1f8dae179353c3c56e2764927aa793b2a9fe3869a2fb746cd7a3a2acb1a753e0
    c2 = 0x4160a907ed70fc53c76bd6a074fa86b1f760ce5693136603b2d800ff7dc43abd35401eea1884e96fd7c9dd999dab0ad53f9d4845e9d4435eeb54a14989330040fa315796e2901fe06b967bfef535b2054a5598e1b9d032434417c9010763f73208e304e4cb916c625f0e6ed70ff79893c6573097e685b998e62ad5fe434e4958542a9ebb059e97029722c372f5f8788f510880210f8f7d2a894ab2d6bc98c4407bc8ee30b3720720dd171372c7f794c29b5d226ccec77ea5b15d10686fdfa21d401f3980247a0ac394f0133fbfe4fcef27af868540356e2d1c7a51b361ff29f72542c16e8367196b1f2082609510516520a5cf457753bef053673717ac1a6d7a
    solve_all(keys, c1, c2)
    
    # from keygen import keygen
    # from enc import enc
    # keys = keygen()
    # c1, c2 = enc(keys, 0x31323334353637)
    # print("keys =", keys)
    # print("c1 =", hex(c1))
    # print("c2 =", hex(c2))
    
    
    
    

