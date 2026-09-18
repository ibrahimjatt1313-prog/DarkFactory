from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# In-memory storage for Stage 2 Web UI
tables = [
    {"id": 1, "seats": 2, "status": "available"},
    {"id": 2, "seats": 4, "status": "available"},
    {"id": 3, "seats": 6, "status": "available"}
]
reservations = []

TEMPLATE = """
<!DOCTYPE html>
html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Tablekeeper - Stage 2 Web UI</title>
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
    </style>
</head>
<body>
    <div class="container">
        <h2>🍽️ Tablekeeper - Restaurant Reservations</h2>
        
        <h3>Available Tables</h3>
        <table>
            <thead>
                <tr>
                    <th>Table ID</th>
                    <th>Seats</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody data-testid="table-list">
                {% for table in tables %}
                <tr data-testid="table-row-{{ table.id }}">
                    <td data-testid="table-id-{{ table.id }}">{{ table.id }}</td>
                    <td data-testid="table-seats-{{ table.id }}">{{ table.seats }}</td>
                    <td data-testid="table-status-{{ table.id }}">{{ table.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <div class="form-group">
            <h3>Make a Reservation</h3>
            <form method="POST" action="/reserve">
                <label for="table_id">Select Table ID:</label>
                <input type="number" id="table_id" name="table_id" data-testid="input-table-id" required>
                
                <label for="customer_name">Customer Name:</label>
                <input type="text" id="customer_name" name="customer_name" data-testid="input-customer-name" required>
                
                <button type="submit" data-testid="submit-reservation">Book Table</button>
            </form>
        </div>

        {% if message %}
        <p data-testid="response-message" style="margin-top: 15px; font-weight: bold; color: green;">{{ message }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(TEMPLATE, tables=tables, message=None)

@app.route('/reserve', methods=['POST'])
def reserve():
    try:
        table_id = int(request.form.get('table_id'))
    except (TypeError, ValueError):
        return render_template_string(TEMPLATE, tables=tables, message="Invalid Table ID format"), 400
        
    customer_name = request.form.get('customer_name')
    
    table = next((t for t in tables if t['id'] == table_id), None)
    if not table:
        return render_template_string(TEMPLATE, tables=tables, message="Error: Table not found"), 404
        
    if table['status'] == 'reserved':
        return render_template_string(TEMPLATE, tables=tables, message="Error: Table is already reserved"), 409
        
    table['status'] = 'reserved'
    reservations.append({"table_id": table_id, "customer_name": customer_name})
    
    return render_template_string(TEMPLATE, tables=tables, message=f"Success! Table {table_id} booked for {customer_name}.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
