from flask import Flask, render_template_string, request, jsonify
import threading

app = Flask(__name__)
lock = threading.Lock()

tables = [
    {"id": 1, "seats": 2, "status": "available"},
    {"id": 2, "seats": 4, "status": "available"},
    {"id": 3, "seats": 6, "status": "available"},
    {"id": 4, "seats": 8, "status": "available"}
]
reservations = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DarkFactory - Tablekeeper UI</title>
    <style>
        :root { --primary: #007bff; --success: #28a745; --danger: #dc3545; --bg: #f4f7f6; --card: #ffffff; --text: #333; }
        body { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; background-color: var(--bg); color: var(--text); margin: 0; padding: 40px; }
        .container { max-width: 700px; margin: auto; background: var(--card); padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }
        h2 { color: var(--primary); margin-top: 0; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        h3 { margin-top: 25px; color: #444; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; border-radius: 6px; overflow: hidden; }
        th, td { padding: 12px 15px; border: 1px solid #e1e1e1; text-align: left; }
        th { background-color: var(--primary); color: white; font-weight: 600; }
        tr:nth-child(even) { background-color: #fafafa; }
        .badge-available { color: var(--success); font-weight: bold; }
        .badge-reserved { color: var(--danger); font-weight: bold; }
        .form-group { margin-top: 20px; background: #fafbfc; padding: 20px; border: 1px solid #e1e1e1; border-radius: 8px; }
        label { display: block; margin-bottom: 6px; font-weight: 500; }
        input { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 14px; }
        button { background-color: var(--success); color: white; border: none; padding: 12px; width: 100%; font-size: 16px; font-weight: bold; cursor: pointer; border-radius: 6px; transition: background 0.2s; }
        button:hover { background-color: #218838; }
        .msg { margin-top: 15px; padding: 12px; border-radius: 6px; font-weight: bold; text-align: center; }
        .success-msg { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error-msg { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <h2>??? DarkFactory - Tablekeeper UI</h2>
        
        <h3>Available Tables Status</h3>
        <table>
            <thead>
                <tr>
                    <th>Table ID</th>
                    <th>Seats</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {% for table in tables %}
                <tr>
                    <td>{{ table.id }}</td>
                    <td>{{ table.seats }}</td>
                    <td>
                        <span class="{{ 'badge-available' if table.status == 'available' else 'badge-reserved' }}">
                            {{ table.status | capitalize }}
                        </span>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="form-group">
            <h3>Make a New Reservation</h3>
            <form method="POST" action="/reserve">
                <label for="table_id">Select Table ID:</label>
                <input type="number" id="table_id" name="table_id" placeholder="Enter table id (e.g., 1, 2, 3)" required>
                
                <label for="customer_name">Customer Name:</label>
                <input type="text" id="customer_name" name="customer_name" placeholder="Enter customer full name" required>
                
                <button type="submit">Confirm Reservation</button>
            </form>
        </div>

        {% if message %}
        <div class="msg {{ 'success-msg' if 'Success' in message else 'error-msg' }}">
            {{ message }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(HTML_TEMPLATE, tables=tables, message=None)

@app.route("/reserve", methods=["POST"])
def reserve_web():
    try:
        table_id = int(request.form.get("table_id"))
    except (TypeError, ValueError):
        return render_template_string(HTML_TEMPLATE, tables=tables, message="Error: Invalid Table ID format.")
        
    customer_name = request.form.get("customer_name")
    
    with lock:
        table = next((t for t in tables if t["id"] == table_id), None)
        if not table:
            return render_template_string(HTML_TEMPLATE, tables=tables, message="Error: Table not found.")
            
        if table["status"] == "reserved":
            return render_template_string(HTML_TEMPLATE, tables=tables, message=f"Error: Table {table_id} is already reserved!")
            
        table["status"] = "reserved"
        reservations.append({"table_id": table_id, "customer_name": customer_name})
        
    return render_template_string(HTML_TEMPLATE, tables=tables, message=f"Success! Table {table_id} successfully booked for {customer_name}.")

@app.route("/api/tables", methods=["GET"])
def get_tables():
    return jsonify({"success": True, "tables": tables}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
