import lcdTicker
import time
from gpiozero import MCP3008
import Adafruit_DHT
from time import sleep
import threading


class monitor(threading.Thread):
    def __init__(self, dbconn):
        threading.Thread.__init__(self)
        self.monitor = True
        self.db = dbconn
        self.cursor = self.db.cursor()
        self.lightSensor = MCP3008(channel=0)
        self.waterLevelSensor = MCP3008(channel=1)
        self.soilSensor = MCP3008(channel=2)
        Adafruit_DHT.read_retry(11, 19)

        # new thread for LCD
        self.ticker = lcdTicker.LCDThread(0, 0, 0, 0, 0)
        self.ticker.start()

    def setState(self, state):
        self.monitor = state

    def getState(self):
        return self.monitor

    def getMessage(self):
        return self.ticker.getMessage()

    def setMessage(self, message):
        self.ticker.setMessage(message)

    def getLight(self):
        return self.lightSensor.value

    def getMoisture(self):
        return self.soilSensor.value

    def getWaterLevel(self):
        return self.waterLevelSensor.value

    def getTemp(self):
        humidity, temperature = Adafruit_DHT.read_retry(11, 19)
        return temperature

    def getHumdity(self):
        humidity, temperature = Adafruit_DHT.read_retry(11, 19)
        return humidity

    def getHistory(self):
        list = []
        historyCursor = self.db.cursor()
        historyCursor.execute("SELECT * FROM plantmonitor ORDER BY STR_TO_DATE(recorded_time, '%d-%m-%Y %H:%M:%S') DESC LIMIT 50")
        for (recorded_time, temperature, humidity, light_level, moisture, water_level) in historyCursor:
            dataset = {
                "time": recorded_time,
                "temperature": temperature,
                "humidity": humidity,
                "lightlvl": light_level,
                "moisture": moisture,
                "waterlvl": water_level
            }
            list.append(dataset)
        return list

    def run(self):
        while True:
            while self.monitor:

                print("Reading sensor values...")
                humidity, temperature = Adafruit_DHT.read_retry(11, 19)
                lightVal = self.lightSensor.value
                soilVal = self.soilSensor.value
                waterVal = self.waterLevelSensor.value

                noError = True

                if humidity is None or temperature is None:
                    print("DHT_11: Error reading temp/humidity")
                    noError = False
                if lightVal is None:
                    print("LDR: Error reading light levels")
                    noError = False
                if soilVal is None:
                    print("YL-69: Error reading soil moisture")
                    noError = False
                if waterVal is None:
                    print("WLS: Error reading water levels")
                    noError = False

                if noError:
                    try:
                        print("T:" + str(temperature) + " L:" + str(lightVal) + " M:" + str(soilVal) + " W:" + str(waterVal))
                        self.ticker.changeValues(temperature, humidity, lightVal, soilVal, waterVal)
                        sql = "INSERT into plantmonitor (recorded_time,temperature,humidity,light_level,moisture,water_level) VALUES (\"%s\",%f,%f,%f,%f,%f)" % (
                            str(time.strftime("%d-%m-%Y %H:%M:%S")), temperature, humidity, lightVal, soilVal, waterVal)
                        self.cursor.execute(sql)
                        self.db.commit()
                    except Exception as e:
                        print(e.message)
                sleep(30)
        sleep(10)
