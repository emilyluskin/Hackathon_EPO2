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

def build_preamble(preamble,key):
    spread_pre = dsss_spread(preamble,key)
    bpsk_pre = bpsk_mod(spread_pre)
    return bpsk_pre

def final_signal(preamble, data):

    return (preamble + data)

if __name__ == "__main__":

    barker_13_bits = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
    print("barker", barker_13_bits)
    message = "h"
    bits = ascii_mess_val(message)
    print("ascii",bits)

    seed = 42
    key_len = 2
    key =  generate_key(seed,key_len)
    print ("key",key)

    spreaded_bits = dsss_spread (bits, key)
    print("spread bits" ,spreaded_bits)

    spreaded_bpsk_preamble = build_preamble(barker_13_bits,key)
    print("preamble", spreaded_bpsk_preamble)
    signal_mod = bpsk_mod(spreaded_bits)
    print("modulation signal" ,signal_mod)

    signal_trs = final_signal(spreaded_bpsk_preamble,signal_mod )
    print("pre+signal",signal_trs )


    # a=np.array([1,1])
    # b=np.array([0,2,3])
    # print(np.concatenate((a,b)))
