import numpy as np
from collections import deque
import random

def generate_key(seed,key_len):
    random.seed(seed)
    key = [random.randint(0, 1) for _ in range(key_len)]
    return key


def ascii_mess_val (message):
    #turn the message to ascii values
    ascii_val = ''.join(format(ord(char), '08b') for char in message)
    return ascii_val

def dsss_spread (bits, key):
    
    bits_list = [int(b) for b in bits]

    #repeat the key and bits
    repeated_ascii_val = np.repeat(bits_list, len(key))
    repeated_key = np.tile(key, len(bits))

    #xor to get the key for bit 0 or flipped key for 1
    spreaded_bits = repeated_key ^ repeated_ascii_val

    return spreaded_bits

def bpsk_mod (bits):

    return [1 if b==1 else -1 for b in bits]


if __name__ == "__main__":

    message = "h"
    bits = ascii_mess_val(message)
    print("ascii",bits)

    seed = 42
    key_len = 4
    key =  generate_key(seed,key_len)
    print ("key",key)

    spreaded_bits = dsss_spread (bits, key)
    print("spread" ,spreaded_bits)

    signal_mod = bpsk_mod(spreaded_bits)
    print("modulation" ,signal_mod)
