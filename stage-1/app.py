from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for Stage 1 prototype
tables = [
    {"id": 1, "seats": 2, "status": "available"},
    {"id": 2, "seats": 4, "status": "available"},
    {"id": 3, "seats": 6, "status": "available"}
]
reservations = []

@app.route('/api/tables', methods=['GET'])
def get_tables():
    return jsonify({"success": True, "tables": tables}), 200

@app.route('/api/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    
    # Validation checks
    if not data or 'table_id' not in data or 'customer_name' not in data:
        return jsonify({"success": False, "error": "Missing required fields: table_id, customer_name"}), 400
        
    table_id = data['table_id']
    table = next((t for t in tables if t['id'] == table_id), None)
    
    if not table:
        return jsonify({"success": False, "error": "Table not found"}), 404
        
    if table['status'] == 'reserved':
        return jsonify({"success": False, "error": "Table is already reserved"}), 409
        
    # Book the table
    table['status'] = 'reserved'
    reservation = {
        "reservation_id": len(reservations) + 1,
        "table_id": table_id,
        "customer_name": data['customer_name'],
        "status": "confirmed"
    }
    reservations.append(reservation)
    
    return jsonify({"success": True, "reservation": reservation}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
