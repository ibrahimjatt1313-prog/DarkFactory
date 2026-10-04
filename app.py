from flask import Flask, render_template_string, request, redirect, url_for, Response
from datetime import datetime
import io
import csv

app = Flask(__name__)

# ==========================================
# MOCK DATABASES
# ==========================================

MEMORY_TABLES = [
    {"id": 1, "code": "DT-01", "name": "Drive-Thru Lane 1", "seats": 4, "zone": "Drive-Thru", "status": "available", "icon": "fa-car"},
    {"id": 2, "code": "DT-02", "name": "Drive-Thru Lane 2", "seats": 4, "zone": "Drive-Thru", "status": "available", "icon": "fa-car"},
    {"id": 3, "code": "FC-101", "name": "Front Counter Station A", "seats": 2, "zone": "Front Counter", "status": "available", "icon": "fa-cash-register"},
    {"id": 4, "code": "FC-102", "name": "Front Counter Station B", "seats": 2, "zone": "Front Counter", "status": "available", "icon": "fa-cash-register"},
    {"id": 5, "code": "KS-01", "name": "Self-Order Kiosk Alpha", "seats": 1, "zone": "Kiosks", "status": "available", "icon": "fa-tablet-screen-button"},
    {"id": 6, "code": "KS-02", "name": "Self-Order Kiosk Beta", "seats": 1, "zone": "Kiosks", "status": "available", "icon": "fa-tablet-screen-button"},
    {"id": 7, "code": "DL-201", "name": "Global Dispatch Hub 1", "seats": 6, "zone": "Delivery Hub", "status": "available", "icon": "fa-motorcycle"},
    {"id": 8, "code": "VIP-01", "name": "Executive Lounge", "seats": 8, "zone": "VIP Lounge", "status": "available", "icon": "fa-champagne-glasses"}
]

MEMORY_RESERVATIONS = []
REGISTERED_USERS = []
CURRENT_SESSION_USER = {"name": None, "email": None, "logged_in": False}

table_id_counter = 9
reservation_id_counter = 101
MAX_TOTAL_STATIONS = 15

# ==========================================
# COMPACT & LUXURY UI TEMPLATE
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>L'Étoile Noire & Grand Gastronomy - Executive Suite</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-deep: #090a0f;
            --bg-card: #131620;
            --bg-card-hover: #1a1d2b;
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-brand: #6366f1;
            --accent-hover: #4f46e5;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --card-shadow: 0 8px 24px -6px rgba(0,0,0,0.4);
        }
        [data-theme="light"] {
            --bg-deep: #f1f5f9;
            --bg-card: #ffffff;
            --bg-card-hover: #f8fafc;
            --border-color: rgba(0, 0, 0, 0.08);
            --accent-brand: #4f46e5;
            --accent-hover: #4338ca;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --card-shadow: 0 8px 20px -4px rgba(0,0,0,0.05);
        }
        [data-theme="editorial"] {
            --bg-deep: #fcf9f2;
            --bg-card: #ffffff;
            --bg-card-hover: #f5f0e6;
            --border-color: rgba(44, 36, 29, 0.1);
            --accent-brand: #d97706;
            --accent-hover: #b45309;
            --text-main: #2c241d;
            --text-muted: #78716c;
            --card-shadow: 0 8px 24px -6px rgba(44, 36, 29, 0.08);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; transition: background-color 0.2s ease, color 0.2s ease; }
        body {
            background-color: var(--bg-deep);
            color: var(--text-main);
            font-family: 'Plus Jakarta Sans', sans-serif;
            min-height: 100vh;
            padding: 16px;
        }
        .wrapper { max-width: 1350px; margin: 0 auto; display: flex; flex-direction: column; gap: 14px; }
        
        /* Hero Header */
        .hero-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 14px 20px;
            box-shadow: var(--card-shadow);
            flex-wrap: wrap;
            gap: 12px;
        }
        .hero-title h1 {
            font-size: 18px;
            font-weight: 800;
            margin-bottom: 2px;
            background: linear-gradient(135deg, var(--text-main) 30%, var(--accent-brand) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .hero-title p { color: var(--accent-brand); font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; }
        .header-actions { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }
        
        .btn-action {
            background: var(--bg-deep);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 7px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
        }
        .btn-action:hover { border-color: var(--accent-brand); background: var(--bg-card-hover); }
        .btn-export { background: rgba(99, 102, 241, 0.1); border-color: rgba(99, 102, 241, 0.3); color: var(--accent-brand); }
        
        .server-badge {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #10b981;
            padding: 7px 12px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Metrics Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }
        @media(max-width: 900px) { .metrics-grid { grid-template-columns: 1fr 1fr; } }
        .metric-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 14px;
            box-shadow: var(--card-shadow);
        }
        .metric-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
        .metric-title { font-size: 9px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.8px; font-weight: 700; }
        .metric-value { font-size: 18px; font-weight: 800; }

        .notification-banner {
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: var(--accent-brand);
            padding: 10px 14px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        /* Compact Dashboard Grid */
        .dashboard-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 14px;
            align-items: start;
        }
        @media (max-width: 1024px) { .dashboard-grid { grid-template-columns: 1fr; } }
        
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 16px;
            box-shadow: var(--card-shadow);
        }
        .card h3 {
            font-size: 13px;
            margin-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-main);
        }
        .card h3 i { color: var(--accent-brand); }

        /* Zone Filter Tabs */
        .zone-tabs { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 10px; }
        .zone-tab {
            background: var(--bg-deep);
            border: 1px solid var(--border-color);
            color: var(--text-muted);
            padding: 5px 9px;
            border-radius: 6px;
            font-size: 10px;
            font-weight: 600;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 5px;
        }
        .zone-tab.active, .zone-tab:hover { background: var(--accent-brand); color: #fff; border-color: var(--accent-brand); }

        /* Stations Grid - Optimized for compactness */
        .tables-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 10px;
            max-height: 380px;
            overflow-y: auto;
            padding-right: 4px;
        }
        .table-box {
            background: var(--bg-deep);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 10px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .table-info-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }
        .table-icon-wrap { width: 28px; height: 28px; border-radius: 6px; background: rgba(99,102,241,0.1); display: flex; align-items: center; justify-content: center; color: var(--accent-brand); font-size: 12px; }
        .table-name { font-weight: 700; font-size: 11px; margin-top: 4px; }
        .table-zone { font-size: 8px; color: var(--text-muted); text-transform: uppercase; }
        
        .badge-avail { background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.25); padding: 2px 6px; border-radius: 4px; font-size: 8px; font-weight: 800; display: inline-flex; align-items: center; gap: 3px; }
        .badge-res { background: rgba(239, 68, 68, 0.12); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.25); padding: 2px 6px; border-radius: 4px; font-size: 8px; font-weight: 800; display: inline-flex; align-items: center; gap: 3px; }
        
        .table-meta { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; padding-top: 6px; border-top: 1px solid var(--border-color); font-size: 10px; color: var(--text-muted); }

        .btn-delete-station {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            color: #ef4444;
            padding: 3px 6px;
            border-radius: 4px;
            font-size: 9px;
            cursor: pointer;
        }
        .btn-delete-station:hover { background: rgba(239, 68, 68, 0.2); }

        /* Forms Styling */
        .right-column-stack { display: flex; flex-direction: column; gap: 14px; }
        .form-group { margin-bottom: 10px; }
        .form-group label { display: block; font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text-muted); margin-bottom: 4px; }
        .form-control {
            width: 100%;
            background: var(--bg-deep);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 8px 10px;
            border-radius: 8px;
            font-size: 11px;
            font-family: 'Plus Jakarta Sans', sans-serif;
            outline: none;
        }
        .form-control:focus { border-color: var(--accent-brand); box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.15); }
        
        /* FIX FOR DROP DOWN OPTIONS VISIBILITY */
        select.form-control option, select option {
            background: var(--bg-card) !important;
            color: var(--text-main) !important;
        }

        .phone-group { display: flex; gap: 6px; }
        
        .btn-luxury {
            background: linear-gradient(135deg, var(--accent-brand) 0%, var(--accent-hover) 100%);
            color: #ffffff;
            border: none;
            width: 100%;
            padding: 9px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 11px;
            cursor: pointer;
            margin-top: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .btn-luxury:hover { opacity: 0.95; }

        /* Ledger Table */
        .ledger-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px; }
        .search-input { background: var(--bg-deep); border: 1px solid var(--border-color); color: var(--text-main); padding: 7px 10px; border-radius: 7px; font-size: 11px; width: 220px; outline: none; }
        .search-input:focus { border-color: var(--accent-brand); }
        
        .archive-table { width: 100%; border-collapse: collapse; text-align: left; }
        .archive-table th { font-size: 9px; text-transform: uppercase; letter-spacing: 0.8px; color: var(--text-muted); padding: 8px 6px; border-bottom: 1px solid var(--border-color); font-weight: 700; }
        .archive-table td { padding: 9px 6px; border-bottom: 1px solid var(--border-color); font-size: 11px; }
        .archive-table tr:hover td { background: var(--bg-card-hover); }
        
        .btn-cancel {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.25);
            color: #ef4444;
            padding: 4px 8px;
            border-radius: 5px;
            font-size: 9px;
            font-weight: 700;
            cursor: pointer;
        }
        .btn-cancel:hover { background: rgba(239, 68, 68, 0.2); }
        .empty-state { text-align: center; color: var(--text-muted); padding: 18px; font-style: italic; font-size: 11px; }

        /* Modals */
        .modal-overlay {
            position: fixed; inset: 0;
            background: rgba(9, 10, 15, 0.8);
            backdrop-filter: blur(3px);
            display: none; align-items: center; justify-content: center;
            z-index: 100; padding: 16px;
        }
        .modal-card {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            width: 100%; max-width: 380px;
            padding: 20px;
            box-shadow: var(--card-shadow);
            position: relative;
        }
        .modal-close {
            position: absolute; top: 14px; right: 14px;
            background: none; border: none; color: var(--text-muted);
            font-size: 16px; cursor: pointer;
        }
        .modal-close:hover { color: var(--text-main); }
    </style>
    <script>
        function switchTheme(themeName) {
            document.documentElement.setAttribute("data-theme", themeName);
            localStorage.setItem("theme", themeName);
        }
        window.addEventListener("DOMContentLoaded", () => {
            const savedTheme = localStorage.getItem("theme") || "dark";
            document.documentElement.setAttribute("data-theme", savedTheme);
            const selector = document.getElementById("themeSelector");
            if(selector) selector.value = savedTheme;
        });

        function openModal(id) { document.getElementById(id).style.display = "flex"; }
        function closeModal(id) { document.getElementById(id).style.display = "none"; }
    </script>
</head>
<body>
    <div class="wrapper">
        <!-- Hero Header -->
        <div class="hero-header">
            <div class="hero-title">
                <h1>L'Étoile Noire & Grand Gastronomy</h1>
                <p><i class="fa-solid fa-crown"></i> Executive Tablekeeper & Concierge Suite</p>
            </div>
            <div class="header-actions">
                <!-- Theme Switcher with visibility fix -->
                <div class="btn-action" style="padding: 5px 10px;">
                    <i class="fa-solid fa-moon" style="color: var(--accent-brand);"></i>
                    <span style="font-size: 10px; font-weight: 700; text-transform: uppercase; color: var(--text-muted);">Theme:</span>
                    <select id="themeSelector" onchange="switchTheme(this.value)" style="background: transparent; border: none; color: var(--text-main); font-weight: 600; cursor: pointer; outline: none; font-family: 'Plus Jakarta Sans', sans-serif; font-size: 11px;">
                        <option value="dark">Dark Glass</option>
                        <option value="light">Light Clean</option>
                        <option value="editorial">Editorial Cream</option>
                    </select>
                </div>

                <a href="/export" class="btn-action btn-export"><i class="fa-solid fa-file-csv"></i> Reports</a>
                
                {% if current_user.logged_in %}
                    <div class="btn-action" style="background: rgba(16,185,129,0.1); color: #10b981; border-color: rgba(16,185,129,0.3);">
                        <i class="fa-solid fa-user-check"></i> {{ current_user.name }}
                    </div>
                    <a href="/logout" class="btn-action" style="color: #ef4444;"><i class="fa-solid fa-right-from-bracket"></i></a>
                {% else %}
                    <button onclick="openModal('loginModal')" class="btn-action"><i class="fa-solid fa-right-to-bracket"></i> Log in</button>
                    <button onclick="openModal('signupModal')" class="btn-action" style="background: var(--accent-brand); color: #fff; border-color: var(--accent-brand);">Sign up</button>
                {% endif %}

                <div class="server-badge"><i class="fa-solid fa-shield-halved"></i> Secure Cluster</div>
            </div>
        </div>

        <!-- Metrics Grid -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">Total Stations</span>
                    <i class="fa-solid fa-network-wired" style="color: var(--accent-brand); font-size: 12px;"></i>
                </div>
                <div class="metric-value">{{ metrics.total_suites }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">Utilization Rate</span>
                    <i class="fa-solid fa-chart-line" style="color: #10b981; font-size: 12px;"></i>
                </div>
                <div class="metric-value" style="color: #10b981;">{{ metrics.occupancy_rate }}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">Active Dispatch</span>
                    <i class="fa-solid fa-receipt" style="color: #f59e0b; font-size: 12px;"></i>
                </div>
                <div class="metric-value" style="color: #f59e0b;">{{ metrics.active_count }}</div>
            </div>
            <div class="metric-card">
                <div class="metric-header">
                    <span class="metric-title">Customer Traffic</span>
                    <i class="fa-solid fa-users" style="color: #3b82f6; font-size: 12px;"></i>
                </div>
                <div class="metric-value">{{ metrics.total_guests }}</div>
            </div>
        </div>

        {% if notification %}
        <div class="notification-banner">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <div><strong>System Notification:</strong> {{ notification }}</div>
        </div>
        {% endif %}

        <!-- Dashboard Layout -->
        <div class="dashboard-grid">
            <!-- Left: Floor Plan & Stations Matrix -->
            <div class="card">
                <h3><i class="fa-solid fa-map-location-dot"></i> Live Floor & Station Matrix</h3>
                <div class="zone-tabs">
                    <a href="/?zone=All" class="zone-tab {% if current_zone == 'All' %}active{% endif %}"><i class="fa-solid fa-border-all"></i> All</a>
                    <a href="/?zone=Drive-Thru" class="zone-tab {% if current_zone == 'Drive-Thru' %}active{% endif %}"><i class="fa-solid fa-car"></i> Drive-Thru</a>
                    <a href="/?zone=Front%20Counter" class="zone-tab {% if current_zone == 'Front Counter' %}active{% endif %}"><i class="fa-solid fa-cash-register"></i> Counter</a>
                    <a href="/?zone=Kiosks" class="zone-tab {% if current_zone == 'Kiosks' %}active{% endif %}"><i class="fa-solid fa-tablet-screen-button"></i> Kiosks</a>
                    <a href="/?zone=Delivery%20Hub" class="zone-tab {% if current_zone == 'Delivery Hub' %}active{% endif %}"><i class="fa-solid fa-motorcycle"></i> Delivery</a>
                    <a href="/?zone=VIP%20Lounge" class="zone-tab {% if current_zone == 'VIP Lounge' %}active{% endif %}"><i class="fa-solid fa-champagne-glasses"></i> VIP</a>
                </div>

                <div class="tables-container">
                    {% if tables %}
                        {% for t in tables %}
                        <div class="table-box">
                            <div>
                                <div class="table-info-top">
                                    <div class="table-icon-wrap"><i class="fa-solid {{ t.icon }}"></i></div>
                                    <div>
                                        {% if t.status == 'available' %}
                                            <span class="badge-avail"><i class="fa-solid fa-check"></i> READY</span>
                                        {% else %}
                                            <span class="badge-res"><i class="fa-solid fa-lock"></i> ACTIVE</span>
                                        {% endif %}
                                    </div>
                                </div>
                                <div class="table-name">{{ t.name }}</div>
                                <div class="table-zone">{{ t.zone }}</div>
                            </div>
                            <div class="table-meta">
                                <span>Code: <strong>{{ t.code }}</strong></span>
                                <div style="display: flex; align-items: center; gap: 6px;">
                                    <span><i class="fa-solid fa-user-group"></i> {{ t.seats }}</span>
                                    <form method="POST" action="/delete-table/{{ t.id }}" style="margin: 0;" onsubmit="return confirm('Remove station {{ t.code }}?');">
                                        <button type="submit" class="btn-delete-station" title="Remove"><i class="fa-solid fa-trash-can"></i></button>
                                    </form>
                                </div>
                            </div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="empty-state" style="grid-column: 1 / -1;"><i class="fa-solid fa-folder-open"></i> No stations configured in this zone.</div>
                    {% endif %}
                </div>
            </div>

            <!-- Right: Order Dispatch & Station Registration -->
            <div class="right-column-stack">
                <div class="card">
                    <h3><i class="fa-solid fa-paper-plane"></i> Order Dispatch Desk</h3>
                    <form method="POST" action="/book">
                        <div class="form-group">
                            <label>Select Ready Station</label>
                            <select name="table_id" class="form-control" required>
                                {% set available_found = namespace(val=false) %}
                                {% for t in MEMORY_TABLES %}
                                    {% if t.status == 'available' %}
                                        {% set available_found.val = true %}
                                        <option value="{{ t.id }}">{{ t.name }} (Cap: {{ t.seats }})</option>
                                    {% endif %}
                                {% endfor %}
                                {% if not available_found.val %}
                                    <option value="" disabled selected>All stations occupied</option>
                                {% endif %}
                            </select>
                        </div>

                        <div class="form-group">
                            <label>Guest Name</label>
                            <input type="text" name="customer_name" class="form-control" placeholder="Guest name..." required>
                        </div>

                        <div class="form-group">
                            <label>Phone Number</label>
                            <div class="phone-group">
                                <select name="country_code" class="form-control" style="width: 85px;">
                                    <option value="+92" selected>+92</option>
                                    <option value="+971">+971</option>
                                    <option value="+44">+44</option>
                                    <option value="+1">+1</option>
                                </select>
                                <input type="tel" name="phone_number" class="form-control" placeholder="300 1234567" required>
                            </div>
                        </div>

                        <div class="form-group">
                            <label>Party Size (Max 50)</label>
                            <input type="number" name="guests" class="form-control" value="2" min="1" max="50" required>
                        </div>

                        <button type="submit" class="btn-luxury">
                            <i class="fa-solid fa-bolt"></i> Dispatch Order
                        </button>
                    </form>
                </div>

                <div class="card">
                    <h3><i class="fa-solid fa-circle-plus"></i> Register Station</h3>
                    <form method="POST" action="/add-table">
                        <div class="form-group">
                            <label>Code (e.g., APX-03)</label>
                            <input type="text" name="code" class="form-control" placeholder="APX-03" required>
                        </div>
                        <div class="form-group">
                            <label>Name</label>
                            <input type="text" name="name" class="form-control" placeholder="Express Counter 3" required>
                        </div>
                        <div class="form-group">
                            <label>Zone</label>
                            <select name="zone" class="form-control" required>
                                <option value="Drive-Thru">Drive-Thru</option>
                                <option value="Front Counter">Front Counter</option>
                                <option value="Kiosks">Kiosks</option>
                                <option value="Delivery Hub">Delivery Hub</option>
                                <option value="VIP Lounge">VIP Lounge</option>
                            </select>
                        </div>
                        <button type="submit" class="btn-luxury" style="background: rgba(99, 102, 241, 0.12); color: var(--accent-brand); border: 1px solid rgba(99, 102, 241, 0.3);">
                            <i class="fa-solid fa-plus"></i> Add Station
                        </button>
                    </form>
                </div>
            </div>
        </div>

        <!-- Active Operations Ledger -->
        <div class="card">
            <div class="ledger-header">
                <h3><i class="fa-solid fa-list-check"></i> Active Operations Ledger</h3>
                <form method="GET" action="/" style="margin: 0;">
                    <input type="hidden" name="zone" value="{{ current_zone }}">
                    <input type="text" name="search" class="search-input" placeholder="🔍 Search guest or phone..." value="{{ search_query }}">
                </form>
            </div>

            {% if reservations %}
                <table class="archive-table">
                    <thead>
                        <tr>
                            <th>Guest / Fleet</th>
                            <th>Station</th>
                            <th>Zone</th>
                            <th>Phone</th>
                            <th>Size</th>
                            <th>Timestamp</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for r in reservations %}
                        <tr>
                            <td><strong>{{ r.customer_name }}</strong></td>
                            <td>{{ r.table_name }} (<span style="color: var(--accent-brand);">{{ r.code }}</span>)</td>
                            <td>{{ r.zone }}</td>
                            <td>{{ r.phone }}</td>
                            <td>{{ r.guests }}</td>
                            <td>{{ r.timestamp }}</td>
                            <td>
                                <form method="POST" action="/cancel/{{ r.id }}" style="margin: 0;">
                                    <button type="submit" class="btn-cancel"><i class="fa-solid fa-rotate-left"></i> Release</button>
                                </form>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            {% else %}
                <div class="empty-state"><i class="fa-solid fa-inbox"></i> No active orders found in the ledger.</div>
            {% endif %}
        </div>
    </div>

    <!-- Real Signup Modal -->
    <div id="signupModal" class="modal-overlay">
        <div class="modal-card">
            <button onclick="closeModal('signupModal')" class="modal-close">&times;</button>
            <h3 style="border:none; margin-bottom: 6px; padding:0;"><i class="fa-solid fa-user-plus"></i> Create Real Account</h3>
            <p style="font-size: 11px; color: var(--text-muted); margin-bottom: 12px;">Register with your original email address.</p>
            <form method="POST" action="/signup">
                <div class="form-group">
                    <label>Full Name</label>
                    <input type="text" name="name" class="form-control" placeholder="Muhammad Ibraheem" required>
                </div>
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" name="email" class="form-control" placeholder="name@example.com" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" class="form-control" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn-luxury" style="margin-top: 6px;">Register &rarr;</button>
            </form>
        </div>
    </div>

    <!-- Real Login Modal -->
    <div id="loginModal" class="modal-overlay">
        <div class="modal-card">
            <button onclick="closeModal('loginModal')" class="modal-close">&times;</button>
            <h3 style="border:none; margin-bottom: 6px; padding:0;"><i class="fa-solid fa-right-to-bracket"></i> Executive Login</h3>
            <p style="font-size: 11px; color: var(--text-muted); margin-bottom: 12px;">Enter your registered credentials.</p>
            <form method="POST" action="/login">
                <div class="form-group">
                    <label>Email Address</label>
                    <input type="email" name="email" class="form-control" placeholder="name@example.com" required>
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" name="password" class="form-control" placeholder="••••••••" required>
                </div>
                <button type="submit" class="btn-luxury" style="margin-top: 6px;">Log in &rarr;</button>
            </form>
        </div>
    </div>
</body>
</html>
"""

# ==========================================
# FLASK ROUTE CONTROLLERS
# ==========================================

@app.route("/")
def index():
    zone_filter = request.args.get("zone", "All")
    search_query = request.args.get("search", "").strip()
    notification = request.args.get("note", "")
    
    if zone_filter == "All":
        tables = MEMORY_TABLES
    else:
        tables = [t for t in MEMORY_TABLES if t["zone"] == zone_filter]
        
    total_suites = len(MEMORY_TABLES)
    reserved_suites = sum(1 for t in MEMORY_TABLES if t["status"] == "reserved")
    occupancy_rate = round((reserved_suites / total_suites * 100), 1) if total_suites > 0 else 0
    total_guests = sum(int(r["guests"]) for r in MEMORY_RESERVATIONS)
    active_count = len(MEMORY_RESERVATIONS)
    
    metrics = {
        "total_suites": total_suites,
        "occupancy_rate": occupancy_rate,
        "active_count": active_count,
        "total_guests": total_guests
    }
    
    reservations = MEMORY_RESERVATIONS
    if search_query:
        reservations = [
            r for r in MEMORY_RESERVATIONS 
            if search_query.lower() in r["customer_name"].lower() or search_query in r["phone"]
        ]
        
    return render_template_string(
        HTML_TEMPLATE,
        tables=tables,
        reservations=reservations,
        metrics=metrics,
        current_zone=zone_filter,
        search_query=search_query,
        notification=notification,
        MEMORY_TABLES=MEMORY_TABLES,
        current_user=CURRENT_SESSION_USER
    )

@app.route("/signup", methods=["POST"])
def signup():
    global CURRENT_SESSION_USER
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    
    if any(u["email"] == email for u in REGISTERED_USERS):
        return redirect(url_for("index", note="Error: Email is already registered. Please log in."))
        
    user = {"name": name, "email": email, "password": password}
    REGISTERED_USERS.append(user)
    
    CURRENT_SESSION_USER = {"name": name, "email": email, "logged_in": True}
    return redirect(url_for("index", note=f"Welcome {name}! Account successfully created and logged in."))

@app.route("/login", methods=["POST"])
def login():
    global CURRENT_SESSION_USER
    email = request.form.get("email")
    password = request.form.get("password")
    
    user = next((u for u in REGISTERED_USERS if u["email"] == email and u["password"] == password), None)
    if user:
        CURRENT_SESSION_USER = {"name": user["name"], "email": user["email"], "logged_in": True}
        return redirect(url_for("index", note=f"Welcome back, {user['name']}!"))
    else:
        return redirect(url_for("index", note="Error: Invalid email or password. Please sign up if you don't have an account."))

@app.route("/logout")
def logout():
    global CURRENT_SESSION_USER
    CURRENT_SESSION_USER = {"name": None, "email": None, "logged_in": False}
    return redirect(url_for("index", note="Successfully logged out."))

@app.route("/add-table", methods=["POST"])
def add_table():
    global table_id_counter
    if len(MEMORY_TABLES) >= MAX_TOTAL_STATIONS:
        return redirect(url_for("index", note=f"Error: Max stations limit ({MAX_TOTAL_STATIONS}) reached."))

    code = request.form.get("code")
    name = request.form.get("name")
    zone = request.form.get("zone")
    
    if any(t["code"] == code for t in MEMORY_TABLES):
        return redirect(url_for("index", note=f"Error: Station code {code} already exists."))

    icon_map = {
        "Drive-Thru": "fa-car",
        "Front Counter": "fa-cash-register",
        "Kiosks": "fa-tablet-screen-button",
        "Delivery Hub": "fa-motorcycle",
        "VIP Lounge": "fa-champagne-glasses"
    }
    
    new_table = {
        "id": table_id_counter,
        "code": code,
        "name": name,
        "seats": 4,
        "zone": zone,
        "status": "available",
        "icon": icon_map.get(zone, "fa-utensils")
    }
    MEMORY_TABLES.append(new_table)
    table_id_counter += 1
    return redirect(url_for("index", note=f"Station {name} registered successfully."))

@app.route("/delete-table/<int:table_id>", methods=["POST"])
def delete_table(table_id):
    global MEMORY_TABLES, MEMORY_RESERVATIONS
    MEMORY_TABLES = [t for t in MEMORY_TABLES if t["id"] != table_id]
    MEMORY_RESERVATIONS = [r for r in MEMORY_RESERVATIONS if r["table_id"] != table_id]
    return redirect(url_for("index", note="Station removed successfully."))

@app.route("/book", methods=["POST"])
def book():
    global reservation_id_counter
    table_id_str = request.form.get("table_id")
    customer_name = request.form.get("customer_name")
    country_code = request.form.get("country_code", "+92")
    phone_number = request.form.get("phone_number")
    full_phone = f"{country_code} {phone_number}"
    
    try:
        guests = int(request.form.get("guests", 2))
    except ValueError:
        guests = 2
        
    if not table_id_str:
        return redirect(url_for("index", note="Please select an available station."))
        
    table_id = int(table_id_str)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    target_table = None
    for t in MEMORY_TABLES:
        if t["id"] == table_id:
            if t["status"] == "reserved":
                return redirect(url_for("index", note="Station is already occupied."))
            t["status"] = "reserved"
            target_table = t
            break
            
    if target_table:
        reservation = {
            "id": reservation_id_counter,
            "table_id": table_id,
            "table_name": target_table["name"],
            "code": target_table["code"],
            "zone": target_table["zone"],
            "customer_name": customer_name,
            "phone": full_phone,
            "guests": guests,
            "timestamp": timestamp
        }
        MEMORY_RESERVATIONS.insert(0, reservation)
        reservation_id_counter += 1
        
    return redirect(url_for("index", note=f"Order dispatched for {customer_name}."))

@app.route("/cancel/<int:res_id>", methods=["POST"])
def cancel(res_id):
    global MEMORY_RESERVATIONS
    target_res = next((r for r in MEMORY_RESERVATIONS if r["id"] == res_id), None)
    if target_res:
        t_id = target_res["table_id"]
        for t in MEMORY_TABLES:
            if t["id"] == t_id:
                t["status"] = "available"
                break
        MEMORY_RESERVATIONS = [r for r in MEMORY_RESERVATIONS if r["id"] != res_id]
    return redirect(url_for("index", note="Station released successfully."))

@app.route("/export")
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Order ID", "Guest Name", "Station Name", "Code", "Zone", "Phone", "Size", "Timestamp"])
    for r in MEMORY_RESERVATIONS:
        writer.writerow([r["id"], r["customer_name"], r["table_name"], r["code"], r["zone"], r["phone"], r["guests"], r["timestamp"]])
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=letoile_noire_operations_ledger.csv"}
    )

if __name__ == "__main__":
    app.run(debug=True)