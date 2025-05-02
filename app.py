from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

# === Initialisation base de données ===
def init_db():
    conn = sqlite3.connect('iot.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS measures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            pir INTEGER,
            gas INTEGER,
            light INTEGER,
            current REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# === Route d'envoi de mesures ===
@app.route('/upload', methods=['POST'])
def upload():
    data = request.json
    if not data:
        return jsonify({'status': 'fail', 'reason': 'No JSON'}), 400

    timestamp = datetime.now().isoformat()
    conn = sqlite3.connect('iot.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO measures (timestamp, temperature, humidity, pir, gas, light, current)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        timestamp,
        data.get('temp'),
        data.get('hum'),
        data.get('pir'),
        data.get('gas'),
        data.get('light'),
        data.get('curr')
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

# === Route d'affichage de la dernière mesure ===
@app.route('/last', methods=['GET'])
def last():
    conn = sqlite3.connect('iot.db')
    c = conn.cursor()
    c.execute('SELECT * FROM measures ORDER BY id DESC LIMIT 1')
    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({
            'timestamp': row[1],
            'temp': row[2],
            'hum': row[3],
            'pir': row[4],
            'gas': row[5],
            'light': row[6],
            'curr': row[7],
        })
    else:
        return jsonify({'status': 'no_data'})

# === Démarrage serveur ===
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
