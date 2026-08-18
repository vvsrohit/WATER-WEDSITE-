from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)


def get_db():
    return sqlite3.connect(
        os.path.join(BASE_DIR, "sensor_data.db")
    )


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

        return "Data received and stored", 200

    return render_template("index.html")


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
