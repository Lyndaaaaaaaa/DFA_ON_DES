import requests
from bs4 import BeautifulSoup


def inverser_pc2(k16):
    k56 = ['x'] * 56
    for i, val in enumerate(TABLE_PC2):
        k56[val - 1] = k16[i]
    return ''.join(k56)


def inverser_pc1(k56):
    k64 = ['x'] * 64
    for i in range(64):
        if (i + 1) % 8 != 0:
            try:
                k64[i] = k56[TABLE_PC1.index(i + 1)]
            except ValueError:
                k64[i] = '0'
    return ''.join(k64)


def ajouter_parite(k64):
    k_final = ''
    for i in range(0, 64, 8):
        octet = k64[i:i+7]
        parite = '0' if octet.count('1') % 2 == 0 else '1'
        k_final += octet + parite
    return k_final


TABLE_PC2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32
]

TABLE_PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4
]


def recuperer_cle_maitre(k16):
    print("\n------> Etape 3 : maintenant on essay de reconstruire la cle master avec k16")
    k56 = inverser_pc2(k16)

    for i in range(256):  # 2 puissance 8
        bits_inconnus = format(i, '08b')
        k56_temp = list(k56)

        indices_inconnus = [8, 17, 21, 24, 34, 37, 42, 53]
        for idx, bit in zip(indices_inconnus, bits_inconnus):
            k56_temp[idx] = bit

        k56_str = ''.join(k56_temp)
        k64 = inverser_pc1(k56_str)
        k64_parite = ajouter_parite(k64)

        cle_hex = format(int(k64_parite, 2), '016X')
        print(f" tentative avec cle :\t{k64_parite}")
        print(f"                     \t{cle_hex}")

        url = f"https://emvlab.org/descalc/?key={cle_hex}&iv=0000000000000000&input={format(CHIFFRE_CORRECT, '016X')}&mode=ecb&action=Decrypt&output="
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sortie = soup.find(id='output').get_text()

        if sortie == format(MESSAGE_CLAIR, '016X'):
            print(f"*** cle trouvee : {cle_hex}")
            return cle_hex

    print("???? aucune cle valide trouve apres brute force ??????")
    return None

import requests
from bs4 import BeautifulSoup


# permutation init de DES pour 64bit 
table_perm_init = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7
]



# TABLE pour expansion (32bit -> 48bit) 

expansion_tab = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1
]



# permutation dans fonction F 
perm_fct = [
    16, 7, 20, 21,
    29, 12, 28, 17,
    1, 15, 23, 26,
    5, 18, 31, 10,
    2, 8, 24, 14,
    32, 27, 3, 9,
    19, 13, 30, 6,
    22, 11, 4, 25
]

# inverse de permutation du haut
perm_fct_inv = [
    9, 17, 23, 31,
    13, 28, 2, 18,
    24, 16, 30, 6,
    26, 20, 10, 1,
    8, 14, 25, 3,
    4, 29, 11, 19,
    32, 12, 22, 7,
    5, 27, 15, 21
]


# les 8 sbox dans une liste pour simplifier 
sboxes = [
    [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],[0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],[4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],[15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],
    [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],[3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],[0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],[13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],
    [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],[13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],[13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],[1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],
    [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],[13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],[10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],[3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],
    [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],[14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],[4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],[11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],
    [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],[10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],[9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],[4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],
    [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],[13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],[1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],[6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],
    [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],[1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],[7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],[2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]
]


# recuperation de K16 depuis les chiffre foireux

def permuter(bits, table):
    return ''.join(bits[i - 1] for i in table)

def xor_bin(a, b):
    return ''.join(str(int(x)^int(y)) for x,y in zip(a,b))

def applique_sbox(sbox, bits):
    ligne = int(bits[0] + bits[-1], 2)
    col = int(bits[1:5], 2)
    return format(sbox[ligne][col], '04b')

def intersec(listes):
    return list(set.intersection(*map(set, listes)))



#     on recup k16 en analysant des chiffre faux

def recuper_k16():
    print("\n------> etape 1 : on lance la recup de k16 avec les chiffre faux")
    k16_possibles = [[] for _ in range(8)]

    r16_bon, l16_bon = obtenir_r_l(CHIFFRE_CORRECT)
    r15_bon = l16_bon
    r15_exp = permuter(r15_bon, expansion_tab)

    for i, chiffre_bad in enumerate(CHIFFRES_FAUTES):
        print(f"\n analyse chiffre fautif #{i+1} : {hex(chiffre_bad)}")

        r16_bad, l16_bad = obtenir_r_l(chiffre_bad)
        r15_bad = l16_bad
        r15_bad_exp = permuter(r15_bad, expansion_tab)

        diff = xor_bin(r16_bon, r16_bad)
        diff_inv = permuter(diff, perm_fct_inv)

        for j in range(8):
            seg = diff_inv[j*4:(j+1)*4]
            if seg == '0000': continue
            candidats = []
            for k in range(64):
                k_bin = format(k, '06b')
                out1 = applique_sbox(sboxes[j], xor_bin(r15_exp[j*6:(j+1)*6], k_bin))
                out2 = applique_sbox(sboxes[j], xor_bin(r15_bad_exp[j*6:(j+1)*6], k_bin))
                if xor_bin(out1, out2) == seg:
                    candidats.append(k_bin)
            k16_possibles[j].append(candidats)
            print(f"   sbox {j+1} -> {len(candidats)} candidats : {candidats}")

    print("\n------> etape 2 : intersection des valeurs candidates pour avoir k16 final")
    k16 = ''
    for j in range(8):
        inter = intersec(k16_possibles[j])
        k16 += inter[0] if inter else '000000'
        print(f"   sbox {j+1} -> finale : {inter if inter else 'aucune'}")

    print(f"\n!!!!! cle K16 reconstitue : {k16}\n")
    return k16


def obtenir_r_l(chiffre):
    bits = format(chiffre, '064b')
    perm = permuter(bits, table_perm_init)
    return perm[:32], perm[32:]



CHIFFRE_CORRECT = 0x85B2833FDAAF0E2D
MESSAGE_CLAIR = 0xA810EF37C1C78570

CHIFFRES_FAUTES = [
    0x87E3873A8ABF0E2B, 0xD5B29236DAEB2E2D, 0x95F2863FDAAD2E2D,
    0x95B0C27FFAAE1F6D, 0x85F2937982BE0E2C, 0x95B2E32FDBAF5F4D,
    0x85A0817FDAAF0E2D, 0xE5B2833FDEA71F2C, 0x11B6C32BDBAE0ABD,
    0xC5F28379CAAE062C, 0xC5B3833FDA2F0638, 0x8532932F93BF0E2C,
    0x85E383BBC9AF4E39, 0xC5B29B3FDEBB0E64, 0x8532033FDBAF0A2D,
    0x8CB2833F9AB90E2D, 0xB5B2D32FDDEF5F0D, 0x84F387BFCBAF4C39,
    0x84F2C63FCA8F0C2D, 0x85C2833BCCAF1E2D, 0x81B7C31F5BAF4B7D,
    0x85E2853E8ABE0E2F, 0x8592A33FDEAF0F6D, 0x87A2833BDA2F0E3D,
    0xCCF2973F8EBB0E64, 0x81B7C31FDAAF8F6D, 0x85B7933FDAE78E2C,
    0x85BF833F1BBF4A3D, 0xD5B2D236FAEB1F6D, 0x85B6032BDAAE4ABD,
    0x85BA8B3E9AAB0E2D, 0x15B2832FDB8F0A2D
]

if __name__ == '__main__':
    k16 = recuper_k16()
    cle = recuperer_cle_maitre(k16)
    print(f"\n Fin. La cle finale : {cle if cle else 'non trouvee'}")
