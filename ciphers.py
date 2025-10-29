import string

def letter_reverser(input: str, decode: bool) -> str:
    alphabet = string.ascii_letters + string.digits
    reversed = alphabet[::-1]
    if decode == False:
        trans = str.maketrans(alphabet, reversed)
    else:
        trans = str.maketrans(reversed, alphabet)

    return input.translate(trans)

def caesar_cipher(input: str, shift: int, decode: bool) -> str:
    alphabet = string.ascii_letters + string.digits
    shift = shift % len(alphabet)

    if decode:
        shift = -shift
    
    shifted = alphabet[shift:] + alphabet[:shift]
    trans = str.maketrans(alphabet,shifted)

    return input.translate(trans)

def rail_fence(input: str, key):
    rails = [[] for _ in range(key)]
    rail_index = 0
    direction = 1

    for char in input:
        rails[rail_index].append(char)

        if rail_index == key - 1:
            direction = -1
        elif rail_index == 0:
            direction = 1
        
        rail_index += direction
    
    ciphered = ""

    for rail in rails:
        ciphered += "".join(rail)
    
    return ciphered

def decrypt_rail_fence(input, key):
    length = len(input)

    rail_map = [["\n"] * length for _ in range(key)]

    rail_index = 0
    direction = 1

    for i in range(length):
        rail_map[rail_index][i] = '*'
        if rail_index == key - 1 or rail_index == 0:
            direction *= -1
        rail_index += direction
    
    index = 0

    for r in range(key):
        for c in range(length):
            if rail_map[r][c] == '*':
                rail_map[r][c] = input[index]
                index += 1
    
    plain = ""
    rail_index = 0
    direction = 1

    for i in range(length):
        plain += rail_map[rail_index][i]
        if rail_index == key - 1 or rail_index == 0:
            direction *= -1
        rail_index += direction
    
    return plain

