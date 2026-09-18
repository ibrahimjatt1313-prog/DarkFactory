import streamlit as st

st.set_page_config(page_title="DarkFactory - Tablekeeper UI", page_icon="???", layout="centered")

st.title("DarkFactory - Tablekeeper UI")
st.write("Welcome to the Table Reservation system for the WeAreDevelopers x BAND hackathon.")

if "tables" not in st.session_state:
    st.session_state.tables = [
        {"id": 1, "seats": 2, "status": "available"},
        {"id": 2, "seats": 4, "status": "available"},
        {"id": 3, "seats": 6, "status": "available"},
        {"id": 4, "seats": 8, "status": "available"}
    ]

if "reservations" not in st.session_state:
    st.session_state.reservations = []

st.subheader("Available Tables Status")
st.table(st.session_state.tables)

st.markdown("---")
st.subheader("Make a New Reservation")

with st.form("reservation_form"):
    available_ids = [t["id"] for t in st.session_state.tables if t["status"] == "available"]
    if available_ids:
        table_id = st.selectbox("Select Table ID", options=available_ids)
        customer_name = st.text_input("Customer Full Name")
        submit_button = st.form_submit_button("Confirm Reservation")

        if submit_button:
            if not customer_name.strip():
                st.error("Please enter a valid customer name.")
            else:
                for table in st.session_state.tables:
                    if table["id"] == table_id:
                        table["status"] = "reserved"
                        st.session_state.reservations.append({"table_id": table_id, "customer_name": customer_name})
                        st.success(f"Success! Table {table_id} successfully booked for {customer_name}.")
                        st.rerun()
    else:
        st.info("No tables currently available.")

if st.session_state.reservations:
    st.markdown("---")
    st.subheader("Current Active Reservations")
    st.write(st.session_state.reservations)
