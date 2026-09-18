from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import os

app = FastAPI(title="DarkFactory Enterprise Dashboard", version="2.3.0")

# In-memory storage updated for a large enterprise restaurant capacity
RESERVATIONS = []
TABLES = [
    {"id": "T1", "seats": 2, "status": "Available"},
    {"id": "T2", "seats": 4, "status": "Available"},
    {"id": "T3", "seats": 4, "status": "Available"},
    {"id": "T4", "seats": 6, "status": "Available"},
    {"id": "T5", "seats": 6, "status": "Available"},
    {"id": "T6", "seats": 8, "status": "Available"},
    {"id": "T7", "seats": 8, "status": "Available"},
    {"id": "T8", "seats": 10, "status": "Available"},
    {"id": "T9", "seats": 12, "status": "Available"},
    {"id": "T10", "seats": 12, "status": "Available"}
]

@app.get("/", response_class=HTMLResponse)
async def dashboard(tab: str = "dashboard"):
    
    content_html = ""
    total_capacity = sum(t["seats"] for t in TABLES)
    
    if tab == "dashboard":
        available_count = sum(1 for t in TABLES if t["status"] == "Available")
        booked_seats = sum(t["seats"] for t in TABLES if t["status"] == "Booked")
        occupancy = int((booked_seats / total_capacity) * 100) if total_capacity > 0 else 0
        
        tables_options = "".join([f'<option value="{t["id"]}" {"disabled" if t["status"]=="Booked" else ""}>{t["id"]} ({t["seats"]} Seats - {t["status"]})</option>' for t in TABLES])
        reservations_list = "".join([f'<div class="p-3 bg-slate-800/50 rounded-xl border border-slate-700/50 flex justify-between items-center text-sm"><div><span class="font-semibold text-white">{r["name"]}</span> <span class="text-xs text-slate-400 block">Table {r["table"]} • {r["guests"]} Guests • {r["country_code"]} {r["phone"]}</span></div><span class="px-2.5 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs rounded-full font-medium">Confirmed</span></div>' for r in RESERVATIONS]) if RESERVATIONS else '<div class="text-center py-8 text-slate-500 text-xs">No active reservations recorded yet.</div>'
        
        table_status_rows = "".join([f'''
        <div class="flex items-center justify-between p-3 bg-slate-800/40 border border-slate-700/50 rounded-xl">
            <div class="flex items-center gap-3">
                <span class="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center font-mono font-bold text-xs text-accentBlue border border-slate-700">{t["id"]}</span>
                <div>
                    <p class="text-sm font-semibold text-slate-200">Table {t["id"]}</p>
                    <p class="text-xs text-slate-400">{t["seats"]} seats capacity</p>
                </div>
            </div>
            <span class="px-2.5 py-1 text-xs font-medium rounded-full {"bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" if t["status"]=="Available" else "bg-rose-500/10 text-rose-400 border border-rose-500/20"}">{t["status"]}</span>
        </div>
        ''' for t in TABLES])

        content_html = f"""
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-cardBg border border-slate-800 rounded-2xl p-5 shadow-lg">
                <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Available Tables</p>
                <p class="text-3xl font-extrabold text-white">{available_count} <span class="text-xs font-normal text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">/ {len(TABLES)} FREE</span></p>
            </div>
            <div class="bg-cardBg border border-slate-800 rounded-2xl p-5 shadow-lg">
                <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Active Reservations</p>
                <p class="text-3xl font-extrabold text-white">{len(RESERVATIONS)} <span class="text-xs font-normal text-accentBlue bg-accentBlue/10 px-2 py-0.5 rounded-full border border-accentBlue/20">LIVE</span></p>
            </div>
            <div class="bg-cardBg border border-slate-800 rounded-2xl p-5 shadow-lg">
                <p class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Current Occupancy</p>
                <p class="text-3xl font-extrabold text-white">{occupancy}% <span class="text-xs font-normal text-slate-400">/ {total_capacity} SEATS</span></p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div class="lg:col-span-2 space-y-6">
                <div class="bg-cardBg border border-slate-800 rounded-2xl p-6 shadow-xl">
                    <h3 class="text-sm font-bold text-white mb-4 flex items-center justify-between">
                        <span>Live Table Status</span>
                        <span class="text-xs font-normal text-emerald-400 flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> Monitor Seating</span>
                    </h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {table_status_rows}
                    </div>
                </div>

                <div class="bg-cardBg border border-slate-800 rounded-2xl p-6 shadow-xl">
                    <h3 class="text-sm font-bold text-white mb-4">Active Reservations ({len(RESERVATIONS)})</h3>
                    <div class="space-y-3 max-h-60 overflow-y-auto pr-1">
                        {reservations_list}
                    </div>
                </div>
            </div>

            <div class="bg-cardBg border border-slate-800 rounded-2xl p-6 shadow-xl h-fit">
                <h3 class="text-sm font-bold text-white mb-4">Live Booking Desk</h3>
                <form action="/add-reservation" method="POST" class="space-y-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Assign Table</label>
                        <select name="table_id" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-accentBlue">
                            {tables_options}
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Customer Name</label>
                        <input type="text" name="customer_name" required placeholder="Enter guest name" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-accentBlue">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Contact Phone (International)</label>
                        <div class="grid grid-cols-12 gap-2">
                            <select name="country_code" class="col-span-5 bg-slate-900 border border-slate-700 rounded-xl px-2 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-accentBlue font-mono">
                                <option value="+92">+92 (PK)</option>
                                <option value="+1">+1 (US)</option>
                                <option value="+44">+44 (UK)</option>
                                <option value="+971">+971 (UAE)</option>
                                <option value="+966">+966 (KSA)</option>
                            </select>
                            <input type="text" name="phone" required placeholder="300 1234567" class="col-span-7 bg-slate-900 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-accentBlue">
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Guest Count</label>
                        <input type="number" name="guests" min="1" max="12" value="2" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-accentBlue">
                    </div>
                    <button type="submit" class="w-full bg-accentBlue hover:bg-blue-600 text-white font-medium py-2.5 px-4 rounded-xl transition shadow-lg shadow-blue-500/20 text-sm">
                        Confirm Reservation Table
                    </button>
                </form>
            </div>
        </div>
        """

    elif tab == "tables":
        table_cards = "".join([f'''
        <div class="bg-cardBg border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col justify-between">
            <div>
                <div class="flex justify-between items-center mb-4">
                    <span class="text-lg font-bold font-mono text-white">Table {t["id"]}</span>
                    <span class="px-2.5 py-1 text-xs font-medium rounded-full {"bg-emerald-500/10 text-emerald-400 border border-emerald-500/20" if t["status"]=="Available" else "bg-rose-500/10 text-rose-400 border border-rose-500/20"}">{t["status"]}</span>
                </div>
                <p class="text-sm text-slate-400 mb-6">Capacity: <strong class="text-slate-200">{t["seats"]} Seats</strong></p>
            </div>
            <form action="/toggle-table" method="POST">
                <input type="hidden" name="table_id" value="{t["id"]}">
                <button type="submit" class="w-full py-2 px-3 rounded-xl text-xs font-semibold border {"border-rose-500/30 text-rose-400 hover:bg-rose-500/10" if t["status"]=="Available" else "border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"} transition">
                    {"Mark as Booked" if t["status"]=="Available" else "Set as Available"}
                </button>
            </form>
        </div>
        ''' for t in TABLES])

        content_html = f"""
        <div class="mb-6">
            <h2 class="text-xl font-bold text-white">Table Management ({len(TABLES)} Tables)</h2>
            <p class="text-xs text-slate-400">Manage restaurant seating layouts and operational availability status.</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {table_cards}
        </div>
        """

    elif tab == "reservations":
        all_res = "".join([f'''
        <div class="bg-cardBg border border-slate-800 rounded-xl p-4 flex justify-between items-center">
            <div>
                <h4 class="text-sm font-bold text-white">{r["name"]}</h4>
                <p class="text-xs text-slate-400">Table: {r["table"]} | Guests: {r["guests"]} | Phone: {r["country_code"]} {r["phone"]}</p>
            </div>
            <span class="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs rounded-full">Confirmed Active</span>
        </div>
        ''' for r in RESERVATIONS]) or '<div class="bg-cardBg border border-slate-800 rounded-xl p-8 text-center text-slate-500 text-sm">No reservations found. Use the Live Dashboard booking desk to add entries.</div>'

        content_html = f"""
        <div class="mb-6">
            <h2 class="text-xl font-bold text-white">All Reservations</h2>
            <p class="text-xs text-slate-400">Complete historical and active guest booking records.</p>
        </div>
        <div class="space-y-4 max-w-4xl">
            {all_res}
        </div>
        """

    elif tab == "logs":
        content_html = """
        <div class="mb-6">
            <h2 class="text-xl font-bold text-white">Operational System Logs</h2>
            <p class="text-xs text-slate-400">System diagnostics, audit trails, and automated script event streams.</p>
        </div>
        <div class="bg-slate-950 border border-slate-800 rounded-2xl p-6 font-mono text-xs text-slate-300 space-y-2 shadow-xl">
            <p class="text-emerald-400">[17:40:01] INFO: Phone container grid responsive layout fixed.</p>
            <p class="text-slate-400">[17:40:15] DEBUG: Form inputs constrained within card boundaries successfully.</p>
        </div>
        """

    elif tab == "settings":
        content_html = f"""
        <div class="mb-6">
            <h2 class="text-xl font-bold text-white">System Settings</h2>
            <p class="text-xs text-slate-400">Configure platform parameters, shift schedules, and security credentials.</p>
        </div>
        <div class="bg-cardBg border border-slate-800 rounded-2xl p-6 max-w-xl space-y-4 shadow-xl">
            <div>
                <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Active Shift Schedule</label>
                <input type="text" value="Dinner (17:00 - 22:00)" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-200">
            </div>
            <div>
                <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Total Restaurant Seating Capacity</label>
                <input type="number" value="{total_capacity}" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-200">
            </div>
            <button class="bg-accentBlue hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-xl text-sm transition">Save Configuration</button>
        </div>
        """

    def nav_class(name):
        base = "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition"
        if tab == name:
            return f"{base} bg-accentBlue text-white shadow-lg shadow-blue-500/20"
        return f"{base} text-slate-400 hover:text-white hover:bg-slate-800/50"

    html_page = f"""
    <!DOCTYPE html>
    <html lang="en" class="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DarkFactory Enterprise Tablekeeper</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {{
                darkMode: 'class',
                theme: {{
                    extend: {{
                        colors: {{
                            darkBg: '#0b0f19',
                            cardBg: '#131c2e',
                            accentBlue: '#6366f1',
                        }}
                    }}
                }}
            }}
        </script>
    </head>
    <body class="bg-darkBg text-slate-100 min-h-screen font-sans antialiased flex">

        <!-- Sidebar -->
        <aside class="w-72 border-r border-slate-800/80 bg-cardBg/40 flex flex-col justify-between p-6 sticky top-0 h-screen">
            <div class="space-y-8">
                <div class="flex items-center space-x-3 px-2">
                    <div class="w-8 h-8 rounded-xl bg-accentBlue flex items-center justify-center font-bold text-white shadow-lg shadow-blue-500/30">DF</div>
                    <div>
                        <h1 class="text-base font-bold text-white tracking-wide">DarkFactory</h1>
                        <p class="text-[10px] text-slate-400 uppercase tracking-widest font-mono">ENTERPRISE PLATFORM</p>
                    </div>
                </div>

                <nav class="space-y-2">
                    <a href="/?tab=dashboard" class="{nav_class('dashboard')}">
                        <span>📊</span> Live Dashboard
                    </a>
                    <a href="/?tab=tables" class="{nav_class('tables')}">
                        <span>🪑</span> Table Management
                    </a>
                    <a href="/?tab=reservations" class="{nav_class('reservations')}">
                        <span>📅</span> Reservations
                    </a>
                    <a href="/?tab=logs" class="{nav_class('logs')}">
                        <span>📈</span> Operational Logs
                    </a>
                    <a href="/?tab=settings" class="{nav_class('settings')}">
                        <span>⚙️</span> System Settings
                    </a>
                </nav>
            </div>

            <div class="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-4">
                <p class="text-[10px] font-mono font-semibold text-accentBlue uppercase tracking-wider mb-1">US HACKATHON EDITION</p>
                <p class="text-xs text-slate-400">WeAreDevelopers &times; BAND Reservation Platform Build</p>
            </div>
        </aside>

        <!-- Main Content Area -->
        <div class="flex-1 flex flex-col min-h-screen">
            <header class="border-b border-slate-800/80 bg-cardBg/30 backdrop-blur sticky top-0 z-50 px-8 h-20 flex items-center justify-between">
                <div>
                    <h2 class="text-xl font-extrabold text-white tracking-tight">Enterprise Tablekeeper System</h2>
                    <p class="text-xs text-slate-400">Real-time restaurant reservation and table seating coordinator dashboard</p>
                </div>
                <div class="flex items-center gap-4">
                    <span class="px-3 py-1.5 bg-slate-900 border border-slate-700/80 rounded-xl text-xs font-medium text-slate-300">Shift: Dinner (17:00 - 22:00)</span>
                    <span class="px-3 py-1.5 bg-accentBlue/20 border border-accentBlue/30 text-accentBlue rounded-xl text-xs font-semibold flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-accentBlue animate-ping"></span> Live Feed Active
                    </span>
                </div>
            </header>

            <main class="flex-1 p-8">
                {content_html}
            </main>
        </div>

    </body>
    </html>
    """
    return HTMLResponse(content=html_page)

@app.post("/add-reservation")
async def add_reservation(table_id: str = Form(...), customer_name: str = Form(...), country_code: str = Form(...), phone: str = Form(...), guests: int = Form(...)):
    RESERVATIONS.append({"table": table_id, "name": customer_name, "country_code": country_code, "phone": phone, "guests": guests})
    for t in TABLES:
        if t["id"] == table_id:
            t["status"] = "Booked"
    return RedirectResponse(url="/?tab=dashboard", status_code=303)

@app.post("/toggle-table")
async def toggle_table(table_id: str = Form(...)):
    for t in TABLES:
        if t["id"] == table_id:
            t["status"] = "Available" if t["status"] == "Booked" else "Booked"
    return RedirectResponse(url="/?tab=tables", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("index:app", host="127.0.0.1", port=8000, reload=True)