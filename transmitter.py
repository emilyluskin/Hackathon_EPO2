import random

def generate_key(length, seed=4):
    random.seed(seed)
    return [random.randint(0,1) for _ in range(length)]

def text_to_bits(text):
    bits = []
    for byte in text.encode():
        for i in range(8):
            bits.append((byte >> (7-i)) & 1)
    return bits

def dsss_spread(bits, key):
    chips = []
    for bit in bits:
        for k in key:
            chips.append(bit ^ k)
    return chips

def bpsk_map(bits):
    return [1 if b == 1 else -1 for b in bits]

def transmitter(message, key_length=8):
    bits = text_to_bits(message)
    key = generate_key(key_length)
    chips = dsss_spread(bits, key)
    signal = bpsk_map(chips)
    print(f"Message: {message}")
    print(f"Bits: {bits}")
    print(f"Key: {key}")
    print(f"Chips: {chips}")
    return signal, key

if __name__ == "__main__":
    message = "Hello"
    signal, key = transmitter(message)
 