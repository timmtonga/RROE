from __future__ import division
import time
import spidev

class CheckVoltage:
    def bitstring(self,n):
        s = bin(n)[2:]
        return '0'*(8-len(s)) + s

    def read_it(self,adc_channel=0, spi_channel=0):
        conn =spidev.SpiDev(0, spi_channel)
        conn.max_speed_hz = 1200000 #1.2MHz
        cmd = 128
        if adc_channel:
            cmd +=32
        reply_bytes = conn.xfer2([cmd, 0])
        conn.close()
        reply_bitstring = ''.join(self.bitstring(n) for n in reply_bytes)
        reply = reply_bitstring[5:15]
        return int(reply, 2) / 2**10

    def current_voltage(self):
        m = 0
        for x in range(10):
            x = self.read_it()
            time.sleep(0.1)
            m = m+ x

        avg = m/10
        average_voltage = avg * 16.5
        return average_voltage

    def getVoltage(self):
        min_voltage = 10.5
        raw_voltage =self.current_voltage()
        #Assume max_voltage is 13 volts. voltagePercent = (100*x)/2.5 ie x*40
        voltage_percent = (raw_voltage - min_voltage) *40
        if voltage_percent > 100:
            voltage_percent = 100
        return voltage_percent
