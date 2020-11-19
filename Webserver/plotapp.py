from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
from flask import Flask, render_template, send_file, make_response, request
app = Flask(__name__)
import sqlite3
import os
import pyodbc
import settings as conf


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "measurements.db")



# Retrieve LAST data from database
def getLastData():
    with sqlite3.connect(db_path) as conn: 
        curs = conn.cursor()
        for row in curs.execute("SELECT * FROM measurements ORDER BY timestamp DESC LIMIT 1"):
            time = str(row[-1])
            temp = row[1]
            hum = row[2]
            pres = row[3] 
    return time, temp, hum, pres

def getHistData (numSamples):
    with sqlite3.connect(db_path) as conn: 
        curs = conn.cursor()
        curs.execute("SELECT * FROM measurements ORDER BY timestamp DESC LIMIT "+str(numSamples))
        data = curs.fetchall()
        dates = []
        temps = []
        hums = []
        pressures = []
        for row in reversed(data):
            dates.append(row[-1])
            temps.append(row[1])
            hums.append(row[2])
            pressures.append(row[3])
    return dates, temps, hums, pressures

def maxRowsTable():
    with sqlite3.connect(db_path) as conn: 
        curs = conn.cursor()
        for row in curs.execute("select COUNT(temp) from  measurements"):
            maxNumberRows=row[0]
        
    return maxNumberRows

# define and initialize global variables
global numSamples
numSamples = maxRowsTable()
if (numSamples > 101):
    numSamples = 100

# main route
@app.route("/")
def index():
    time, temp, hum, pres = getLastData()
    templateData = {
  	'time'	: time,
	'temp'	: temp,
   	'hum'	: hum,
        'pres'  : pres,
      	'numSamples': numSamples
    }
    return render_template('index.html', **templateData)

@app.route('/', methods=['POST'])
def my_form_post():
    global numSamples
    numSamples = int (request.form['numSamples'])
    numMaxSamples = maxRowsTable()
    if numSamples > numMaxSamples:
        numSamples = (numMaxSamples-1)
    time, temp, hum, pres = getLastData()
    templateData = {
	  	'time'	: time,
      		'temp'	: temp,
      		'hum'	: hum,
                'pres'  : pres,
      		'numSamples'	: numSamples
	}
    return render_template('index.html', **templateData)

@app.route('/plot/temp')
def plot_temp():
    times, temps, hums, pressures = getHistData(numSamples)
    ys = temps
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Temperature [C]")
    axis.set_xlabel("Samples")
    axis.grid(True)
    xs = range(numSamples)
    axis.plot(xs, ys)
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

@app.route('/plot/hum')
def plot_hum():
	times, temps, hums, pressures = getHistData(numSamples)
	ys = hums
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Humidity [%]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

@app.route('/plot/pres')
def plot_pres():
	times, temps, hums , pressures= getHistData(numSamples)
	ys = pressures
	fig = Figure()
	axis = fig.add_subplot(1, 1, 1)
	axis.set_title("Pressure [hPA]")
	axis.set_xlabel("Samples")
	axis.grid(True)
	xs = range(numSamples)
	axis.plot(xs, ys)
	canvas = FigureCanvas(fig)
	output = io.BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = 'image/png'
	return response

if __name__ == "__main__":
   app.run(host='0.0.0.0', port=443, debug=False, ssl_context=('cert.pem', 'key.pem'))
