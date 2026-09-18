from flask import Flask, render_template_string, request, jsonify
import threading

app = Flask(__name__)
lock = threading.Lock()

tables = [
    {"id": 1, "seats": 2, "status": "available"},
    {"id": 2, "seats": 4, "status": "available"},
    {"id": 3, "seats": 6, "status": "available"}
]
reservations = []
idempotency_store = {}

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>DarkFactory - Table Reservation UI</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f4f4f9; color: #333; }
        .container { max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; border: 1px solid #ddd; text-align: left; }
        th { background-color: #007bff; color: white; }
        .form-group { margin-top: 15px; }
        input, select, button { padding: 8px; margin-top: 5px; width: 100%; box-sizing: border-box; }
        button { background-color: #28a745; color: white; border: none; cursor: pointer; border-radius: 4px; }
        button:hover { background-color: #218838; }
        .msg { margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h2>??? DarkFactory - Restaurant Reservations</h2>
        
        <h3>Available Tables</h3>
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
                    <td>{{ table.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="form-group">
            <h3>Make a Reservation</h3>
            <form method="POST" action="/reserve">
                <label for="table_id">Select Table ID:</label>
                <input type="number" id="table_id" name="table_id" required>
                
                <label for="customer_name">Customer Name:</label>
                <input type="text" id="customer_name" name="customer_name" required>
                
                <button type="submit">Book Table</button>
            </form>
        </div>

        {% if message %}
        <p class="msg" style="color: {{ "green" if "Success" in message else "red" }};">{{ message }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TEMPLATE, tables=tables, message=None)

@app.route("/reserve", methods=["POST"])
def reserve_web():
    try:
        table_id = int(request.form.get("table_id"))
    except (TypeError, ValueError):
        return render_template_string(TEMPLATE, tables=tables, message="Error: Invalid Table ID format")
        
    customer_name = request.form.get("customer_name")
    
    with lock:
        table = next((t for t in tables if t["id"] == table_id), None)
        if not table:
            return render_template_string(TEMPLATE, tables=tables, message="Error: Table not found")
            
        if table["status"] == "reserved":
            return render_template_string(TEMPLATE, tables=tables, message="Error: Table is already reserved")
            
        table["status"] = "reserved"
        reservation = {
            "reservation_id": len(reservations) + 1,
            "table_id": table_id,
            "customer_name": customer_name,
            "status": "confirmed"
        }
        reservations.append(reservation)
        
    return render_template_string(TEMPLATE, tables=tables, message=f"Success! Table {table_id} booked for {customer_name}.")

@app.route("/api/tables", methods=["GET"])
def get_tables():
    return jsonify({"success": True, "tables": tables}), 200

@app.route("/api/reservations", methods=["POST"])
def create_reservation():
    idem_key = request.headers.get("X-Idempotency-Key")
    if idem_key and idem_key in idempotency_store:
        return jsonify(idempotency_store[idem_key]["response"]), idempotency_store[idem_key]["status"]

    data = request.get_json()
    if not data or "table_id" not in data or "customer_name" not in data:
        return jsonify({"success": False, "error": "Malformed input: Missing table_id or customer_name"}), 400
        
    try:
        table_id = int(data["table_id"])
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid table_id format"}), 400

    with lock:
        table = next((t for t in tables if t["id"] == table_id), None)
        
        if not table:
            response_data, status_code = {"success": False, "error": "Table not found"}, 404
        elif table["status"] == "reserved":
            response_data, status_code = {"success": False, "error": "Conflict: Table is already reserved"}, 409
        else:
            table["status"] = "reserved"
            reservation = {
                "reservation_id": len(reservations) + 1,
                "table_id": table_id,
                "customer_name": data["customer_name"],
                "status": "confirmed"
            }
            reservations.append(reservation)
            response_data, status_code = {"success": True, "reservation": reservation}, 201

    if idem_key:
        idempotency_store[idem_key] = {"response": response_data, "status": status_code}

    return jsonify(response_data), status_code

@app.route("/api/reservations/<int:reservation_id>", methods=["DELETE"])
def cancel_reservation(reservation_id):
    with lock:
        reservation = next((r for r in reservations if r["reservation_id"] == reservation_id and r["status"] == "confirmed"), None)
        
        if not reservation:
            return jsonify({"success": False, "error": "Active reservation not found"}), 404
            
        table = next((t for t in tables if t["id"] == reservation["table_id"]), None)
        if table:
            table["status"] = "available"
            
        reservation["status"] = "cancelled"
        
    return jsonify({"success": True, "message": f"Reservation {reservation_id} successfully cancelled and table released."}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)

