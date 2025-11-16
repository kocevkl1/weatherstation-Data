import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database setup
def get_db():
    conn = sqlite3.connect('readings.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table if it doesn't exist
def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
init_db()

# Endpoint to receive JSON data
@app.route('/add_reading', methods=['POST'])
def add_reading():
    data = request.get_json()
    value = data.get('value')
    with get_db() as conn:
        conn.execute('INSERT INTO readings (value) VALUES (?)', (value,))
    return jsonify({"status": "success"}), 201

# Endpoint to return the latest reading
@app.route('/latest_reading', methods=['GET'])
def latest_reading():
    with get_db() as conn:
        reading = conn.execute('SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1').fetchone()
    return jsonify(dict(reading)) if reading else jsonify({"error": "No readings found"}), 404

# Endpoint to return 3 days of history
@app.route('/history', methods=['GET'])
def history():
    with get_db() as conn:
        readings = conn.execute('SELECT * FROM readings WHERE timestamp >= datetime("now", "-3 days")').fetchall()
    return jsonify([dict(row) for row in readings])

# Endpoint to remove data
@app.route('/remove_readings', methods=['DELETE'])
def remove_readings():
    with get_db() as conn:
        conn.execute('DELETE FROM readings')
    return jsonify({"status": "all readings removed"}), 200

if __name__ == '__main__':
    app.run(debug=True)
