"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""
import numpy as np
import random
from gnuradio import gr


class blk(gr.sync_block):

    def __init__(self, message="hello", seed=42, key_len=16):

        gr.sync_block.__init__(
            self,
            name="dsss_bpsk_source",
            in_sig=None,
            out_sig=[np.float32]
        )

        self.message = message
        self.seed = seed
        self.key_len = key_len

        # Barker
        barker = [1,1,1,1,1,0,0,1,1,0,1,0,1]

        key = self.generate_key(seed, key_len)

        # ---------- HEADER ----------
        msg_bytes = message.encode("utf-8")
        length = len(msg_bytes)

        length_bits = format(length, "08b")

        payload_bits = "".join(format(b, "08b") for b in msg_bytes)

        bits = length_bits + payload_bits

        # ---------- DSSS ----------
        spread_bits = self.dsss_spread(bits, key)

        # ---------- BPSK ----------
        data_symbols = self.bpsk_mod(spread_bits)

        # ---------- PREAMBLE ----------
        preamble = self.build_preamble(barker, key)

        # ---------- FINAL PACKET ----------
        self.packet = np.array(self.final_signal(preamble, data_symbols), dtype=np.float32)

        self.index = 0

    # ------------------------------------------------

    def generate_key(self, seed, key_len):
        random.seed(seed)
        return [random.randint(0,1) for _ in range(key_len)]

    # ------------------------------------------------

    def dsss_spread(self, bits, key):

        bits_list = [int(b) for b in bits]

        repeated_bits = np.repeat(bits_list, len(key))
        repeated_key = np.tile(key, len(bits))

        spreaded = repeated_key ^ repeated_bits

        return spreaded

    # ------------------------------------------------

    def bpsk_mod(self, bits):
        return [1 if b==1 else -1 for b in bits]

    # ------------------------------------------------

    def build_preamble(self, preamble, key):

        spread = self.dsss_spread(preamble, key)
        return self.bpsk_mod(spread)

    # ------------------------------------------------

    def final_signal(self, preamble, data):

        return preamble + data

    # ------------------------------------------------

    def work(self, input_items, output_items):

        out = output_items[0]
        n = len(out)

        for i in range(n):

            out[i] = self.packet[self.index]

            self.index += 1

            if self.index >= len(self.packet):
                self.index = 0

        return n