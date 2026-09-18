import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="DarkFactory - Enterprise Tablekeeper", page_icon="???", layout="wide")

# Custom Professional Styling
st.markdown("""
    <style>
        .metric-card { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef; text-align: center; }
        .stButton>button { width: 100%; border-radius: 6px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("??? DarkFactory - Enterprise Tablekeeper System")
st.markdown("Advanced Stage 4 Restaurant Reservation Management Platform for WeAreDevelopers x BAND Hackathon.")
st.markdown("---")

# Initialize Session State
if "tables" not in st.session_state:
    st.session_state.tables = [
        {"id": 1, "seats": 2, "status": "available"},
        {"id": 2, "seats": 4, "status": "available"},
        {"id": 3, "seats": 6, "status": "available"},
        {"id": 4, "seats": 8, "status": "available"},
        {"id": 5, "seats": 10, "status": "available"}
    ]

if "reservations" not in st.session_state:
    st.session_state.reservations = []

# --- TOP METRICS DASHBOARD ---
total_tables = len(st.session_state.tables)
available_count = len([t for t in st.session_state.tables if t["status"] == "available"])
reserved_count = total_tables - available_count

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Tables", value=total_tables)
with col2:
    st.metric(label="Available Tables", value=available_count, delta=f"{available_count} free")
with col3:
    st.metric(label="Active Reservations", value=reserved_count, delta=f"-{reserved_count} booked" if reserved_count > 0 else "0")

st.markdown("---")

# Layout: Two Columns (Left: Tables & Actions, Right: Reservation Management)
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("?? Live Table Status")
    df_tables = pd.DataFrame(st.session_state.tables)
    st.dataframe(df_tables, use_container_width=True, hide_index=True)

    st.subheader("? Book a Table")
    with st.form("booking_form"):
        available_ids = [t["id"] for t in st.session_state.tables if t["status"] == "available"]
        
        if available_ids:
            selected_table = st.selectbox("Select Available Table ID", options=available_ids)
            customer_name = st.text_input("Customer Full Name")
            phone_number = st.text_input("Customer Phone Number")
            
            submit = st.form_submit_button("Confirm Booking", type="primary")
            
            if submit:
                if not customer_name.strip() or not phone_number.strip():
                    st.error("Please fill in all required customer details.")
                else:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for table in st.session_state.tables:
                        if table["id"] == selected_table:
                            table["status"] = "reserved"
                            st.session_state.reservations.append({
                                "Booking ID": len(st.session_state.reservations) + 1,
                                "Table ID": selected_table,
                                "Customer Name": customer_name,
                                "Phone": phone_number,
                                "Timestamp": timestamp
                            })
                            st.success(f"Table {selected_table} successfully booked for {customer_name}!")
                            st.rerun()
        else:
            st.warning("All tables are currently fully booked.")

with right_col:
    st.subheader("?? Active Reservations & Management")
    
    if st.session_state.reservations:
        # Search / Filter Bar
        search_query = st.text_input("?? Search by Customer Name or Table ID", "").lower()
        
        filtered_reservations = st.session_state.reservations
        if search_query:
            filtered_reservations = [
                r for r in st.session_state.reservations 
                if search_query in r["Customer Name"].lower() or search_query in str(r["Table ID"])
            ]
        
        df_res = pd.DataFrame(filtered_reservations)
        st.dataframe(df_res, use_container_width=True, hide_index=True)
        
        st.markdown("### ?? Release / Cancel Table")
        with st.form("release_form"):
            booked_table_ids = [t["id"] for t in st.session_state.tables if t["status"] == "reserved"]
            if booked_table_ids:
                release_table_id = st.selectbox("Select Reserved Table to Free Up", options=booked_table_ids)
                release_submit = st.form_submit_button("Release Table (Checkout)")
                
                if release_submit:
                    # Update table status
                    for table in st.session_state.tables:
                        if table["id"] == release_table_id:
                            table["status"] = "available"
                    # Remove from active reservations log
                    st.session_state.reservations = [r for r in st.session_state.reservations if r["Table ID"] != release_table_id]
                    st.success(f"Table {release_table_id} has been released and is now available!")
                    st.rerun()
            else:
                st.info("No active reservations to release.")
    else:
        st.info("No active reservations recorded yet.")
