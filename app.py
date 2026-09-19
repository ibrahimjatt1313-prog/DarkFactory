from flask import Flask, render_template_string, request, redirect, url_for, Response
from datetime import datetime
import io
import csv

app = Flask(__name__)

# ==========================================
# ENTERPRISE CORE MOCK DATABASE
# ==========================================

MEMORY_TABLES = [
    {"id": 1, "code": "DT-01", "name": "Drive-Thru Lane 1", "seats": 4, "zone": "Drive-Thru", "status": "available"},
    {"id": 2, "code": "DT-02", "name": "Drive-Thru Lane 2", "seats": 4, "zone": "Drive-Thru", "status": "available"},
    {"id": 3, "code": "FC-101", "name": "Front Counter Station A", "seats": 2, "zone": "Front Counter", "status": "available"},
    {"id": 4, "code": "FC-102", "name": "Front Counter Station B", "seats": 2, "zone": "Front Counter", "status": "available"},
    {"id": 5, "code": "KS-01", "name": "Self-Order Kiosk Alpha", "seats": 1, "zone": "Kiosks", "status": "available"},
    {"id": 6, "code": "KS-02", "name": "Self-Order Kiosk Beta", "seats": 1, "zone": "Kiosks", "status": "available"},
    {"id": 7, "code": "DL-201", "name": "Global Dispatch Hub 1", "seats": 6, "zone": "Delivery Hub", "status": "available"},
    {"id": 8, "code": "VIP-01", "name": "Executive Lounge", "seats": 8, "zone": "VIP Lounge", "status": "available"}
]

MEMORY_RESERVATIONS = []

table_id_counter = 9
reservation_id_counter = 101

# ==========================================
# COMPREHENSIVE ENTERPRISE UI TEMPLATE
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L'Étoile Noire & Grand Gastronomy - Executive Suite</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #0f1117;
            --bg-card: #181b24;
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-brand: #6366f1;
            --accent-hover: #4f46e5;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: var(--bg-deep);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            padding: 25px 20px;
        }
        .wrapper { max-width: 1400px; margin: 0 auto; }
        .hero-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 24px 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .hero-title h1 {
            font-size: 24px;
            color: #ffffff;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .hero-title p { color: var(--accent-brand); font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px; }
        .header-actions { display: flex; gap: 12px; align-items: center; }
        .btn-export {
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.4);
            color: #818cf8;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s;
        }
        .btn-export:hover { background: rgba(99, 102, 241, 0.3); }
        .server-badge {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #34d399;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .server-badge::before { content: ""; width: 8px; height: 8px; background: #34d399; border-radius: 50%; box-shadow: 0 0 8px #34d399; }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        @media(max-width: 900px) { .metrics-grid { grid-template-columns: 1fr 1fr; } }
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 18px;
        }
        .metric-title { font-size: 10px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 6px; }
        .metric-value { font-size: 22px; font-weight: 700; color: #fff; }
        .notification-banner {
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #818cf8;
            padding: 12px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 13px;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        @media (max-width: 1024px) { .dashboard-grid { grid-template-columns: 1fr; } }
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        .card h3 {
            font-size: 16px;
            margin-bottom: 15px;
            color: #ffffff;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
            font-weight: 600;
        }
        .zone-tabs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 15px; }
        .zone-tab {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s;
        }
        .zone-tab.active, .zone-tab:hover { background: var(--accent-brand); color: #fff; border-color: var(--accent-brand); }
        .tables-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
            max-height: 440px;
            overflow-y: auto;
            padding-right: 5px;
        }
        .table-box {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .table-box:hover { border-color: var(--accent-brand); }
        .table-info-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
        .table-name { font-weight: 600; font-size: 12px; color: #fff; }
        .table-zone { font-size: 10px; color: var(--accent-brand); margin-top: 2px; }
        .table-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; margin-bottom: 8px; font-size: 11px; color: var(--text-muted); }
        .badge-avail { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; }
        .badge-res { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); padding: 2px 6px; border-radius: 4px; font-size: 9px; font-weight: 700; }
        .form-group { margin-bottom: 12px; }
        .form-group label { display: block; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-muted); margin-bottom: 4px; }
        .form-control {
            width: 100%;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border-color);
            color: #ffffff;
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 12px;
            outline: none;
        }
        .form-control:focus { border-color: var(--accent-brand); }
        select.form-control option { background: #181b24; color: #fff; }
        .btn-luxury {
            background: var(--accent-brand);
            color: #ffffff;
            border: none;
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-top: 4px;
        }
        .btn-luxury:hover { background: var(--accent-hover); }
        .ledger-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 10px; }
        .search-input { background: rgba(0,0,0,0.4); border: 1px solid var(--border-color); color: #fff; padding: 6px 12px; border-radius: 6px; font-size: 11px; width: 240px; outline: none; }
        .search-input:focus { border-color: var(--accent-brand); }
        .archive-table { width: 100%; border-collapse: collapse; text-align: left; }
        .archive-table th { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); padding: 8px; border-bottom: 1px solid var(--border-color); font-weight: 600; }
        .archive-table td { padding: 10px 8px; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 11px; color: #e0e0e0; }
        .btn-cancel {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #f87171;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 9px;
            font-weight: 700;
            cursor: pointer;
        }
        .btn-cancel:hover { background: rgba(239, 68, 68, 0.3); }
        .btn-delete-table {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.25);
            color: #f87171;
            width: 100%;
            padding: 5px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-delete-table:hover { background: rgba(239, 68, 68, 0.25); }
        .empty-state { text-align: center; color: var(--text-muted); padding: 20px; font-style: italic; font-size: 12px; }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="hero-header">
            <div class="hero-title">
                <h1>L'Étoile Noire & Grand Gastronomy</h1>
                <p>Executive Tablekeeper & Concierge Suite</p>
            </div>
            <div class="header-actions">
                <a href="/export" class="btn-export">📥 Export Reports (CSV)</a>
                <div class="server-badge">Live Secure Cluster</div>
            </div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">Total Units / Stations</div>
                <div class="metric-value">{{ metrics.total_suites }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Active Utilization Rate</div>
                <div class="metric-value" style="color: #34d399;">{{ metrics.occupancy_rate }}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Active Dispatch Orders</div>
                <div class="metric-value" style="color: var(--accent-brand);">{{ metrics.active_count }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Total Customer Traffic</div>
                <div class="metric-value">{{ metrics.total_guests }}</div>
            </div>
        </div>

        {% if notification %}
        <div class="notification-banner">
            ⚡ <strong>Automated Concierge:</strong> {{ notification }}
        </div>
        {% endif %}

        <div class="dashboard-grid">
            <div class="card" style="margin-bottom: 0;">
                <h3>Live Floor & Station Matrix</h3>
                <div class="zone-tabs">
                    <a href="/?zone=All" class="zone-tab {% if current_zone == 'All' %}active{% endif %}">All Zones</a>
                    <a href="/?zone=Drive-Thru" class="zone-tab {% if current_zone == 'Drive-Thru' %}active{% endif %}">Drive-Thru</a>
                    <a href="/?zone=Front%20Counter" class="zone-tab {% if current_zone == 'Front Counter' %}active{% endif %}">Front Counter</a>
                    <a href="/?zone=Kiosks" class="zone-tab {% if current_zone == 'Kiosks' %}active{% endif %}">Kiosks</a>
                    <a href="/?zone=Delivery%20Hub" class="zone-tab {% if current_zone == 'Delivery Hub' %}active{% endif %}">Delivery Hub</a>
                    <a href="/?zone=VIP%20Lounge" class="zone-tab {% if current_zone == 'VIP Lounge' %}active{% endif %}">VIP Lounge</a>
                </div>

                <div class="tables-container">
                    {% if tables %}
                        {% for t in tables %}
                        <div class="table-box">
                            <div>
                                <div class="table-info-top">
                                    <div>
                                        <div class="table-name">{{ t.name }}</div>
                                        <div class="table-zone">{{ t.zone }}</div>
                                    </div>
                                    <div>
                                        {% if t.status == 'available' %}
                                            <span class="badge-avail">READY</span>
                                        {% else %}
                                            <span class="badge-res">ACTIVE</span>
                                        {% endif %}
                                    </div>
                                </div>
                                <div class="table-meta">
                                    <span>ID: <strong>{{ t.code }}</strong></span>
                                    <span>👥 Cap: {{ t.seats }}</span>
                                </div>
                            </div>
                            <form method="POST" action="/delete-table/{{ t.id }}" style="margin: 0;">
                                <button type="submit" class="btn-delete-table">🗑️ Remove Station</button>
                            </form>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="empty-state" style="grid-column: 1 / -1;">No stations configured for this zone.</div>
                    {% endif %}
                </div>
            </div>

            <div>
                <!-- Add Station Desk -->
                <div class="card">
                    <h3>Register New Station</h3>
                    <form method="POST" action="/add-table">
                        <div class="form-group">
                            <label>Station Code (e.g., APX-03)</label>
                            <input type="text" name="code" class="form-control" placeholder="APX-03" required>
                        </div>
                        <div class="form-group">
                            <label>Station Name</label>
                            <input type="text" name="name" class="form-control" placeholder="Express Counter 3" required>
                        </div>
                        <div class="form-group">
                            <label>Zone Category</label>
                            <select name="zone" class="form-control" required>
                                <option value="Drive-Thru">Drive-Thru</option>
                                <option value="Front Counter">Front Counter</option>
                                <option value="Kiosks">Kiosks</option>
                                <option value="Delivery Hub">Delivery Hub</option>
                                <option value="VIP Lounge">VIP Lounge</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Capacity / Slots</label>
                            <input type="number" name="seats" class="form-control" value="4" min="1" max="50" required>
                        </div>
                        <button type="submit" class="btn-luxury" style="background: rgba(99, 102, 241, 0.2); color: #818cf8; border: 1px solid rgba(99, 102, 241, 0.4);">Register Station</button>
                    </form>
                </div>

                <!-- Booking / Order Dispatch Desk -->
                <div class="card">
                    <h3>Tablekeeper & Order Dispatch</h3>
                    <form method="POST" action="/book">
                        <div class="form-group">
                            <label>Select Ready Station</label>
                            <select name="table_id" class="form-control" required>
                                {% set available_found = namespace(val=false) %}
                                {% for t in MEMORY_TABLES %}
                                    {% if t.status == 'available' %}
                                        {% set available_found.val = true %}
                                        <option value="{{ t.id }}">{{ t.name }} ({{ t.zone }})</option>
                                    {% endif %}
                                {% endfor %}
                                {% if not available_found.val %}
                                    <option value="" disabled selected>All stations currently busy</option>
                                {% endif %}
                            </select>
                        </div>

                        <div class="form-group">
                            <label>Customer / Guest Name</label>
                            <input type="text" name="customer_name" class="form-control" placeholder="Guest name..." required>
                        </div>

                        <div class="form-group">
                            <label>Contact Phone</label>
                            <input type="text" name="phone" class="form-control" placeholder="+92 300 0000000" required>
                        </div>

                        <div class="form-group">
                            <label>Party / Order Size</label>
                            <input type="number" name="guests" class="form-control" value="2" min="1" max="50" required>
                        </div>

                        <button type="submit" class="btn-luxury">Dispatch & Secure Slot</button>
                    </form>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="ledger-header">
                <h3>Active Operations Ledger</h3>
                <form method="GET" action="/" style="margin: 0;">
                    <input type="hidden" name="zone" value="{{ current_zone }}">
                    <input type="text" name="search" class="search-input" placeholder="Search guest or phone..." value="{{ search_query }}">
                </form>
            </div>

            {% if reservations %}
                <table class="archive-table">
                    <thead>
                        <tr>
                            <th>Guest / Fleet</th>
                            <th>Station Assigned</th>
                            <th>Zone</th>
                            <th>Contact Phone</th>
                            <th>Size</th>
                            <th>Timestamp</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for r in reservations %}
                        <tr>
                            <td><strong>{{ r.customer_name }}</strong></td>
                            <td>{{ r.table_name }} ({{ r.code }})</td>
                            <td><span style="color: var(--accent-brand);">{{ r.zone }}</span></td>
                            <td>{{ r.phone }}</td>
                            <td>{{ r.guests }}</td>
                            <td>{{ r.timestamp }}</td>
                            <td>
                                <form method="POST" action="/cancel/{{ r.id }}" style="margin: 0;">
                                    <button type="submit" class="btn-cancel">Release</button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <div class="empty-state">No active orders found in the executive ledger.</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

# ==========================================
# FLASK ROUTE CONTROLLERS
# ==========================================

@app.route("/")
def index():
    zone_filter = request.args.get("zone", "All")
    search_query = request.args.get("search", "").strip()
    notification = request.args.get("note", "")
    
    if zone_filter == "All":
        tables = MEMORY_TABLES
    else:
        tables = [t for t in MEMORY_TABLES if t["zone"] == zone_filter]
        
    total_suites = len(MEMORY_TABLES)
    reserved_suites = sum(1 for t in MEMORY_TABLES if t["status"] == "reserved")
    occupancy_rate = round((reserved_suites / total_suites * 100), 1) if total_suites > 0 else 0
    total_guests = sum(int(r["guests"]) for r in MEMORY_RESERVATIONS)
    active_count = len(MEMORY_RESERVATIONS)
    
    metrics = {
        "total_suites": total_suites,
        "occupancy_rate": occupancy_rate,
        "active_count": active_count,
        "total_guests": total_guests
    }
    
    reservations = MEMORY_RESERVATIONS
    if search_query:
        reservations = [
            r for r in MEMORY_RESERVATIONS 
            if search_query.lower() in r["customer_name"].lower() or search_query in r["phone"]
        ]
        
    return render_template_string(
        HTML_TEMPLATE,
        tables=tables,
        reservations=reservations,
        metrics=metrics,
        current_zone=zone_filter,
        search_query=search_query,
        notification=notification,
        MEMORY_TABLES=MEMORY_TABLES
    )

@app.route("/add-table", methods=["POST"])
def add_table():
    global table_id_counter
    code = request.form.get("code")
    name = request.form.get("name")
    zone = request.form.get("zone")
    seats = int(request.form.get("seats", 4))
    
    new_table = {
        "id": table_id_counter,
        "code": code,
        "name": name,
        "seats": seats,
        "zone": zone,
        "status": "available"
    }
    MEMORY_TABLES.append(new_table)
    table_id_counter += 1
    
    note = f"Station {name} ({code}) successfully registered to the network."
    return redirect(url_for("index", note=note))

@app.route("/delete-table/<int:table_id>", methods=["POST"])
def delete_table(table_id):
    global MEMORY_TABLES, MEMORY_RESERVATIONS
    
    MEMORY_RESERVATIONS = [r for r in MEMORY_RESERVATIONS if r["table_id"] != table_id]
    MEMORY_TABLES = [t for t in MEMORY_TABLES if t["id"] != table_id]
    
    note = "Station removed successfully from the network."
    return redirect(url_for("index", note=note))

@app.route("/book", methods=["POST"])
def book():
    global reservation_id_counter
    table_id_str = request.form.get("table_id")
    customer_name = request.form.get("customer_name")
    phone = request.form.get("phone")
    guests = request.form.get("guests")
    
    if not table_id_str:
        return redirect(url_for("index", note="Please select an available station."))
        
    table_id = int(table_id_str)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    target_table = None
    for t in MEMORY_TABLES:
        if t["id"] == table_id:
            t["status"] = "reserved"
            target_table = t
            break
            
    if target_table:
        reservation = {
            "id": reservation_id_counter,
            "table_id": table_id,
            "table_name": target_table["name"],
            "code": target_table["code"],
            "zone": target_table["zone"],
            "customer_name": customer_name,
            "phone": phone,
            "guests": guests,
            "timestamp": timestamp
        }
        MEMORY_RESERVATIONS.insert(0, reservation)
        reservation_id_counter += 1
        
    note = f"Order successfully dispatched and secured for {customer_name}."
    return redirect(url_for("index", note=note))

@app.route("/cancel/<int:res_id>", methods=["POST"])
def cancel(res_id):
    global MEMORY_RESERVATIONS
    
    target_res = None
    for r in MEMORY_RESERVATIONS:
        if r["id"] == res_id:
            target_res = r
            break
            
    if target_res:
        t_id = target_res["table_id"]
        for t in MEMORY_TABLES:
            if t["id"] == t_id:
                t["status"] = "available"
                break
        MEMORY_RESERVATIONS = [r for r in MEMORY_RESERVATIONS if r["id"] != res_id]
        
    note = "Station released successfully and returned to ready status."
    return redirect(url_for("index", note=note))

@app.route("/export")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Order ID", "Guest Name", "Station Name", "Code", "Zone", "Phone", "Size", "Timestamp"])
    
    for r in MEMORY_RESERVATIONS:
        writer.writerow([r["id"], r["customer_name"], r["table_name"], r["code"], r["zone"], r["phone"], r["guests"], r["timestamp"]])
        
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=letoile_noire_operations_ledger.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)