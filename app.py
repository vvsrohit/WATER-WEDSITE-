from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime

app = Flask(__name__)


def get_db():
    return sqlite3.connect("sensor_data.db")


def init_db():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soil INTEGER NOT NULL,
            temperature REAL NOT NULL,
            humidity REAL NOT NULL,
            timestamp DATETIME NOT NULL
        )
    """)

    db.commit()
    db.close()


# Receive data from ESP32
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        data = request.get_json()

        soil = data["soil"]
        temperature = data["temperature"]
        humidity = data["humidity"]

        db = get_db()

        db.execute("""
            INSERT INTO sensor_data
            (soil, temperature, humidity, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            soil,
            temperature,
            humidity,
            datetime.now()
        ))

        db.commit()
        db.close()

        print("Data stored:", data)

        return "Data received and stored", 200

    return render_template("index.html")


# Return latest 50 readings
@app.route("/data")
def get_data():

    db = get_db()

    cursor = db.execute("""
        SELECT id, soil, temperature, humidity, timestamp
        FROM sensor_data
        ORDER BY id DESC
        LIMIT 50
    """)

    rows = cursor.fetchall()
    db.close()

    data = []

    for row in rows:
        data.append({
            "id": row[0],
            "soil": row[1],
            "temperature": row[2],
            "humidity": row[3],
            "timestamp": row[4]
        })

    return jsonify(data)


init_db()

app.run(host="0.0.0.0", port=5000)