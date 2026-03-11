import numpy as np
import matplotlib.pyplot as plt
import uhd  # ודאי שמותקן: pip install uhd

from trans_poc import ascii_mess_val, generate_key, dsss_spread, bpsk_mod, final_signal, build_preamble
from lpi_receiver import find_peaks_in_corr, peak_classifier, bits_to_string, last_idx_preamble

# --- הגדרות חומרה ---
FS = 1e6        # קצב דגימה (1MHz)
FREQ = 2.45e9   # תדר מרכזי
TX_GAIN = 50    # עוצמת שידור
RX_GAIN = 40    # הגבר קליטה

# --- פונקציות עזר ל-USRP ---

def send_and_receive_usrp(tx_data, fs, freq):
    # חיבור למכשיר (B210 מזוהה כ-b200)
    usrp = uhd.usrp.MultiUSRP("type=b200")
    
    # הגדרות ערוץ שידור (TX)
    usrp.set_tx_rate(fs, 0)
    usrp.set_tx_freq(uhd.libpyuhd.types.tune_request(freq), 0)
    usrp.set_tx_gain(TX_GAIN, 0)
    
    # הגדרות ערוץ קליטה (RX)
    usrp.set_rx_rate(fs, 0)
    usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(freq), 0)
    usrp.set_rx_gain(RX_GAIN, 0)
    
    # הכנת הסטרימרים
    st_args = uhd.usrp.StreamArgs("fc32", "sc16")
    tx_streamer = usrp.get_tx_stream(st_args)
    rx_streamer = usrp.get_rx_stream(st_args)
    
    # הכנת הנתונים למשלוח (חובה Complex64)
    tx_samples = tx_data.astype(np.complex64)
    
    # קליטה של פי 2 יותר דגימות כדי לא לפספס את תחילת ההודעה
    num_rx_samples = len(tx_samples) * 3
    rx_buffer = np.zeros(num_rx_samples, dtype=np.complex64)
    
    # פקודת קליטה
    metadata_rx = uhd.types.RXMetadata()
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.num_done)
    stream_cmd.num_samples = num_rx_samples
    stream_cmd.stream_now = True
    rx_streamer.issue_stream_cmd(stream_cmd)
    
    # שידור
    metadata_tx = uhd.types.TXMetadata()
    tx_streamer.send(tx_samples, metadata_tx)
    
    # משיכת הדגימות שנקלטו מהאוויר
    rx_streamer.recv(rx_buffer, metadata_rx)
    
    return rx_buffer

# --- תחילת התוכנית הראשית ---

# message
message = "hi"

# barker
barker_13_bits = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]

# TRANSMITTER
bits = ascii_mess_val(message)
bits_list = [int(b) for b in bits]

seed = 42
key_len = 64

key = generate_key(seed, key_len)
spreaded_bits = dsss_spread(bits, key)
modulated_data = bpsk_mod(spreaded_bits)
preamble = build_preamble(barker_13_bits, key)
signal = final_signal(preamble, modulated_data)

# --- מעבר לחומרה (במקום add_noise) ---
print("Starting Over-the-Air Transmission...")
rx_signal_raw = send_and_receive_usrp(signal, FS, FREQ)

# המרה לערכים ממשיים (אם הפענוח שלך מבוסס על BPSK ממשי)
# בשידור חי תהיה פאזה, אז נשתמש בערך המוחלט או בחלק הממשי אחרי סנכרון פאזה
rx_signal = np.real(rx_signal_raw) 

# RECEIVER
# חיפוש ה-Preamble בתוך האות שנקלט מהאוויר
end_of_pre = last_idx_preamble(rx_signal, preamble)
rx_signal_sliced = rx_signal[end_of_pre:]

pn = np.array(key)
pn_bpsk = bpsk_mod(pn)
# חשוב: הקורלציה צריכה להתבצע על האות שנחתך
corr = np.correlate(rx_signal_sliced, pn_bpsk, mode='full')

peaks = find_peaks_in_corr(rx_signal_sliced, pn_bpsk)
decoded_bits = peak_classifier(peaks)
decoded_text = bits_to_string(decoded_bits)

print("Decoded bits:", decoded_bits)
print("Decoded message:", decoded_text)

# --- PLOTS ---
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
plt.title("Received Signal from USRP (Real Part)")
plt.plot(rx_signal)

plt.subplot(6,1,5)
plt.title("Correlation Output")
plt.plot(corr)

plt.subplot(6,1,6)
plt.title("Decoded Bits")
if len(decoded_bits) > 0:
    plt.stem(decoded_bits)

plt.tight_layout()
plt.show()
