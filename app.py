@app.route('/')
def home():
    return {"status": "success", "message": "DarkFactory API is live and running!"}, 200
from flask import Flask, request, jsonify
import threading

app = Flask(__name__)
lock = threading.Lock()

# In-memory storage with domain extension (cancellations / time slots)
tables = [
    {"id": 1, "seats": 2, "status": "available"},
    {"id": 2, "seats": 4, "status": "available"},
    {"id": 3, "seats": 6, "status": "available"}
]
reservations = []
idempotency_store = {}

@app.route('/api/tables', methods=['GET'])
def get_tables():
    return jsonify({"success": True, "tables": tables}), 200

@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    idem_key = request.headers.get('X-Idempotency-Key')
    if idem_key and idem_key in idempotency_store:
        return jsonify(idempotency_store[idem_key]["response"]), idempotency_store[idem_key]["status"]

    data = request.get_json()
    if not data or 'table_id' not in data or 'customer_name' not in data:
        return jsonify({"success": False, "error": "Malformed input: Missing table_id or customer_name"}), 400
        
    try:
        table_id = int(data['table_id'])
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid table_id format"}), 400

    with lock:
        table = next((t for t in tables if t['id'] == table_id), None)
        
        if not table:
            response_data, status_code = {"success": False, "error": "Table not found"}, 404
        elif table['status'] == 'reserved':
            response_data, status_code = {"success": False, "error": "Conflict: Table is already reserved"}, 409
        else:
            table['status'] = 'reserved'
            reservation = {
                "reservation_id": len(reservations) + 1,
                "table_id": table_id,
                "customer_name": data['customer_name'],
                "status": "confirmed"
            }
            reservations.append(reservation)
            response_data, status_code = {"success": True, "reservation": reservation}, 201

    if idem_key:
        idempotency_store[idem_key] = {"response": response_data, "status": status_code}

    return jsonify(response_data), status_code

# --- STAGE 4: Domain Extension (Cancel Reservation) ---
@app.route('/api/reservations/<int:reservation_id>', methods=['DELETE'])
def cancel_reservation(reservation_id):
    with lock:
        reservation = next((r for r in reservations if r['reservation_id'] == reservation_id and r['status'] == 'confirmed'), None)
        
        if not reservation:
            return jsonify({"success": False, "error": "Active reservation not found"}), 404
            
        # Free up the table
        table = next((t for t in tables if t['id'] == reservation['table_id']), None)
        if table:
            table['status'] = 'available'
            
        reservation['status'] = 'cancelled'
        
    return jsonify({"success": True, "message": f"Reservation {reservation_id} successfully cancelled and table released."}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
