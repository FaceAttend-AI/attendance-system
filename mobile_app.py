from flask import Flask, jsonify, render_template_string
import sqlite3
import pandas as pd
from datetime import datetime

app = Flask(__name__)

MOBILE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Attendance System</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: Arial; background: #1a1a2e; color: white; padding: 15px; }

        .header { text-align: center; padding: 20px 0; }
        .header h1 { color: #4CAF50; font-size: 22px; }
        .header p  { color: #aaa; font-size: 13px; }

        .cards { display: flex; gap: 10px; margin: 15px 0; }
        .card  {
            flex: 1; background: #16213e; border-radius: 12px;
            padding: 15px; text-align: center;
        }
        .card .num   { font-size: 32px; font-weight: bold; color: #4CAF50; }
        .card .label { font-size: 12px; color: #aaa; margin-top: 5px; }

        .filter { margin: 10px 0; }
        .filter input {
            width: 100%; padding: 10px; border-radius: 8px;
            border: 1px solid #333; background: #16213e;
            color: white; font-size: 14px;
        }

        .btn {
            width: 100%; padding: 12px; margin: 5px 0;
            border-radius: 8px; border: none;
            background: #4CAF50; color: white;
            font-size: 15px; cursor: pointer;
        }
        .btn:active { background: #388E3C; }

        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th    { background: #4CAF50; padding: 10px 8px; font-size: 13px; }
        td    { padding: 10px 8px; border-bottom: 1px solid #333;
                font-size: 13px; }
        tr:nth-child(even) { background: #16213e; }

        .badge {
            background: #4CAF50; color: white;
            padding: 3px 8px; border-radius: 12px; font-size: 11px;
        }
        .refresh { text-align: center; color: #aaa;
                   font-size: 12px; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📋 Attendance System</h1>
        <p id="datetime"></p>
    </div>

    <div class="cards">
        <div class="card">
            <div class="num" id="total">-</div>
            <div class="label">Total Present</div>
        </div>
        <div class="card">
            <div class="num" id="unique">-</div>
            <div class="label">Students</div>
        </div>
    </div>

    <div class="filter">
        <input type="date" id="dateFilter" onchange="loadData()">
    </div>

    <button class="btn" onclick="loadData()">🔄 Refresh</button>
    <button class="btn" style="background:#2196F3"
            onclick="downloadCSV()">⬇️ Download CSV</button>

    <div id="tableContainer"></div>
    <p class="refresh">Auto-refresh every 30 seconds</p>

<script>
    // Set today's date
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('dateFilter').value = today;

    // Update clock
    function updateClock() {
        const now = new Date();
        document.getElementById('datetime').textContent =
            now.toLocaleDateString() + '  ' + now.toLocaleTimeString();
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Load attendance data
    async function loadData() {
        const date = document.getElementById('dateFilter').value;
        const res  = await fetch('/api/attendance?date=' + date);
        const data = await res.json();

        document.getElementById('total').textContent  = data.length;
        const unique = [...new Set(data.map(r => r.name))].length;
        document.getElementById('unique').textContent = unique;

        if (data.length === 0) {
            document.getElementById('tableContainer').innerHTML =
                '<p style="text-align:center;color:#aaa;margin-top:20px">No records found</p>';
            return;
        }

        let rows = data.map(r => `
            <tr>
                <td>${r.name}</td>
                <td>${r.time}</td>
                <td><span class="badge">${r.status}</span></td>
            </tr>`).join('');

        document.getElementById('tableContainer').innerHTML = `
            <table>
                <tr><th>Name</th><th>Time</th><th>Status</th></tr>
                ${rows}
            </table>`;
    }

    function downloadCSV() {
        const date = document.getElementById('dateFilter').value;
        window.location.href = '/api/download?date=' + date;
    }

    // Auto refresh every 30 seconds
    setInterval(loadData, 30000);
    loadData();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(MOBILE_HTML)

@app.route("/api/attendance")
def get_attendance():
    from flask import request
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    conn = sqlite3.connect("attendance.db")
    df   = pd.read_sql_query(
        "SELECT name, date, time, status FROM attendance WHERE date=? ORDER BY time DESC",
        conn, params=(date,)
    )
    conn.close()
    return jsonify(df.to_dict(orient="records"))

@app.route("/api/download")
def download_csv():
    from flask import request, Response
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    conn = sqlite3.connect("attendance.db")
    df   = pd.read_sql_query(
        "SELECT * FROM attendance WHERE date=? ORDER BY time",
        conn, params=(date,)
    )
    conn.close()
    return Response(
        df.to_csv(index=False),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=attendance_{date}.csv"}
    )

if __name__ == "__main__":
    print("\n" + "="*45)
    print("  Mobile App starting...")
    print("  Local:   http://localhost:5000")

    # Get local IP
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    print(f"  Mobile:  http://{ip}:5000")
    print("  Open on phone (same WiFi)")
    print("="*45 + "\n")

    app.run(host="0.0.0.0", port=5000, debug=False)