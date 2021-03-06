#!/usr/bin/env python
from scapy.all import *

class Sniffer:
    def __init__(self, interface):
        # Radiotap field specification
        self.radiotap_formats = {"TSFT": "Q", "Flags": "B", "Rate": "B",
                                 "Channel": "HH", "FHSS": "BB", "dBm_AntSignal": "b", "dBm_AntNoise": "b",
                                 "Lock_Quality": "H", "TX_Attenuation": "H", "dB_TX_Attenuation": "H",
                                 "dBm_TX_Power": "b", "Antenna": "B", "dB_AntSignal": "B",
                                 "dB_AntNoise": "B", "b14": "H", "b15": "B", "b16": "B", "b17": "B", "b18": "B",
                                 "b19": "BBB", "b20": "LHBB", "b21": "HBBBBBH", "b22": "B", "b23": "B",
                                 "b24": "B", "b25": "B", "b26": "B", "b27": "B", "b28": "B", "b29": "B",
                                 "b30": "B", "Ext": "B"}
        self.interface = interface
        self.running = False

    def should_exit(self, pkt):
        return self.running == False

    # callback(SSID, BSSID, RSSI)
    def start(self, callback):
        self.running = True

        def sniff_callback(pkt):
            if pkt.haslayer(Dot11) and pkt.type == 0 and pkt.subtype == 8:
                addr, rssi = self.parsePacket(pkt)
                try:
                    if addr is not None and rssi is not None and pkt.info is not None and pkt.info is not "":
                        # print "%d,%s,%s,%s" % (int(time.time()), pkt.info, addr, rssi)
                        callback(pkt.info, addr, rssi)
                except AttributeError:
                    pass
                    # print 'Weird attribute error'

        sniff(iface=self.interface, prn=sniff_callback, stop_filter=self.should_exit, store=0)

    def stop(self):
        self.running = False

    def parsePacket(self, pkt):
        if pkt.addr2 is not None:
            # check available Radiotap fields
            field, val = pkt.getfield_and_val("present")
            names = [field.names[i][0] for i in range(len(field.names)) if (1 << i) & val != 0]
            # check if we measured signal strength
            if "dBm_AntSignal" in names:
                # decode radiotap header
                fmt = "<"
                rssipos = 0
                for name in names:
                    # some fields consist of more than one value
                    if name == "dBm_AntSignal":
                        # correct for little endian format sign
                        rssipos = len(fmt) - 1
                    fmt = fmt + self.radiotap_formats[name]
                # unfortunately not all platforms work equally well and on my arm
                # platform notdecoded was padded with a ton of zeros without
                # indicating more fields in pkt.len and/or padding in pkt.pad
                decoded = struct.unpack(fmt, pkt.notdecoded[:struct.calcsize(fmt)])

                as_hex = ''.join(x.encode('hex') for x in pkt.notdecoded)
                rssi_hex = as_hex[44] + as_hex[45]
                rssi = struct.unpack("b", rssi_hex.decode('hex'))

                # return pkt.addr2, decoded[rssipos]
                return pkt.addr2, rssi[0]
        return None, None
