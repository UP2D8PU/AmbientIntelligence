from flask import Flask, render_template, request, redirect
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

from python.database import *
from python.waterprogram import *


app = Flask(__name__)

@app.route('/', methods = ['POST','GET'])
def init():

    if request.method=='GET':
        type= [plants[garden[0]["type"]]["name"],plants[garden[1]["type"]]["name"],plants[garden[2]["type"]]["name"],plants[garden[3]["type"]]["name"],plants[garden[4]["type"]]["name"],plants[garden[5]["type"]]["name"]]
        return render_template('index.html', dict = sensor_values, garden = garden, plants_dict = plants, type=type)

    else:

        #For plant 1
        if request.form['button'] == "water1":
            wp.water_plant(garden[0]["angle"], plants[garden[0]["type"]]["water quantity"])
        elif request.form['button'] == "add1":
            value = int(request.form['add_plant1'])
            if (value !=0):
                garden[0]["type"] = value
        elif request.form['button'] == "delete1":
                garden[0]["type"] = 0

        #For plant 2
        if request.form['button'] == "water2":
            wp.water_plant(garden[1]["angle"], plants[garden[1]["type"]]["water quantity"])
        elif request.form['button'] == "add2":
            value = int(request.form['add_plant2'])
            if (value !=0):
                garden[1]["type"] = value
        elif request.form['button'] == "delete2":
            garden[1]["type"] = 0


        #For plant 3
        if request.form['button'] == "water3":
            wp.water_plant(garden[2]["angle"], plants[garden[2]["type"]]["water quantity"])
        elif request.form['button'] == "add3":
            value = int(request.form['add_plant3'])
            if (value !=0):
                garden[2]["type"] = value
        elif request.form['button'] == "delete3":
            garden[2]["type"] = 0


        #For plant 4
        if request.form['button'] == "water4":
            wp.water_plant(garden[3]["angle"], plants[garden[3]["type"]]["water quantity"])
        elif request.form['button'] == "add4":
            value = int(request.form['add_plant4'])
            if (value !=0):
                garden[3]["type"] = value
        elif request.form['button'] == "delete4":
            garden[3]["type"] = 0


        #For plant 5
        if request.form['button'] == "water5":
            wp.water_plant(garden[4]["angle"], plants[garden[4]["type"]]["water quantity"])
        elif request.form['button'] == "add5":
            value = int(request.form['add_plant5'])
            if (value !=0):
                garden[4]["type"] = value
        elif request.form['button'] == "delete5":
            garden[4]["type"] = 0


        #For plant 6
        if request.form['button'] == "water6":
            wp.water_plant(garden[5]["angle"], plants[garden[5]["type"]]["water quantity"])
        elif request.form['button'] == "add6":
            value = int(request.form['add_plant6'])
            if (value !=0):
                garden[5]["type"] = value
        elif request.form['button'] == "delete6":
            garden[5]["type"] = 0


        type= [plants[garden[0]["type"]]["name"],plants[garden[1]["type"]]["name"],plants[garden[2]["type"]]["name"],plants[garden[3]["type"]]["name"],plants[garden[4]["type"]]["name"],plants[garden[5]["type"]]["name"]]
        return render_template('index.html', dict = sensor_values, garden = garden, plants_dict = plants, type=type)

def sensordata():
    wp.retrieve_all_sensor_data()
    timeout_milliseconds(500)
    wp.evaluate_sensor_data()

def dailywater():
    wp.daily_water()

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
    sched.add_job(sensordata,'interval',minutes=2)
    sched.add_job(dailywater,'interval',hours=24)
    sched.start()

    #Register the function to be called on exit
    atexit.register(close_running_threads)

    app.run()



    #do 0.0.0.0 so that we can log into this webpage
    # using another computer on the same network later
    #app.run(host='0.0.0.0')