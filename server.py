from flask import Flask, render_template, jsonify, request, json
import MySQLdb
import plantMonitor
from gevent.pywsgi import WSGIServer

app = Flask(__name__)

startupsuccessful = True

print('Plant Monitor v1.0 Starting Up...')
try:
    db = MySQLdb.connect("localhost", "root", "dmitiot", "plantmonitor")
    curs = db.cursor()
    print("Successfully connected to database!")
except:
    print("Error connecting to mySQL database")
    startupsuccessful = False

if startupsuccessful:
    print("Starting plant monitor thread...")
    plantMonitorer = plantMonitor.monitor(db)
    plantMonitorer.start()


@app.route("/")
def index():
    humidity = plantMonitorer.getHumdity()
    temperature = plantMonitorer.getTemp()
    lightVal = plantMonitorer.getLight()
    soilVal = plantMonitorer.getMoisture()
    waterVal = plantMonitorer.getWaterLevel()

    tempAdvisory = "GOOD"
    lightAdvisory = "GOOD"
    moistureAdvisory = "GOOD"
    waterAdvisory = "GOOD"

    if temperature > 28 or temperature < 25:
        tempAdvisory = "Recommended Temperature: 25-28 C"
    if lightVal > 0.35:
        lightAdvisory = "Insufficient light"
    if soilVal > 0.5:
        moistureAdvisory = "Soil is very dry"
    if waterVal > 0.3:
        waterAdvisory = "Empty water collection plate"

    templateData = {
        'temperature': str(temperature),
        'tempAdvisory': tempAdvisory,
        'humidity': str(humidity),
        'lightLevel': str(lightVal),
        'lightAdvisory': lightAdvisory,
        'moisture': str(soilVal),
        'moistureAdvisory': moistureAdvisory,
        'waterLevel': str(waterVal),
        'waterAdvisory': waterAdvisory
    }
    return render_template('index.html', **templateData)


@app.route("/getHistory")
def getHistory():
    return jsonify(plantMonitorer.getHistory())


@app.route("/updateMessage", methods=['POST'])
def updateMessage():
    print("Updating message...")
    data = request.json['message']
    print(str(data))
    plantMonitorer.setMessage(str(data))
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getMessage")
def getMessage():
    messageObject = {
        "message": plantMonitorer.getMessage()
    }
    return jsonify(messageObject)


@app.route("/getState")
def getState():
    stateObject = {
        "state": plantMonitorer.getState()
    }
    return jsonify(stateObject)


@app.route("/setState", methods=['POST'])
def setState():
    data = request.json['state']
    print(str(data))
    plantMonitorer.setState(data)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__' and startupsuccessful:
    try:
        print("Starting web server")
        http_server = WSGIServer(('0.0.0.0', 8001), app)
        app.debug = True
        print("Web server started")
        http_server.serve_forever()
    except:
        print("Exception")
