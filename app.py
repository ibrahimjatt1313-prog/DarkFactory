import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="DarkFactory - Enterprise Tablekeeper",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise Styling matching Reference UI exactly
st.markdown("""
    <style>
        .stApp {
            background-color: #f8fafc;
            font-family: 'Inter', sans-serif;
        }
        [data-testid="stSidebar"] {
            background-color: #0d1322;
            color: #ffffff;
            border-right: 1px solid #1e293b;
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #ffffff !important;
        }
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        }
        .badge-available {
            background-color: #dcfce7;
            color: #166534;
            padding: 3px 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 11px;
        }
        .table-box {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px 16px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 5px;">
            <div style="background: #7c3aed; color: white; padding: 6px 10px; border-radius: 6px; font-weight: bold;">DF</div>
            <h3 style="margin: 0; color: white; font-size: 18px;">DarkFactory</h3>
        </div>
        <p style="font-size: 10px; color: #64748b; letter-spacing: 1px; margin-bottom: 25px;">ENTERPRISE PLATFORM</p>
    """, unsafe_allow_html=True)
    
    selected_page = st.radio(
        "Navigation",
        ["🔲  Live Dashboard", "📋  Table Management", "📅  Reservations", "📈  Operational Logs", "⚙️  System Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background-color: #131d31; padding: 14px; border-radius: 10px; border: 1px solid #1e293b;">
            <p style="font-size: 10px; color: #818cf8; font-weight: 600; margin: 0;">US HACKATHON EDITION</p>
            <p style="font-size: 11px; color: #94a3b8; margin: 4px 0 0 0; line-height: 1.4;">WeAreDevelopers × BAND Reservation Platform Build</p>
        </div>
    """, unsafe_allow_html=True)

# Initialize Session State
if "tables" not in st.session_state:
    st.session_state.tables = [
        {"id": 1, "code": "T1", "name": "Table 1", "seats": 2, "status": "available"},
        {"id": 2, "code": "T2", "name": "Table 2", "seats": 4, "status": "available"},
        {"id": 3, "code": "T3", "name": "Table 3", "seats": 6, "status": "available"},
        {"id": 4, "code": "T4", "name": "Table 4", "seats": 8, "status": "available"}
    ]

if "reservations" not in st.session_state:
    st.session_state.reservations = []

if "guest_count" not in st.session_state:
    st.session_state.guest_count = 4

# --- TOP HEADER SECTION ---
header_col1, header_col2, header_col3 = st.columns([3, 1, 1])
with header_col1:
    st.markdown("## **Enterprise Tablekeeper System**")
    st.markdown("<p style='color: #64748b; margin-top: -10px; font-size: 14px;'>Real-time restaurant reservation and table seating coordinator dashboard</p>", unsafe_allow_html=True)
with header_col2:
    st.markdown("""
        <div style="background-color: #ffffff; border: 1px solid #e2e8f0; padding: 7px 12px; border-radius: 8px; text-align: center; font-size: 12px; font-weight: 500; color: #334155;">
            Shift: Dinner (17:00 - 22:00)
        </div>
    """, unsafe_allow_html=True)
with header_col3:
    st.markdown("""
        <div style="background-color: #7c3aed; color: white; padding: 7px 12px; border-radius: 8px; text-align: center; font-size: 12px; font-weight: 600;">
            🟢 Live Feed Active
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px; border-color: #e2e8f0;'>", unsafe_allow_html=True)

# --- METRICS ROW (3 Cards) ---
total_tables = len(st.session_state.tables)
available_count = len([t for t in st.session_state.tables if t["status"] == "available"])
reserved_count = total_tables - available_count
total_seats = sum([t["seats"] for t in st.session_state.tables])
booked_seats = sum([t["seats"] for t in st.session_state.tables if t["status"] == "reserved"])
occupancy_rate = int((booked_seats / total_seats) * 100) if total_seats > 0 else 0

mcol1, mcol2, mcol3 = st.columns(3)

with mcol1:
    st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #64748b; font-size: 13px; font-weight: 500;">Available Tables</span>
                <span style="color: #64748b; font-size: 16px;">📋</span>
            </div>
            <h2 style="margin: 10px 0 8px 0; color: #0f172a; font-size: 28px;">{available_count}</h2>
            <span style="background-color: #dcfce7; color: #166534; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">{available_count} FREE</span>
        </div>
    """, unsafe_allow_html=True)

with mcol2:
    st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #64748b; font-size: 13px; font-weight: 500;">Active Reservations</span>
                <span style="color: #64748b; font-size: 16px;">📅</span>
            </div>
            <h2 style="margin: 10px 0 8px 0; color: #0f172a; font-size: 28px;">{reserved_count}</h2>
            <span style="color: #64748b; font-size: 11px; font-weight: 600;">0 LIVE</span>
        </div>
    """, unsafe_allow_html=True)

with mcol3:
    st.markdown(f"""
        <div class="metric-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #64748b; font-size: 13px; font-weight: 500;">Current Occupancy</span>
                <span style="color: #64748b; font-size: 16px;">👤</span>
            </div>
            <h2 style="margin: 10px 0 8px 0; color: #0f172a; font-size: 28px;">{occupancy_rate}%</h2>
            <span style="color: #64748b; font-size: 11px; font-weight: 500;">{booked_seats} / {total_seats} SEATS</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- MAIN DASHBOARD LAYOUT (3 COLUMNS) ---
col_left, col_mid, col_right = st.columns([1.1, 1.1, 1.3])

with col_left:
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #0f172a; font-size: 16px;">Live Table Status</h4>
            <span style="font-size: 12px; color: #166534; font-weight: 500;">🟢 Monitor Seating</span>
        </div>
    """, unsafe_allow_html=True)
    
    for t in st.session_state.tables:
        badge_html = '<span class="badge-available">● AVAILABLE</span>' if t["status"] == "available" else '<span style="background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:6px; font-weight:600; font-size:11px;">● RESERVED</span>'
        
        st.markdown(f"""
            <div class="table-box">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <div style="background-color: #dcfce7; color: #166534; padding: 8px 12px; border-radius: 8px; font-weight: 700; font-size: 13px;">{t['code']}</div>
                    <div>
                        <strong style="color: #0f172a; font-size: 14px;">{t['name']}</strong><br>
                        <span style="color: #64748b; font-size: 12px;">{t['seats']} Seats</span>
                    </div>
                </div>
                <div>{badge_html}</div>
            </div>
        """, unsafe_allow_html=True)

with col_mid:
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h4 style="margin: 0; color: #0f172a; font-size: 16px;">Active Reservations</h4>
            <span style="font-size: 12px; color: #64748b; font-weight: 500;">0 Total</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.reservations:
        for r in st.session_state.reservations:
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px; margin-bottom: 10px;">
                    <div style="display: flex; justify-content: space-between;">
                        <strong style="color: #0f172a;">{r['Customer Name']}</strong>
                        <span style="font-size: 12px; color: #7c3aed; font-weight: 600;">Table ID: {r['Table ID']}</span>
                    </div>
                    <p style="margin: 4px 0 0 0; color: #64748b; font-size: 12px;">📞 {r['Phone']} | 🕒 {r['Timestamp']}</p>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background: white; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 45px 20px; text-align: center;">
                <div style="font-size: 24px; margin-bottom: 8px;">📋</div>
                <p style="color: #475569; font-size: 14px; font-weight: 500; margin-bottom: 4px;">No active reservations recorded yet</p>
                <p style="color: #94a3b8; font-size: 11px; margin: 0;">Use the Live Booking Desk to confirm a new reservation</p>
            </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("<h4 style='margin: 0 0 15px 0; color: #0f172a; font-size: 16px;'>Live Booking Desk</h4>", unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px;">
    """, unsafe_allow_html=True)
    
    with st.form("booking_desk_form"):
        st.markdown("<label style='font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px;'>ASSIGN TABLE</label>", unsafe_allow_html=True)
        available_tables = [t for t in st.session_state.tables if t["status"] == "available"]
        
        if available_tables:
            table_options = {f"{t['name']} ({t['seats']} Seats - Available)": t['id'] for t in available_tables}
            selected_label = st.selectbox("Assign Table Select", options=list(table_options.keys()), label_visibility="collapsed")
            selected_table_id = table_options[selected_label]
            
            st.markdown("<label style='font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-top: 12px; display: block;'>CUSTOMER NAME</label>", unsafe_allow_html=True)
            customer_name = st.text_input("Customer Name Input", value="Ashraf", label_visibility="collapsed")
            
            st.markdown("<label style='font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-top: 12px; display: block;'>CONTACT PHONE (INTERNATIONAL)</label>", unsafe_allow_html=True)
            
            phone_col1, phone_col2 = st.columns([1, 2.5])
            with phone_col1:
                st.text_input("CC", value="+1", disabled=True, label_visibility="collapsed")
            with phone_col2:
                phone_number = st.text_input("Phone Input", placeholder="(202) 555-0143", label_visibility="collapsed")
            
            st.markdown("<label style='font-size: 11px; font-weight: 700; color: #64748b; letter-spacing: 0.5px; margin-top: 12px; display: block;'>GUEST COUNT</label>", unsafe_allow_html=True)
            
            gc1, gc2, gc3, gc4 = st.columns(4)
            with gc1:
                b2 = st.form_submit_button("2", use_container_width=True)
            with gc2:
                b4 = st.form_submit_button("4", use_container_width=True)
            with gc3:
                b6 = st.form_submit_button("6", use_container_width=True)
            with gc4:
                b8 = st.form_submit_button("8", use_container_width=True)
            
            if b2: st.session_state.guest_count = 2
            if b4: st.session_state.guest_count = 4
            if b6: st.session_state.guest_count = 6
            if b8: st.session_state.guest_count = 8
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_btn = st.form_submit_button("➕ Confirm Reservation Table", use_container_width=True)
            
            if submit_btn:
                if not customer_name.strip() or not phone_number.strip():
                    st.error("Kripya customer name aur phone number bhariye.")
                else:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    for t in st.session_state.tables:
                        if t["id"] == selected_table_id:
                            t["status"] = "reserved"
                            st.session_state.reservations.append({
                                "Table ID": selected_table_id,
                                "Customer Name": customer_name,
                                "Phone": f"+1 {phone_number}",
                                "Timestamp": timestamp
                            })
                            st.success(f"Table successfully assigned to {customer_name}!")
                            st.rerun()
        else:
            st.warning("Sabhi tables abhi occupied hain.")
            
    st.markdown("</div>", unsafe_allow_html=True)
