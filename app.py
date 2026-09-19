from flask import Flask, render_template_string, request, redirect, url_for
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# In-memory database simulation (Session state alternative for Flask)
app_state = {
    "tables": [
        {"id": 1, "code": "T1", "name": "Table 1", "seats": 2, "status": "available"},
        {"id": 2, "code": "T2", "name": "Table 2", "seats": 4, "status": "available"},
        {"id": 3, "code": "T3", "name": "Table 3", "seats": 6, "status": "available"},
        {"id": 4, "code": "T4", "name": "Table 4", "seats": 8, "status": "available"}
    ],
    "reservations": [],
    "guest_count": 4,
    "nav_page": "Live Dashboard"
}

# HTML Template with Dark Mode & Enterprise UI
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DarkFactory - Enterprise Tablekeeper</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { background-color: #0b0f19; color: #f8fafc; font-family: 'Inter', sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1e293b; padding-bottom: 20px; margin-bottom: 20px; }
        .card { background: #111827; border: 1px solid #1f2937; border-radius: 16px; padding: 20px; margin-bottom: 20px; }
        .btn { background: #7c3aed; color: white; border: none; padding: 10px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; }
        .btn:hover { background: #6d28d9; }
        .badge-available { background: #dcfce7; color: #166534; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }
        .badge-reserved { background: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; }
        input, select { background: #1f2937; border: 1px solid #374151; color: white; padding: 10px; border-radius: 8px; width: 100%; margin-top: 5px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>🍽️ DarkFactory - Enterprise Tablekeeper</h2>
            <span style="background: #10b981; color: white; padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600;">🟢 Live Flask Server</span>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div class="card">
                <h3>Live Table Status</h3>
                {% for t in state.tables %}
                    <div style="display: flex; justify-content: space-between; align-items: center; background: #1f2937; padding: 12px; border-radius: 10px; margin-bottom: 10px;">
                        <div>
                            <strong>{{ t.name }}</strong> ({{ t.seats }} Seats)
                        </div>
                        <div>
                            {% if t.status == 'available' %}
                                <span class="badge-available">● AVAILABLE</span>
                            {% else %}
                                <span class="badge-reserved">● RESERVED</span>
                            {% endif %}
                        </div>
                    </div>
                {% endfor %}
            </div>

            <div class="card">
                <h3>Live Booking Desk</h3>
                <form method="POST" action="/book">
                    <label style="font-size: 12px; color: #9ca3af;">SELECT AVAILABLE TABLE</label>
                    <select name="table_id">
                        {% for t in state.tables %}
                            {% if t.status == 'available' %}
                                <option value="{{ t.id }}">{{ t.name }} ({{ t.seats }} Seats)</option>
                            {% endif %}
                        {% endfor %}
                    </select>

                    <label style="font-size: 12px; color: #9ca3af;">CUSTOMER NAME</label>
                    <input type="text" name="customer_name" value="Ashraf" required>

                    <label style="font-size: 12px; color: #9ca3af;">CONTACT PHONE</label>
                    <input type="text" name="phone" placeholder="(202) 555-0143" required>

                    <label style="font-size: 12px; color: #9ca3af;">GUEST COUNT</label>
                    <input type="number" name="guests" value="4" min="1" max="10" required>

                    <button type="submit" class="btn" style="width: 100%;">➕ Confirm Reservation Table</button>
                </form>
            </div>
        </div>

        <div class="card">
            <h3>Active Reservations Archive</h3>
            {% if state.reservations %}
                <table style="width: 100%; text-align: left; border-collapse: collapse;">
                    <tr style="border-bottom: 1px solid #374151;">
                        <th style="padding: 10px;">Customer</th>
                        <th style="padding: 10px;">Table ID</th>
                        <th style="padding: 10px;">Phone</th>
                        <th style="padding: 10px;">Guests</th>
                        <th style="padding: 10px;">Timestamp</th>
                    </tr>
                    {% for r in state.reservations %}
                    <tr style="border-bottom: 1px solid #1f2937;">
                        <td style="padding: 10px;">{{ r['Customer Name'] }}</td>
                        <td style="padding: 10px;">Table {{ r['Table ID'] }}</td>
                        <td style="padding: 10px;">{{ r['Phone'] }}</td>
                        <td style="padding: 10px;">{{ r['Guests'] }}</td>
                        <td style="padding: 10px;">{{ r['Timestamp'] }}</td>
                    </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p style="color: #9ca3af;">No active reservations recorded yet.</p>
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
    table_id = int(request.form.get("table_id"))
    customer_name = request.form.get("customer_name")
    phone = request.form.get("phone")
    guests = int(request.form.get("guests"))
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for t in app_state["tables"]:
        if t["id"] == table_id:
            t["status"] = "reserved"
            app_state["reservations"].append({
                "Table ID": table_id,
                "Customer Name": customer_name,
                "Phone": phone,
                "Guests": guests,
                "Timestamp": timestamp
            })
            break
            
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)