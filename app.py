from flask import Flask, render_template, request, jsonify
import threading

app = Flask(__name__)
lock = threading.Lock()

tables = [
    {"id": 1, "seats": 2, "status": "available"},
    {"id": 2, "seats": 4, "status": "available"},
    {"id": 3, "seats": 6, "status": "available"}
]
reservations = []

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", tables=tables, message=None)

@app.route("/reserve", methods=["POST"])
def reserve_web():
    try:
        table_id = int(request.form.get("table_id"))
    except (TypeError, ValueError):
        return render_template("index.html", tables=tables, message="Error: Invalid Table ID format")
    customer_name = request.form.get("customer_name")
    with lock:
        table = next((t for t in tables if t["id"] == table_id), None)
        if not table:
            return render_template("index.html", tables=tables, message="Error: Table not found")
        if table["status"] == "reserved":
            return render_template("index.html", tables=tables, message="Error: Table is already reserved")
        table["status"] = "reserved"
        reservations.append({"table_id": table_id, "customer_name": customer_name})
    return render_template("index.html", tables=tables, message=f"Success! Table {table_id} booked for {customer_name}.")

@app.route("/api/tables", methods=["GET"])
def get_tables():
    return jsonify({"success": True, "tables": tables}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
