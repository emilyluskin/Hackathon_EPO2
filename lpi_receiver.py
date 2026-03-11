import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import random

def bpsk_mod(bits):

    return [1 if b==1 else -1 for b in bits]

def generate_key(seed,key_len):
    random.seed(seed)
    key = [random.randint(0, 1) for _ in range(key_len)]
    return key

def add_noise(data):
    noise = np.random.normal(0, 1, len(data))
    return (data + noise)

def find_peaks_in_corr(input_data, modulated_key ):
    #correlation between the key and the 
    corr = np.correlate(input_data, modulated_key)
    peaks_val = [corr[i*len(modulated_key)] for i in range(int(len(input_data)/len(modulated_key)))]

    return peaks_val

def peak_classifier(peaks_val):
    
    bits = np.ones(len(peaks_val), dtype=int)

    for i in range(len(peaks_val)):
        #positive corr means no change in the key - bit 0
        if peaks_val[i] > 0:
            bits[i] = 0
        #negative corr means flipped key - bit 1
        if peaks_val[i] <= 0:
            bits[i] = 1

    bits = list(bits)
    return bits

def bits_to_string(bits):
    return ''.join(chr(int(''.join(map(str, bits[i:i+8])), 2)) for i in range(0, len(bits), 8))


if __name__ == "__main__":

    sps = 1
    # Create the key
    seed = 42
    key_len = 4
    key = generate_key(seed,key_len)

    # Perform upsampling according to the sps 
    upsampled_key = np.repeat(key, sps)

    #bpsk modulation
    modulated_key= bpsk_mod(upsampled_key)

    input_data = [-1, -1, 1, -1, 1, 1, -1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, -1, -1, 1, -1, -1, -1, 1, -1, -1, -1, 1, -1]

    #adding noise in channel
    input_data = add_noise(input_data)

    #find thepeaks in correlation
    peaks_val = find_peaks_in_corr(input_data, modulated_key )

    #find bits
    bits = peak_classifier(peaks_val)

    text = bits_to_string(bits)
    print(text)

