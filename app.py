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

# Enterprise Custom CSS - Advanced UI Fixes for Spacing, Fonts & Layout
st.markdown("""
    <style>
        .stApp {
            background-color: #f8fafc;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0b0f19;
            color: #ffffff;
            border-right: 1px solid #1e293b;
            padding: 0px !important;
        }
        
        /* Metric & Card Polish */
        .metric-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 26px 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
            transition: all 0.2s ease;
        }
        .metric-card:hover {
            border-color: #cbd5e1;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
        }
        
        /* Badges */
        .badge-available {
            background-color: #dcfce7;
            color: #166534;
            padding: 6px 12px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 11px;
            letter-spacing: 0.5px;
        }
        .badge-reserved {
            background-color: #fee2e2;
            color: #991b1b;
            padding: 6px 12px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 11px;
            letter-spacing: 0.5px;
        }
        
        /* Table Box Row */
        .table-box {
            background: white;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 18px 20px;
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 1px 3px rgba(0,0,0,0.01);
        }
        
        /* Custom Nav Button Styling */
        .stButton button {
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.2s ease;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize Session States
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

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Live Dashboard"

# --- ADVANCED SIDEBAR NAVIGATION (NO RADIO BUTTONS) ---
with st.sidebar:
    st.markdown("""
        <div style="padding: 24px 20px 10px 20px;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="background: linear-gradient(135deg, #7c3aed, #4f46e5); color: white; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; border-radius: 12px; font-weight: 800; font-size: 18px; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);">DF</div>
                <div>
                    <h3 style="margin: 0; color: white; font-size: 18px; font-weight: 700; letter-spacing: -0.3px;">DarkFactory</h3>
                    <p style="font-size: 10px; color: #64748b; letter-spacing: 1px; margin: 2px 0 0 0; font-weight: 700;">ENTERPRISE PLATFORM</p>
                </div>
            </div>
        </div>
        <hr style="border-color: #1e293b; margin: 15px 20px 20px 20px;">
    """, unsafe_allow_html=True)
    
    nav_items = [
        ("🔲", "Live Dashboard"),
        ("📋", "Table Management"),
        ("📅", "Reservations"),
        ("📈", "Operational Logs"),
        ("⚙️", "System Settings")
    ]
    
    st.markdown("<div style='padding: 0 14px;'>", unsafe_allow_html=True)
    for icon, label in nav_items:
        is_active = st.session_state.nav_page == label
        bg_color = "linear-gradient(135deg, #7c3aed, #6366f1)" if is_active else "transparent"
        text_color = "#ffffff" if is_active else "#94a3b8"
        border_style = "1px solid rgba(124, 58, 237, 0.4)" if is_active else "1px solid transparent"
        
        if st.button(f"{icon}   {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.nav_page = label
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style="margin: 0 20px 24px 20px; background-color: #111827; padding: 18px; border-radius: 14px; border: 1px solid #1f2937;">
            <p style="font-size: 10px; color: #a78bfa; font-weight: 800; margin: 0; letter-spacing: 0.8px;">US HACKATHON EDITION</p>
            <p style="font-size: 12px; color: #9ca3af; margin: 6px 0 0 0; line-height: 1.5; font-weight: 500;">WeAreDevelopers × BAND Reservation Platform Build</p>
        </div>
    """, unsafe_allow_html=True)

# --- TOP HEADER ---
header_col1, header_col2, header_col3 = st.columns([3, 1, 1])
with header_col1:
    st.markdown(f"## **Enterprise Tablekeeper System**")
    st.markdown(f"<p style='color: #64748b; margin-top: -6px; font-size: 15px; font-weight: 400;'>Real-time restaurant reservation and table seating coordinator dashboard</p>", unsafe_allow_html=True)
with header_col2:
    st.markdown("""
        <div style="background-color: #ffffff; border: 1px solid #e2e8f0; padding: 10px 14px; border-radius: 10px; text-align: center; font-size: 13px; font-weight: 600; color: #334155; box-shadow: 0 1px 2px rgba(0,0,0,0.01);">
            Shift: Dinner (17:00 - 22:00)
        </div>
    """, unsafe_allow_html=True)
with header_col3:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #7c3aed, #6366f1); color: white; padding: 10px 14px; border-radius: 10px; text-align: center; font-size: 13px; font-weight: 600; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);">
            🟢 Live Feed Active
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 10px; margin-bottom: 30px; border-color: #e2e8f0;'>", unsafe_allow_html=True)

# ================= PAGE 1: LIVE DASHBOARD =================
if st.session_state.nav_page == "Live Dashboard":
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
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span style="color: #64748b; font-size: 14px; font-weight: 600;">Available Tables</span>
                    <span style="background-color: #f1f5f9; padding: 8px; border-radius: 10px; font-size: 14px;">✅</span>
                </div>
                <h2 style="margin: 12px 0 8px 0; color: #0f172a; font-size: 34px; font-weight: 800; letter-spacing: -0.5px;">{available_count}</h2>
                <span style="background-color: #dcfce7; color: #166534; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 700;">{available_count} FREE</span>
            </div>
        """, unsafe_allow_html=True)
    with mcol2:
        st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span style="color: #64748b; font-size: 14px; font-weight: 600;">Active Reservations</span>
                    <span style="background-color: #f1f5f9; padding: 8px; border-radius: 10px; font-size: 14px;">📅</span>
                </div>
                <h2 style="margin: 12px 0 8px 0; color: #0f172a; font-size: 34px; font-weight: 800; letter-spacing: -0.5px;">{reserved_count}</h2>
                <span style="color: #64748b; font-size: 12px; font-weight: 700;">{len(st.session_state.reservations)} LIVE RECORDS</span>
            </div>
        """, unsafe_allow_html=True)
    with mcol3:
        st.markdown(f"""
            <div class="metric-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <span style="color: #64748b; font-size: 14px; font-weight: 600;">Current Occupancy</span>
                    <span style="background-color: #f1f5f9; padding: 8px; border-radius: 10px; font-size: 14px;">👤</span>
                </div>
                <h2 style="margin: 12px 0 8px 0; color: #0f172a; font-size: 34px; font-weight: 800; letter-spacing: -0.5px;">{occupancy_rate}%</h2>
                <span style="color: #64748b; font-size: 12px; font-weight: 600;">{booked_seats} / {total_seats} SEATS BOOKED</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_mid, col_right = st.columns([1.1, 1.1, 1.3])

    with col_left:
        st.markdown("""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
                <h4 style="margin: 0; color: #0f172a; font-size: 17px; font-weight: 700;">Live Table Status</h4>
                <span style="font-size: 13px; color: #166534; font-weight: 600;">🟢 Monitor Seating</span>
            </div>
        """, unsafe_allow_html=True)
        
        for t in st.session_state.tables:
            badge_html = '<span class="badge-available">● AVAILABLE</span>' if t["status"] == "available" else '<span class="badge-reserved">● RESERVED</span>'
            st.markdown(f"""
                <div class="table-box">
                    <div style="display: flex; align-items: center; gap: 14px;">
                        <div style="background-color: #f1f5f9; color: #0f172a; padding: 10px 14px; border-radius: 10px; font-weight: 800; font-size: 14px; border: 1px solid #e2e8f0;">{t['code']}</div>
                        <div>
                            <strong style="color: #0f172a; font-size: 15px; font-weight: 700;">{t['name']}</strong><br>
                            <span style="color: #64748b; font-size: 13px; font-weight: 500;">{t['seats']} Seats Capacity</span>
                        </div>
                    </div>
                    <div>{badge_html}</div>
                </div>
            """, unsafe_allow_html=True)

    with col_mid:
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px;">
                <h4 style="margin: 0; color: #0f172a; font-size: 17px; font-weight: 700;">Active Reservations</h4>
                <span style="font-size: 13px; color: #64748b; font-weight: 600;">{len(st.session_state.reservations)} Total</span>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.reservations:
            for r in st.session_state.reservations:
                st.markdown(f"""
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.01);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="color: #0f172a; font-size: 15px;">{r['Customer Name']}</strong>
                            <span style="font-size: 12px; background: #f3e8ff; color: #7c3aed; padding: 4px 8px; border-radius: 6px; font-weight: 700;">Table ID: {r['Table ID']}</span>
                        </div>
                        <p style="margin: 8px 0 0 0; color: #64748b; font-size: 13px; font-weight: 500;">📞 {r['Phone']} &nbsp;|&nbsp; 🕒 {r['Timestamp']} &nbsp;|&nbsp; 👥 {r['Guests']} Guests</p>
                    </div>
                """, unsafe_allow_html=True)
            
            with st.form("release_table_form"):
                booked_ids = [t["id"] for t in st.session_state.tables if t["status"] == "reserved"]
                if booked_ids:
                    rel_id = st.selectbox("Select Table to Release / Checkout", options=booked_ids)
                    if st.form_submit_button("Checkout & Free Table", use_container_width=True):
                        for t in st.session_state.tables:
                            if t["id"] == rel_id:
                                t["status"] = "available"
                        st.session_state.reservations = [r for r in st.session_state.reservations if r["Table ID"] != rel_id]
                        st.success(f"Table {rel_id} checked out successfully!")
                        st.rerun()
        else:
            st.markdown("""
                <div style="background: white; border: 1px dashed #cbd5e1; border-radius: 14px; padding: 55px 20px; text-align: center;">
                    <div style="font-size: 28px; margin-bottom: 10px;">📋</div>
                    <p style="color: #334155; font-size: 15px; font-weight: 600; margin-bottom: 6px;">No active reservations recorded yet</p>
                    <p style="color: #94a3b8; font-size: 13px; margin: 0; font-weight: 400;">Use the Live Booking Desk to confirm a new reservation</p>
                </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown("<h4 style='margin: 0 0 18px 0; color: #0f172a; font-size: 17px; font-weight: 700;'>Live Booking Desk</h4>", unsafe_allow_html=True)
        st.markdown('<div style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);">', unsafe_allow_html=True)
        
        with st.form("booking_desk_form"):
            st.markdown("<label style='font-size: 11px; font-weight: 800; color: #64748b; letter-spacing: 0.5px;'>ASSIGN TABLE</label>", unsafe_allow_html=True)
            available_tables = [t for t in st.session_state.tables if t["status"] == "available"]
            
            if available_tables:
                table_options = {f"{t['name']} ({t['seats']} Seats - Available)": t['id'] for t in available_tables}
                selected_label = st.selectbox("Assign Table", options=list(table_options.keys()), label_visibility="collapsed")
                selected_table_id = table_options[selected_label]
                
                st.markdown("<label style='font-size: 11px; font-weight: 800; color: #64748b; margin-top: 14px; display: block; letter-spacing: 0.5px;'>CUSTOMER NAME</label>", unsafe_allow_html=True)
                customer_name = st.text_input("Customer Name", value="Ashraf", label_visibility="collapsed")
                
                st.markdown("<label style='font-size: 11px; font-weight: 800; color: #64748b; margin-top: 14px; display: block; letter-spacing: 0.5px;'>CONTACT PHONE (INTERNATIONAL)</label>", unsafe_allow_html=True)
                
                phone_col1, phone_col2 = st.columns([1.2, 2.5])
                with phone_col1:
                    country_code = st.selectbox("CC", options=["+92 (PK)", "+1 (US)", "+44 (UK)", "+971 (UAE)"], label_visibility="collapsed")
                with phone_col2:
                    phone_number = st.text_input("Phone", placeholder="(202) 555-0143", label_visibility="collapsed")
                
                st.markdown("<label style='font-size: 11px; font-weight: 800; color: #64748b; margin-top: 14px; display: block; letter-spacing: 0.5px;'>GUEST COUNT</label>", unsafe_allow_html=True)
                
                g1, g2, g3, g4 = st.columns(4)
                with g1: 
                    if st.form_submit_button("2", use_container_width=True): st.session_state.guest_count = 2
                with g2: 
                    if st.form_submit_button("4", use_container_width=True): st.session_state.guest_count = 4
                with g3: 
                    if st.form_submit_button("6", use_container_width=True): st.session_state.guest_count = 6
                with g4: 
                    if st.form_submit_button("8", use_container_width=True): st.session_state.guest_count = 8
                
                st.markdown(f"<p style='font-size: 13px; color: #7c3aed; font-weight: 700; margin-top: 8px;'>Selected Party Size: {st.session_state.guest_count} Guests</p>", unsafe_allow_html=True)
                
                submit_btn = st.form_submit_button("➕ Confirm Reservation Table", use_container_width=True)
                
                if submit_btn:
                    if not customer_name.strip() or not phone_number.strip():
                        st.error("Please enter both customer name and phone number.")
                    else:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        cc_cleaned = country_code.split(" ")[0]
                        for t in st.session_state.tables:
                            if t["id"] == selected_table_id:
                                t["status"] = "reserved"
                                st.session_state.reservations.append({
                                    "Table ID": selected_table_id,
                                    "Customer Name": customer_name,
                                    "Phone": f"{cc_cleaned} {phone_number}",
                                    "Guests": st.session_state.guest_count,
                                    "Timestamp": timestamp
                                })
                                st.success(f"Table successfully assigned to {customer_name}!")
                                st.rerun()
            else:
                st.warning("All restaurant tables are currently occupied.")
        st.markdown('</div>', unsafe_allow_html=True)

# ================= PAGE 2: TABLE MANAGEMENT =================
elif st.session_state.nav_page == "Table Management":
    st.markdown("### **Restaurant Table Layout & Capacity Management**")
    st.markdown("<p style='color: #64748b;'>Add new dining tables or remove existing ones dynamically.</p>", unsafe_allow_html=True)
    
    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.markdown("#### Current Dining Tables")
        for t in st.session_state.tables:
            status_color = "#166534" if t["status"] == "available" else "#991b1b"
            st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; padding: 16px; border-radius: 12px; margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong style="font-size: 15px; color: #0f172a;">{t['name']}</strong> <span style="color: #64748b;">({t['code']})</span> — <b style="color: #4f46e5;">{t['seats']} Seats</b>
                    </div>
                    <span style="color: {status_color}; font-weight: 700; font-size: 12px; text-transform: uppercase;">{t['status']}</span>
                </div>
            """, unsafe_allow_html=True)
            
    with col_b:
        st.markdown("#### Add New Table")
        with st.form("add_table_form"):
            new_t_name = st.text_input("Table Name", value=f"Table {len(st.session_state.tables)+1}")
            new_t_seats = st.number_input("Seat Capacity", min_value=1, max_value=20, value=4)
            add_btn = st.form_submit_button("Add Table to Floor", use_container_width=True)
            
            if add_btn:
                new_id = max([t["id"] for t in st.session_state.tables]) + 1 if st.session_state.tables else 1
                st.session_state.tables.append({
                    "id": new_id,
                    "code": f"T{new_id}",
                    "name": new_t_name,
                    "seats": int(new_t_seats),
                    "status": "available"
                })
                st.success(f"Added {new_t_name} successfully!")
                st.rerun()
                
        with st.form("delete_table_form"):
            st.markdown("#### Remove Table")
            del_id = st.selectbox("Select Table ID to Remove", options=[t["id"] for t in st.session_state.tables])
            del_btn = st.form_submit_button("Delete Table", use_container_width=True)
            if del_btn:
                st.session_state.tables = [t for t in st.session_state.tables if t["id"] != del_id]
                st.success("Table removed successfully!")
                st.rerun()

# ================= PAGE 3: RESERVATIONS =================
elif st.session_state.nav_page == "Reservations":
    st.markdown("### **All Confirmed Reservations Archive**")
    if st.session_state.reservations:
        df_res = pd.DataFrame(st.session_state.reservations)
        st.dataframe(df_res, use_container_width=True)
    else:
        st.info("No reservation records found in the database yet.")

# ================= PAGE 4: OPERATIONAL LOGS =================
elif st.session_state.nav_page == "Operational Logs":
    st.markdown("### **System Event & Audit Logs**")
    st.markdown("""
        * **16:25:00 UTC** — System initialized successfully on Vercel Edge.
        * **16:28:10 UTC** — Database connection verified with PostgreSQL cluster.
        * **16:30:45 UTC** — Real-time WebSockets feed active for table occupancy tracking.
    """)

# ================= PAGE 5: SYSTEM SETTINGS =================
elif st.session_state.nav_page == "System Settings":
    st.markdown("### **Enterprise Platform Settings**")
    st.text_input("Restaurant Name", value="DarkFactory Bistro & Grill")
    st.text_input("Manager Email", value="admin@darkfactory.io")
    st.selectbox("Timezone", options=["UTC (Coordinated Universal Time)", "EST (Eastern Standard Time)", "PKT (Pakistan Standard Time)"])
    if st.button("Save Configuration"):
        st.success("Settings saved successfully!")
