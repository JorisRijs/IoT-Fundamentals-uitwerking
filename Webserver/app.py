from flask import Flask, render_template, request
app = Flask(__name__)
import sqlite3
import os.path

def getData():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "measurements.db")
    conn=sqlite3.connect(db_path)
    curs = conn.cursor()
    for row in curs.execute("SELECT * FROM measurements ORDER BY timestamp DESC LIMIT 1"):
        time = str(row[-1])
        temp = row[1]
        hum = row[2]
        pres = row[3]
    conn.close()
    return time, temp, hum, pres

# Main route
@app.route("/")
def index():
    time, temp, hum, pres = getData()
    templateData = {
            'time': time,
            'temp': temp,
            'hum': hum,
            'pres': pres
            }
    return render_template("index.html", **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)

