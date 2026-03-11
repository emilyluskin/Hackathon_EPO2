import numpy as np
import matplotlib.pyplot as plt

from trans_poc import ascii_mess_val, generate_key, dsss_spread, bpsk_mod, final_signal, build_preamble
from lpi_receiver import add_noise, find_peaks_in_corr, peak_classifier, bits_to_string,last_idx_preamble

# message
message = "hidden message"

#barker
barker_13_bits = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]

# TRANSMITTER
bits = ascii_mess_val(message)
bits_list = [int(b) for b in bits]

seed = 42
key_len = 1024
key = generate_key(seed, key_len)
spreaded_bits = dsss_spread(bits, key)
modulated_data = bpsk_mod(spreaded_bits)
preamble = build_preamble(barker_13_bits, key)#bpsk and spreaded
signal = final_signal(preamble, modulated_data)

# CHANNEL
rx_signal = add_noise(signal)

# RECEIVER

#find preamble
end_of_pre = last_idx_preamble(rx_signal, preamble)
rx_signal = rx_signal[end_of_pre:]

pn = np.array(key)
pn_bpsk = bpsk_mod(pn)
corr = np.correlate(rx_signal, pn_bpsk, mode='full')

peaks = find_peaks_in_corr(rx_signal, pn_bpsk)

decoded_bits = peak_classifier(peaks)

decoded_text = bits_to_string(decoded_bits)

print("Decoded bits:", decoded_bits)
print("Decoded message:", decoded_text)

# PLOTS
plt.figure(figsize=(12,12))

plt.subplot(6,1,1)
plt.title("Original bits")
plt.stem(bits_list)

plt.subplot(6,1,2)
plt.title("Spread bits (DSSS)")
plt.plot(spreaded_bits)

plt.subplot(6,1,3)
plt.title("BPSK Modulated Signal")
plt.plot(modulated_data)

plt.subplot(6,1,4)
plt.title("Received Signal with Noise")
plt.plot(rx_signal)

plt.subplot(6,1,5)
plt.title("Correlation Output (peaks over noise)")

plt.plot(corr, label="Correlation")
chip_len = len(pn_bpsk)
peak_positions = [i*chip_len for i in range(len(peaks))]
peak_values = [corr[p] for p in peak_positions]
plt.scatter(peak_positions, peak_values, color='red', label="Detected Peaks")
plt.legend()
plt.grid()

plt.subplot(6,1,6)
plt.title("Decoded Bits")
plt.stem(decoded_bits)

plt.tight_layout()
plt.show()
