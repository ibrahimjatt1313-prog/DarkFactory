from flask import Flask, render_template_string, request, redirect, url_for, Response
from datetime import datetime
import io
import csv

app = Flask(__name__)

# In-Memory Database State - Starts completely empty (No default data)
MEMORY_TABLES = []
MEMORY_RESERVATIONS = []
table_id_counter = 1
reservation_id_counter = 1

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L'Étoile Noir | Enterprise Concierge Suite</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-deep: #07090e;
            --bg-card: #0f141f;
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
            padding: 30px 20px;
        }
        .wrapper { max-width: 1400px; margin: 0 auto; }
        .hero-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 25px 35px;
            margin-bottom: 25px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
        }
        .hero-title h1 {
            font-family: 'Playfair Display', serif;
            font-size: 28px;
            color: #ffffff;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .hero-title p { color: var(--accent-gold); font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; }
        .header-actions { display: flex; gap: 12px; align-items: center; }
        .btn-export {
            background: rgba(212, 175, 55, 0.15);
            border: 1px solid rgba(212, 175, 55, 0.4);
            color: var(--accent-gold);
            padding: 8px 16px;
            border-radius: 50px;
            font-size: 12px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s;
        }
        .btn-export:hover { background: rgba(212, 175, 55, 0.3); }
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
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 25px;
        }
        @media(max-width: 900px) { .metrics-grid { grid-template-columns: 1fr 1fr; } }
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
        }
        .metric-title { font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 8px; }
        .metric-value { font-size: 24px; font-weight: 700; font-family: 'Playfair Display', serif; color: #fff; }
        .notification-banner {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.3);
            color: #60a5fa;
            padding: 12px 20px;
            border-radius: 12px;
            margin-bottom: 25px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .dashboard-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 25px;
            margin-bottom: 25px;
        }
        @media (max-width: 1024px) { .dashboard-grid { grid-template-columns: 1fr; } }
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.4);
            margin-bottom: 25px;
        }
        .card h3 {
            font-family: 'Playfair Display', serif;
            font-size: 18px;
            margin-bottom: 15px;
            color: #ffffff;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
        }
        .zone-tabs { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 15px; }
        .zone-tab {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.2s;
        }
        .zone-tab.active, .zone-tab:hover { background: var(--accent-gold); color: #000; border-color: var(--accent-gold); }
        .tables-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 12px;
            max-height: 480px;
            overflow-y: auto;
            padding-right: 5px;
        }
        .tables-container::-webkit-scrollbar { width: 6px; }
        .tables-container::-webkit-scrollbar-thumb { background: #374151; border-radius: 10px; }
        .table-box {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 14px;
            transition: all 0.3s ease;
        }
        .table-box:hover { border-color: var(--accent-gold); transform: translateY(-2px); }
        .table-info-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
        .table-name { font-weight: 600; font-size: 13px; color: #fff; }
        .table-zone { font-size: 10px; color: var(--accent-gold); margin-top: 2px; }
        .table-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 11px; color: var(--text-muted); }
        .badge-avail { background: rgba(16, 185, 129, 0.1); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.2); padding: 2px 6px; border-radius: 6px; font-size: 9px; font-weight: 700; }
        .badge-res { background: rgba(239, 68, 68, 0.1); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.2); padding: 2px 6px; border-radius: 6px; font-size: 9px; font-weight: 700; }
        .form-group { margin-bottom: 14px; }
        .form-group label { display: block; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); margin-bottom: 5px; }
        .form-control {
            width: 100%;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-color);
            color: #ffffff;
            padding: 10px 14px;
            border-radius: 10px;
            font-size: 13px;
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
            padding: 12px;
            border-radius: 10px;
            font-weight: 700;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.3);
            margin-top: 5px;
        }
        .btn-luxury:hover { background: linear-gradient(135deg, #e6c555 0%, #d4af37 100%); transform: translateY(-1px); }
        .ledger-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }
        .search-input { background: rgba(0,0,0,0.4); border: 1px solid var(--border-color); color: #fff; padding: 8px 14px; border-radius: 8px; font-size: 12px; width: 260px; outline: none; }
        .search-input:focus { border-color: var(--accent-gold); }
        .archive-table { width: 100%; border-collapse: collapse; text-align: left; }
        .archive-table th { font-size: 10px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-muted); padding: 10px; border-bottom: 1px solid var(--border-color); font-weight: 600; }
        .archive-table td { padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 12px; color: #e5e7eb; }
        .btn-cancel {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #f87171;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-cancel:hover { background: rgba(239, 68, 68, 0.3); }
        .empty-state { text-align: center; color: var(--text-muted); padding: 25px; font-style: italic; font-size: 13px; }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="hero-header">
            <div class="hero-title">
                <h1>L'Étoile Noir & Grand Gastronomy</h1>
                <p>Enterprise Tablekeeper & Concierge Suite</p>
            </div>
            <div class="header-actions">
                <a href="/export" class="btn-export">📥 Export Ledger (CSV)</a>
                <div class="server-badge">Live Secure Cluster</div>
            </div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">Total Elite Suites</div>
                <div class="metric-value">{{ metrics.total_suites }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Occupancy Rate</div>
                <div class="metric-value" style="color: #34d399;">{{ metrics.occupancy_rate }}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Active Reservations</div>
                <div class="metric-value" style="color: var(--accent-gold);">{{ metrics.active_count }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Total Seated Guests</div>
                <div class="metric-value">{{ metrics.total_guests }}</div>
            </div>
        </div>

        {% if notification %}
        <div class="notification-banner">
            🔔 <strong>Automated System Dispatch:</strong> {{ notification }}
        </div>
        {% endif %}

        <div class="dashboard-grid">
            <div class="card" style="margin-bottom: 0;">
                <h3>Real-Time Floor Status</h3>
                <div class="zone-tabs">
                    <a href="/?zone=All" class="zone-tab {% if current_zone == 'All' %}active{% endif %}">All Zones</a>
                    <a href="/?zone=Grand%20Ballroom" class="zone-tab {% if current_zone == 'Grand Ballroom' %}active{% endif %}">Grand Ballroom</a>
                    <a href="/?zone=Garden%20Terrace" class="zone-tab {% if current_zone == 'Garden Terrace' %}active{% endif %}">Garden Terrace</a>
                    <a href="/?zone=Penthouse%20Suite" class="zone-tab {% if current_zone == 'Penthouse Suite' %}active{% endif %}">Penthouse Suite</a>
                    <a href="/?zone=Wine%20Cellar" class="zone-tab {% if current_zone == 'Wine Cellar' %}active{% endif %}">Wine Cellar</a>
                    <a href="/?zone=VIP%20Lounge" class="zone-tab {% if current_zone == 'VIP Lounge' %}active{% endif %}">VIP Lounge</a>
                </div>

                <div class="tables-container">
                    {% if tables %}
                        {% for t in tables %}
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
                    {% else %}
                        <div class="empty-state" style="grid-column: 1 / -1;">No suites available in this view. Use the form to add a new suite.</div>
                    {% endif %}
                </div>
            </div>

            <div>
                <!-- Add Table Desk -->
                <div class="card">
                    <h3>Add New Suite / Table</h3>
                    <form method="POST" action="/add-table">
                        <div class="form-group">
                            <label>Suite Code (e.g., GB-01)</label>
                            <input type="text" name="code" class="form-control" placeholder="GB-01" required>
                        </div>
                        <div class="form-group">
                            <label>Suite Name</label>
                            <input type="text" name="name" class="form-control" placeholder="Grand Ballroom Suite 1" required>
                        </div>
                        <div class="form-group">
                            <label>Zone Category</label>
                            <select name="zone" class="form-control" required>
                                <option value="Grand Ballroom">Grand Ballroom</option>
                                <option value="Garden Terrace">Garden Terrace</option>
                                <option value="Penthouse Suite">Penthouse Suite</option>
                                <option value="Wine Cellar">Wine Cellar</option>
                                <option value="VIP Lounge">VIP Lounge</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Seat Capacity</label>
                            <input type="number" name="seats" class="form-control" value="4" min="1" max="30" required>
                        </div>
                        <button type="submit" class="btn-luxury" style="background: rgba(212, 175, 55, 0.2); color: var(--accent-gold); border: 1px solid rgba(212, 175, 55, 0.4);">Add Suite to Floor</button>
                    </form>
                </div>

                <!-- VIP Booking Desk -->
                <div class="card">
                    <h3>VIP Concierge Desk</h3>
                    <form method="POST" action="/book">
                        <div class="form-group">
                            <label>Select Available Suite / Table</label>
                            <select name="table_id" class="form-control" required>
                                {% set available_found = namespace(val=false) %}
                                {% for t in MEMORY_TABLES %}
                                    {% if t.status == 'available' %}
                                        {% set available_found.val = true %}
                                        <option value="{{ t.id }}">{{ t.name }} ({{ t.zone }} - {{ t.seats }} S)</option>
                                    {% endif %}
                                {% endfor %}
                                {% if not available_found.val %}
                                    <option value="" disabled selected>No available suites found</option>
                                {% endif %}
                            </select>
                        </div>

                        <div class="form-group">
                            <label>Distinguished Guest Name</label>
                            <input type="text" name="customer_name" class="form-control" placeholder="Enter guest name..." required>
                        </div>

                        <div class="form-group">
                            <label>Direct Contact Phone</label>
                            <input type="text" name="phone" class="form-control" placeholder="+92 300 0000000" required>
                        </div>

                        <div class="form-group">
                            <label>Party Size (Guests)</label>
                            <input type="number" name="guests" class="form-control" value="4" min="1" max="30" required>
                        </div>

                        <button type="submit" class="btn-luxury">Confirm VIP Reservation</button>
                    </form>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="ledger-header">
                <h3>Confirmed Reservations Ledger</h3>
                <form method="GET" action="/" style="margin: 0;">
                    <input type="hidden" name="zone" value="{{ current_zone }}">
                    <input type="text" name="search" class="search-input" placeholder="Search guest name or phone..." value="{{ search_query }}">
                </form>
            </div>

            {% if reservations %}
                <table class="archive-table">
                    <thead>
                        <tr>
                            <th>Guest Name</th>
                            <th>Table Assigned</th>
                            <th>Zone</th>
                            <th>Contact Phone</th>
                            <th>Party Size</th>
                            <th>Timestamp</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for r in reservations %}
                        <tr>
                            <td><strong>{{ r.customer_name }}</strong></td>
                            <td>{{ r.table_name }} ({{ r.code }})</td>
                            <td><span style="color: var(--accent-gold);">{{ r.zone }}</span></td>
                            <td>{{ r.phone }}</td>
                            <td>{{ r.guests }} Guests</td>
                            <td>{{ r.timestamp }}</td>
                            <td>
                                <form method="POST" action="/cancel/{{ r.id }}" style="margin: 0;">
                                    <button type="submit" class="btn-cancel">Cancel & Release</button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <div class="empty-state">No matching reservations recorded in the secure ledger.</div>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    zone_filter = request.args.get("zone", "All")
    search_query = request.args.get("search", "").strip()
    notification = request.args.get("note", "")
    
    # Filter tables based on zone
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
    
    # Filter reservations for search
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
    
    note = f"Suite {name} ({code}) successfully added to floor plan."
    return redirect(url_for("index", note=note))

@app.route("/book", methods=["POST"])
def book():
    global reservation_id_counter
    table_id_str = request.form.get("table_id")
    customer_name = request.form.get("customer_name")
    phone = request.form.get("phone")
    guests = request.form.get("guests")
    
    if not table_id_str:
        return redirect(url_for("index", note="Please select a valid suite."))
        
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
        
    note = f"VIP Suite successfully secured and confirmed for {customer_name}."
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
        
    note = "Reservation successfully cancelled and suite released back to available status."
    return redirect(url_for("index", note=note))

@app.route("/export")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Reservation ID", "Guest Name", "Suite Name", "Code", "Zone", "Phone", "Guests", "Timestamp"])
    
    for r in MEMORY_RESERVATIONS:
        writer.writerow([r["id"], r["customer_name"], r["table_name"], r["code"], r["zone"], r["phone"], r["guests"], r["timestamp"]])
        
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=reservations_ledger.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)