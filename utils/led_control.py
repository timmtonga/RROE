import RPi.GPIO as GPIO


class led_control:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(23, GPIO.OUT)

    def turn_led_off(self):
        GPIO.output(23, GPIO.LOW)

    def turn_led_on(self):
        GPIO.output(23, GPIO.HIGH)
