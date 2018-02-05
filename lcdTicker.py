from rpi_lcd import LCD
from time import sleep
import threading

lcd = LCD()

class LCDThread(threading.Thread):
    def __init__(self, temp, humid, light, soil, water):
        threading.Thread.__init__(self)
        self.temperature = temp
        self.humidity = humid
        self.lightlvl = light
        self.moisture = soil
        self.waterlvl = water
        self.message = ""

    def changeValues(self, temp, humid, light, soil, water):
        self.temperature = temp
        self.humidity = humid
        self.lightlvl = light
        self.moisture = soil
        self.waterlvl = water

    def setMessage(self, message):
        lcd.text(message, 2)
        self.message = message

    def getMessage(self):
        return self.message

    def run(self):
        while True:
            try:
                lcd.text('Temp:{:.1f}C'.format(self.temperature), 1)
                sleep(3)
                lcd.text('Humidity:{:.1f}%'.format(self.humidity), 1)
                sleep(3)
                lcd.text('Light Lvl:{:.1f}'.format(self.lightlvl), 1)
                sleep(3)
                lcd.text('Moisture:{:.1f}'.format(self.moisture), 1)
                sleep(3)
                lcd.text('Water Lvl:{:.1f}'.format(self.waterlvl), 1)
                sleep(3)
            except Exception as e:
                print(e.message)
