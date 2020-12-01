from utils.charging_checker import CheckChargeState
from utils.voltage_checker import CheckVoltage
from datetime import datetime
import time
import os


def initialize_test():
    while True:
        # Get voltage

        voltage = CheckVoltage().get_voltage()

        if 10 < voltage < 12:
            msg = "At %s , system voltage was %s \n" % (datetime.now().strftime("%d-%b %H:%M"), str(voltage))
            log(msg)
        elif voltage < 10:
            # shutdown
            msg = "At %s , system voltage was %s \n Shutdown ... \n" % (datetime.now().strftime("%d-%b %H:%M"), str(voltage))
            log(msg)
            os.system('sudo shutdown now')
        else:
            log(msg)
            print_label(voltage)
        time.sleep(600)


def log(message):
    f = open("battery_test.log", "a+")
    f.write(message)
    f.close()


def print_label(voltage):
    label_file = open("/tmp/test_order.lbl", "w+")
    label_file.write("N\nq406\nQ203,027\nZT\n")
    label_file.write('A5,10,0,1,1,2,N,"Voltage: %s"\n' % str(voltage))
    label_file.write('b5,70,P,386,80,"%s$"\n' % '~'.join([str(voltage), datetime.now().strftime("%d-%b %H:%M")]))
    label_file.write('A20,170,0,1,1,2,N,"%s" \n' % datetime.now().strftime("%d-%b %H:%M"))
    label_file.write("P1\n")
    label_file.close()
    os.system('sudo sh ~/print.sh /tmp/test_order.lbl')


if __name__ == '__main__':
    initialize_test()
