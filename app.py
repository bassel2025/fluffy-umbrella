from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "sensors_data.db"

# Init DB
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                pir INTEGER,
                temperature REAL,
                humidity REAL,
                gas INTEGER,
                light INTEGER,
                current REAL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT,
                value TEXT
            )
        ''')

@app.route("/")
def home():
    return "✅ SmartHome API en ligne !"

@app.route("/upload", methods=["POST"])
def upload_data():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "Aucune donnée reçue"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            INSERT INTO sensor_data (timestamp, pir, temperature, humidity, gas, light, current)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow().isoformat(),
            data.get("pir"),
            data.get("temperature"),
            data.get("humidity"),
            data.get("gas"),
            data.get("light"),
            data.get("current")
        ))

    return jsonify({"status": "success"}), 200

@app.route("/commands", methods=["GET"])
def get_commands():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute('SELECT key, value FROM commands')
        commands = {row[0]: row[1] for row in cursor.fetchall()}
    return jsonify(commands)

@app.route("/commands", methods=["POST"])
def set_command():
    data = request.get_json()
    if not data or "key" not in data or "value" not in data:
        return jsonify({"status": "error", "message": "Commande invalide"}), 400

    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("REPLACE INTO commands (id, key, value) VALUES ((SELECT id FROM commands WHERE key = ?), ?, ?)",
                     (data["key"], data["key"], data["value"]))
    return jsonify({"status": "command updated"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
