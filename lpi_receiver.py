import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import random
from trans_poc import ascii_mess_val, generate_key, dsss_spread, bpsk_mod, final_signal, build_preamble

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
    print("corr",corr)
    peaks_val = [corr[i*len(modulated_key)] for i in range(int(len(input_data)/len(modulated_key)))]
    print("peaks val",peaks_val)

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

def last_idx_preamble(signal,preamble):
    
    corr = np.correlate(signal, preamble)
    start_idx_preamble = np.argmax(corr)
        # 3. יצירת הגרף
    plt.figure(figsize=(10, 6))

    # # ציור ערכי הקורלציה
    # plt.plot(corr, label='Correlation Value', color='blue', alpha=0.7)

    # # סימון נקודת המקסימום (המיקום המזוהה)
    # plt.scatter(start_idx_preamble, corr[start_idx_preamble], color='red', s=50, zorder=5, 
    #             label=f'Peak found at index {start_idx_preamble}')
    # plt.axvline(x=start_idx_preamble, color='red', linestyle='--', alpha=0.5)
    # plt.title('Correlation between Signal and Preamble')
    # plt.xlabel('Signal Index')
    # plt.ylabel('Correlation Amplitude')
    # plt.legend()
    # plt.grid(True, linestyle=':', alpha=0.6)

    # plt.tight_layout()
    # plt.show()

    return (start_idx_preamble +len(preamble))

if __name__ == "__main__":

    barker_13_bits = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]

    sps = 1
    # Create the key
    seed = 42
    key_len = 8
    key = generate_key(seed,key_len)

    # Perform upsampling according to the sps - for the correlation
    upsampled_key = np.repeat(key, sps)

    #bpsk modulation
    modulated_key= bpsk_mod(upsampled_key)

    input_data = [-1, -1, 1, -1, 1, 1, -1, 1, 1, 1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, -1, -1, 1, -1, -1, -1, 1, -1, -1, -1, 1, -1]

    #build preamble
    spreaded_bpsk_preamble = build_preamble(barker_13_bits,key)

    #add preamble to the signal
    signal_trs = final_signal(spreaded_bpsk_preamble,input_data )

    #adding noise in channel
    input_data = add_noise(signal_trs)

    #find preamble

    end_of_pre = last_idx_preamble(input_data, spreaded_bpsk_preamble)
    input_data = input_data[end_of_pre:]

    #find thepeaks in correlation
    peaks_val = find_peaks_in_corr(input_data, modulated_key )

    #find bits
    bits = peak_classifier(peaks_val)

    text = bits_to_string(bits)
    print(text)

