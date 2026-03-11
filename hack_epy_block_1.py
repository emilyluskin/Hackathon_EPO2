"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""
import numpy as np
from gnuradio import gr
import random

class blk(gr.sync_block):

    def __init__(self, seed=42, key_len=16):

        gr.sync_block.__init__(
            self,
            name="dsss_bpsk_receiver",
            in_sig=[np.float32],
            out_sig=None
        )

        self.seed = seed
        self.key_len = key_len

        # Barker preamble
        self.barker = [1,1,1,1,1,0,0,1,1,0,1,0,1]

        # PN key
        self.key = self.generate_key(seed, key_len)

        # build preamble
        self.preamble = self.build_preamble(self.barker, self.key)

        # PN for despreading
        self.pn_bpsk = self.bpsk_mod(self.key)

        # buffer
        self.buffer = []

    # -------------------------------------------------
    # utilities
    # -------------------------------------------------

    def generate_key(self, seed, key_len):
        random.seed(seed)
        return [random.randint(0,1) for _ in range(key_len)]

    def bpsk_mod(self, bits):
        return [1 if b==1 else -1 for b in bits]

    def dsss_spread(self, bits, key):
        bits = [int(b) for b in bits]
        repeated_bits = np.repeat(bits, len(key))
        repeated_key = np.tile(key, len(bits))
        return repeated_key ^ repeated_bits

    def build_preamble(self, preamble, key):
        spread = self.dsss_spread(preamble, key)
        return self.bpsk_mod(spread)

    # -------------------------------------------------
    # correlation / decoding
    # -------------------------------------------------

    def find_peaks_in_corr(self, data, pn):

        corr = np.correlate(data, pn)
        peaks = []

        for i in range(int(len(data)/len(pn))):
            peaks.append(corr[i*len(pn)])

        return peaks

    def peak_classifier(self, peaks):

        bits = []

        for v in peaks:
            if v > 0:
                bits.append(0)
            else:
                bits.append(1)

        return bits

    def bits_to_string(self, bits):

        chars = []

        for i in range(0,len(bits),8):

            byte = bits[i:i+8]

            if len(byte) < 8:
                break

            value = int("".join(map(str,byte)),2)
            chars.append(chr(value))

        return "".join(chars)

    # -------------------------------------------------
    # preamble detection
    # -------------------------------------------------

    def find_preamble(self, signal):

        if len(signal) < len(self.preamble):
            return None

        corr = np.correlate(signal, self.preamble, mode="valid")

        peak = np.argmax(np.abs(corr))

        energy = np.dot(self.preamble,self.preamble)

        if abs(corr[peak]) > 0.8*energy:
            return peak + len(self.preamble)

        return None

    # -------------------------------------------------
    # main receiver
    # -------------------------------------------------

    def work(self, input_items, output_items):

        in0 = input_items[0]

        self.buffer.extend(in0)

        end_of_pre = self.find_preamble(self.buffer)

        if end_of_pre is None:
            return len(in0)

        payload = self.buffer[end_of_pre:]

        # length field (8 bits)
        length_chips = 8 * self.key_len

        if len(payload) < length_chips:
            return len(in0)

        length_part = payload[:length_chips]

        peaks = self.find_peaks_in_corr(length_part,self.pn_bpsk)

        length_bits = self.peak_classifier(peaks)

        msg_len = int("".join(map(str,length_bits)),2)

        payload_bits = msg_len * 8
        payload_chips = payload_bits * self.key_len

        if len(payload) < length_chips + payload_chips:
            return len(in0)

        data_part = payload[length_chips:length_chips+payload_chips]

        peaks = self.find_peaks_in_corr(data_part,self.pn_bpsk)

        bits = self.peak_classifier(peaks)

        text = self.bits_to_string(bits)

        print("Decoded message:", text)

        # remove processed packet
        self.buffer = self.buffer[end_of_pre + length_chips + payload_chips:]

        return len(in0)