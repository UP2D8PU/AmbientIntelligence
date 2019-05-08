from flask import Flask, render_template, request, redirect
import time

from python.database import *
from python.waterprogram import *


app = Flask(__name__)


@app.route('/', methods = ['POST','GET'])
def hello_world():
    return render_template('index2.html', dict = sensor_values)

@app.route('/water1')
def water1():
    print("WATER1")
    return render_template('index2.html', dict = sensor_values)

@app.route('/water2')
def water2():
    print("WATER2")
    return render_template('index2.html', dict = sensor_values)

@app.route('/water3')
def water3():
    print("WATER3")
    return render_template('index2.html', dict = sensor_values)

@app.route('/water4')
def water4():
    print("WATER4")
    return render_template('index2.html', dict = sensor_values)

@app.route('/water5')
def water5():
    print("WATER5")
    return render_template('index2.html', dict = sensor_values)

@app.route('/water6')
def water6():
    print("WATER6")
    return render_template('index2.html', dict = sensor_values)

@app.route('/update')
def update():
    print("UPDATE")
    wp.retrieve_all_sensordata()
    while sensor_values["updated"]==0:
        time.sleep(0.5)
    return render_template('index2.html', dict = sensor_values)

if __name__ == '__main__':
    wp = WaterProgram()
    wp.run()
    app.run(debug = True)

    #do 0.0.0.0 so that we can log into this webpage
    # using another computer on the same network later
    #app.run(host='0.0.0.0')