import requests

BASE_URL = "http://127.0.0.1:5000/api"

def test_api():
    print("[Test] Fetching tables...")
    res = requests.get(f"{BASE_URL}/tables")
    print("Tables Response:", res.json())
    
    print("\n[Test] Creating a reservation...")
    payload = {"table_id": 1, "customer_name": "Ibraheem"}
    res = requests.post(f"{BASE_URL}/reservations", json=payload)
    print("Reservation Response:", res.json())

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("[Error] Flask server running nahi hai! Pehle 'python stage-1/app.py' chalayein.")
