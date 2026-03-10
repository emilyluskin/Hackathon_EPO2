import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import random

def bpsk_mod(bits):
    bits = np.array(bits)
    symbols = 2*bits - 1
    return symbols


# bits = [1,1,0,1,0,0,1]
# print(bpsk_mod(bits))

sps = 1
# Create the pn sequence
random.seed(42)
pn_seuquence = [random.randint(0, 1) for _ in range(4)]
print(pn_seuquence)
# Perform upsampling according to the sps and perform BPSK modulation
upsampled_pn_sequence = np.repeat(pn_seuquence, sps) # this upsampling is correct only for a rectangular pulse shaper!
#print(upsampled_pn_sequence)
modulated_upsampled_pn_sequence = bpsk_mod(upsampled_pn_sequence)
print(modulated_upsampled_pn_sequence)
input_data = [-1, -1, 1, -1, 1, 1, -1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, -1, -1, 1, -1, -1, -1, 1, -1, -1, -1, 1, -1]
noise = np.random.normal(0, 1, len(input_data))
input_data = input_data + noise
corr = np.correlate(input_data, modulated_upsampled_pn_sequence)
print(corr)
print(len(corr))
#peaks, properties = signal.find_peaks(corr)
peaks_val = [corr[i*len(modulated_upsampled_pn_sequence)] for i in range(int(len(input_data)/len(modulated_upsampled_pn_sequence)))]
print(peaks_val)
#bits = list(input_data)[signal.find_peaks(corr)]
bits=-2*np.ones(len(peaks_val), dtype=int)
for i in range(len(peaks_val)):
    if peaks_val[i] > 0:
        bits[i] = 0
    if peaks_val[i] <= 0:
        bits[i] = 1
bits = list(bits)
print("bits", bits)
text = ''.join(chr(int(''.join(map(str, bits[i:i+8])), 2)) for i in range(0, len(bits), 8))
print(text)

