from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# High-End Luxury Restaurant In-Memory Database State
app_state = {
    "tables": [
        {"id": 1, "code": "VIP-01", "name": "VIP Royal Suite 1", "seats": 2, "zone": "VIP Lounge", "status": "available"},
        {"id": 2, "code": "VIP-02", "name": "VIP Royal Suite 2", "seats": 4, "zone": "VIP Lounge", "status": "available"},
        {"id": 3, "code": "ROOF-01", "name": "Skyline Rooftop A", "seats": 2, "zone": "Rooftop Deck", "status": "available"},
        {"id": 4, "code": "ROOF-02", "name": "Skyline Rooftop B", "seats": 4, "zone": "Rooftop Deck", "status": "available"},
        {"id": 5, "code": "ROOF-03", "name": "Skyline Rooftop C", "seats": 6, "zone": "Rooftop Deck", "status": "available"},
        {"id": 6, "code": "MAIN-01", "name": "Grand Hall Table 1", "seats": 2, "zone": "Main Dining", "status": "available"},
        {"id": 7, "code": "MAIN-02", "name": "Grand Hall Table 2", "seats": 4, "zone": "Main Dining", "status": "available"},
        {"id": 8, "code": "MAIN-03", "name": "Grand Hall Table 3", "seats": 4, "zone": "Main Dining", "status": "available"},
        {"id": 9, "code": "MAIN-04", "name": "Grand Hall Table 4", "seats": 6, "zone": "Main Dining", "status": "available"},
        {"id": 10, "code": "MAIN-05", "name": "Grand Hall Table 5", "seats": 8, "zone": "Main Dining", "status": "available"},
        {"id": 11, "code": "PRIV-01", "name": "Executive Boardroom", "seats": 12, "zone": "Private Rooms", "status": "available"},
        {"id": 12, "code": "PRIV-02", "name": "Chef's Table Experience", "seats": 6, "zone": "Private Rooms", "status": "available"}
    ],
    "reservations": [],
    "restaurant_name": "L'Étoile Noir & Grand Gastronomy"
}

# Luxury Dark Theme UI Template with Premium Typography & Glassmorphism
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L'Étoile Noir | Executive Dining & Reservation Suite</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #07090e;
            --bg-card: #0f141f;
            --bg-glass: rgba(17, 24, 39, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-gold: #d4af37;
            --accent-gold-hover: #e6c555;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-deep);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-image: radial-gradient(circle at 50% 0%, #1a102f 0%, transparent 50%), radial-gradient(circle at 100% 100%, #0d1b2a 0%, transparent 40%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .wrapper { max-width: 1400px; margin: 0 auto; }
        
        /* Header Banner */
        .hero-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 30px 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
            backdrop-filter: blur(10px);
        }
        .hero-title h1 {
            font-family: 'Playfair Display', serif;
            font-size: 32px;
            color: #ffffff;
            font-weight: 700;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
        }
        .hero-title p { color: var(--accent-gold); font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; }
        .server-badge {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #34d399;
            padding: 8px 16px;
            border-radius: 50px;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .server-badge::before { content: ""; width: 8px; height: 8px; background: #34d399; border-radius: 50%; box-shadow: 0 0 10px #34d399; }

        /* Grid Layout */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        @media (max-width: 1024px) { .dashboard-grid { grid-template-columns: 1fr; } }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }
        .card h3 {
            font-family: 'Playfair Display', serif;
            font-size: 20px;
            margin-bottom: 20px;
            color: #ffffff;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px;
        }

        /* Tables Grid View */
        .tables-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 15px;
            max-height: 520px;
            overflow-y: auto;
            padding-right: 5px;
        }
        .tables-container::-webkit-scrollbar { width: 6px; }
        .tables-container::-webkit-scrollbar-thumb { background: #374151; border-radius: 10px; }

        .table-box {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 16px;
            transition: all 0.3s ease;
        }
        .table-box:hover { border-color: var(--accent-gold); transform: translateY(-2px); }
        .table-info-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
        .table-name { font-weight: 600; font-size: 14px; color: #fff; }
        .table-zone { font-size: 11px; color: var(--accent-gold); margin-top: 2px; }
        .table-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; font-size: 12px; color: var(--text-muted); }
        
        .badge-avail { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; }
        .badge-res { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); padding: 3px 8px; border-radius: 6px; font-size: 10px; font-weight: 700; letter-spacing: 0.5px; }

        /* Form Controls */
        .form-group { margin-bottom: 16px; }
        .form-group label { display: block; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); margin-bottom: 6px; }
        .form-control {
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-color);
            color: #ffffff;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }
        .form-control:focus { border-color: var(--accent-gold); }
        select.form-control option { background: #0f141f; color: #fff; }

        .btn-luxury {
            background: linear-gradient(135deg, #d4af37 0%, #aa8c2c 100%);
            color: #000000;
            border: none;
            width: 100%;
            padding: 14px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
            margin-top: 10px;
        }
        .btn-luxury:hover { background: linear-gradient(135deg, #e6c555 0%, #d4af37 100%); transform: translateY(-1px); box-shadow: 0 6px 20px rgba(212, 175, 55, 0.4); }

        /* Reservations Archive Table */
        .archive-table { width: 100%; border-collapse: collapse; text-align: left; margin-top: 10px; }
        .archive-table th { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); padding: 12px; border-bottom: 1px solid var(--border-color); font-weight: 600; }
        .archive-table td { padding: 14px 12px; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 13px; color: #e5e7eb; }
        .empty-state { text-align: center; color: var(--text-muted); padding: 30px; font-style: italic; font-size: 14px; }
    </style>
</head>
<body>
    <div class="wrapper">
        <!-- Hero Header -->
        <div class="hero-header">
            <div class="hero-title">
                <h1>L'Étoile Noir & Grand Gastronomy</h1>
                <p>Executive Tablekeeper & Concierge Suite</p>
            </div>
            <div class="server-badge">Live Secure Cluster</div>
        </div>

        <!-- Main Content Grid -->
        <div class="dashboard-grid">
            <!-- Left Panel: Table Management Grid -->
            <div class="card">
                <h3>Real-Time Dining Room Floor Status ({{ state.tables|length }} Tables)</h3>
                <div class="tables-container">
                    {% for t in state.tables %}
                    <div class="table-box">
                        <div class="table-info-top">
                            <div>
                                <div class="table-name">{{ t.name }}</div>
                                <div class="table-zone">{{ t.zone }}</div>
                            </div>
                            <div>
                                {% if t.status == 'available' %}
                                    <span class="badge-avail">AVAILABLE</span>
                                {% else %}
                                    <span class="badge-res">RESERVED</span>
                                {% endif %}
                            </div>
                        </div>
                        <div class="table-meta">
                            <span>Code: <strong>{{ t.code }}</strong></span>
                            <span>👥 {{ t.seats }} Seats</span>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>

            <!-- Right Panel: Concierge Booking Desk -->
            <div class="card">
                <h3>VIP Reservation Desk</h3>
                <form method="POST" action="/book">
                    <div class="form-group">
                        <label>Select Available Table / Suite</label>
                        <select name="table_id" class="form-control" required>
                            {% set available_found = namespace(val=false) %}
                            {% for t in state.tables %}
                                {% if t.status == 'available' %}
                                    {% set available_found.val = true %}
                                    <option value="{{ t.id }}">{{ t.name }} ({{ t.zone }} - {{ t.seats }} Seats)</option>
                                {% endif %}
                            {% endfor %}
                            {% if not available_found.val %}
                                <option value="" disabled selected>All tables currently reserved</option>
                            {% endif %}
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Distinguished Guest Name</label>
                        <input type="text" name="customer_name" class="form-control" value="Muhammad Ibraheem Ashraf" required>
                    </div>

                    <div class="form-group">
                        <label>Direct Contact Phone</label>
                        <input type="text" name="phone" class="form-control" placeholder="+92 300 0000000" required>
                    </div>

                    <div class="form-group">
                        <label>Party Size (Guests)</label>
                        <input type="number" name="guests" class="form-control" value="4" min="1" max="15" required>
                    </div>

                    <button type="submit" class="btn-luxury">Confirm VIP Reservation</button>
                </form>
            </div>
        </div>

        <!-- Active Reservations Archive -->
        <div class="card">
            <h3>Confirmed Reservations Ledger</h3>
            {% if state.reservations %}
                <table class="archive-table">
                    <thead>
                        <tr>
                            <th>Guest Name</th>
                            <th>Table Assigned</th>
                            <th>Zone</th>
                            <th>Contact Phone</th>
                            <th>Party Size</th>
                            <th>Reservation Timestamp</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for r in state.reservations %}
                        <tr>
                            <td><strong>{{ r['Customer Name'] }}</strong></td>
                            <td>{{ r['Table Name'] }} ({{ r['Code'] }})</td>
                            <td><span style="color: var(--accent-gold);">{{ r['Zone'] }}</span></td>
                            <td>{{ r['Phone'] }}</td>
                            <td>{{ r['Guests'] }} Guests</td>
                            <td>{{ r['Timestamp'] }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <div class="empty-state">No active reservations recorded in the ledger for this session.</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, state=app_state)

@app.route("/book", methods=["POST"])
def book():
    table_id_raw = request.form.get("table_id")
    if not table_id_raw:
        return redirect(url_for("index"))
        
    table_id = int(table_id_raw)
    customer_name = request.form.get("customer_name")
    phone = request.form.get("phone")
    guests = int(request.form.get("guests"))
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for t in app_state["tables"]:
        if t["id"] == table_id:
            t["status"] = "reserved"
            app_state["reservations"].append({
                "Table ID": table_id,
                "Table Name": t["name"],
                "Code": t["code"],
                "Zone": t["zone"],
                "Customer Name": customer_name,
                "Phone": phone,
                "Guests": guests,
                "Timestamp": timestamp
            })
            break
            
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)