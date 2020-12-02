
import RPi.GPIO as GPIO
class CheckChargeState:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(24,GPIO.IN)

    def getState(self):
        state = GPIO.input(24)
        if state:
            return True
        else:
            return False
