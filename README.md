# L'Étoile Noire Tablekeeper
**Executive Tablekeeper, Multi-Zone Floor Management & Live Order Dispatch Suite**

An enterprise-grade restaurant reservation and floor management system built for the **Dark Factory** hackathon (*tablekeeper* track, presented by WeAreDevelopers & BAND).

---

## 🚀 Project Overview
**L'Étoile Noire Tablekeeper** bridges real-time multi-zone floor monitoring with secure administrative control. Designed to handle high-end dining and multi-zone hospitality operations under strict concurrency constraints, it guarantees that tables are never double-booked.

### 🌟 Key Features
* **Live Floor & Station Matrix:** Real-time occupancy tracking across 5 distinct dining zones (Drive-Thru, Front Counter, Kiosks, Delivery Hub, and VIP Lounge).
* **Smart Station Lifecycle:** Dynamic station registration and capacity threshold management (supporting up to 50 seats per station).
* **Order Dispatch Desk:** Secure slot booking with standardized international phone number validation.
* **Active Operations Ledger:** Instant auditing, state locking, and CSV report exports.
* **Glassmorphism UI:** Modern, responsive Tailwind CSS interface with dual Dark/Light theme support.

---

## 🛠️ Tech Stack
* **Backend:** Python, Flask, SQLite / Relational state management.
* **Frontend:** HTML5, Tailwind CSS, Modern JavaScript.
* **Architecture:** Multi-agent autonomous engineering workflow via BAND Desktop, structured across clean-room development stages.

---

## 📁 Repository Structure
* `stage-1/` - Core application foundation, basic routing, and initial station schema.
* `stage-2/` - Multi-zone floor matrix integration and dynamic filtering.
* `stage-3/` - Order dispatch desk, international phone validation, and state locking.
* `stage-4/` - Production-ready glassmorphism UI, CSV report exports, and telemetry.
* `mandates/` - Generic, reusable coding agent standing instructions.
* `Dockerfile` - Clean-room containerization setup.