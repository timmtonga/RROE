from __future__ import division
import spidev

from random import randint
class CheckVoltage:
    def bitstring(n):
        s = bin(n)[2:]
        return '0'*(8-len(s)) + s

    def read(self,adc_channel=0, spi_channel=0):
        conn =spidev.SpiDev(0, spi_channel)
        conn.max_speed_hz = 1200000 #1.2MHz
        cmd = 128
        if adc_channel:
            cmd +=32
        reply_bytes = conn.xfer2([cmd, 0])
        reply_bitstring = ''.join(self.bitstring(n) for n in reply_bytes)
        reply = reply_bitstring[5:15]
        return int(reply, 2) / 2**10

    def getVoltage(self):
        raw_voltage =self.read()
        voltage_percent = ((raw_voltage*25) - 10) *50
        if voltage_percent > 100:
            voltage_percent = 100
        return voltage_percent



# Installing spidev:
#  cd py-spidev-master/
#  sudo python setup.py install

