from flask import Flask, render_template, request, redirect
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
import time
from threading import Thread

from python.database import *
from python.waterprogram import *


app = Flask(__name__)


@app.route('/', methods = ['POST','GET'])
def hello_world():
    type= [plants[garden[0]["type"]]["name"],plants[garden[1]["type"]]["name"],plants[garden[2]["type"]]["name"],plants[garden[3]["type"]]["name"],plants[garden[4]["type"]]["name"],plants[garden[5]["type"]]["name"]]
    return render_template('index2.html', dict = sensor_values, garden = garden, plants_dict = plants, type=type)

@app.route('/water1',methods=['POST'])
def water1():
    projectpath = request.form['projectFilepath']
    print(projectpath)
    print("WATER1")
    return render_template('index2.html', dict = sensor_values, garden = garden, plants_dict = plants)

@app.route('/water2')
def water2():
    if request.form['button'] == "water":
        print("Water plant 2")
    if request.form['button'] == "add":
        value = int(request.form['tvalue'])
        garden[2]["type"] = value
    type= [plants[garden[0]["type"]]["name"],plants[garden[1]["type"]]["name"],plants[garden[2]["type"]]["name"],plants[garden[3]["type"]]["name"],plants[garden[4]["type"]]["name"],plants[garden[5]["type"]]["name"]]
    return render_template('index2.html', dict = sensor_values, garden = garden, plants_dict = plants, types=type)


@app.route('/water3')
def water3():
    print("WATER3")
    return render_template('index2.html', dict = sensor_values, plants_dict = plants)

@app.route('/water4')
def water4():
    print("WATER4")
    return render_template('index2.html', dict = sensor_values, plants_dict = plants)

@app.route('/water5')
def water5():
    print("WATER5")
    return render_template('index2.html', dict = sensor_values, plants_dict = plants)

@app.route('/water6')
def water6():
    print("WATER6")
    return render_template('index2.html', dict = sensor_values, plants_dict = plants)

@app.route('/update')
def update():
    print("UPDATE")
    wp.retrieve_all_sensor_data()
    while sensor_values["updated"]==0:
        time.sleep(0.5)
    return render_template('index2.html', dict = sensor_values, plants_dict = plants)

#@app.before_first_request
#def activate_job():
#    thread = threading.Thread(target=wp.run())
#    thread.start()

def sensordata():
    wp.retrieve_all_sensor_data()
    print("Retrieve all sensordata!")
    time.sleep(1)
    wp.evaluate_sensor_data()
    print("Evaluate sensor_values")

def dailywater():
    wp.daily_water()
    print("Daily water given")

#defining function to run on shutdown
def close_running_threads():
    wp.exit_event.set()
    wp.n_received_tokens.release()
    print("Exiting...")
    for t in wp.threads:
        t.join()
    print ("Threads complete, ready to finish")

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
if __name__ == '__main__':
    wp = WaterProgram()
    sched = BackgroundScheduler(daemon=True, job_defaults=job_defaults)
    sched.add_job(sensordata,'interval',minutes=1)
    sched.add_job(dailywater,'interval',hours=24)
    sched.start()

    #Register the function to be called on exit
    atexit.register(close_running_threads)

    app.run()



    #do 0.0.0.0 so that we can log into this webpage
    # using another computer on the same network later
    #app.run(host='0.0.0.0')