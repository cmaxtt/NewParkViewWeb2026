# Park View Drugs — Pharmacy & Community Healthcare Web Application

A full-stack pharmacy and community healthcare web platform built with **Python (Flask)**, **SQLite**, and modern **Vanilla JS/CSS**, serving the community of Esperance, San Fernando in Trinidad & Tobago.

[![Repository](https://img.shields.io/badge/GitHub-ParkViewAgWebsite-0284C7?logo=github)](https://github.com/cmaxtt/ParkViewAgWebsite.git)
[![Python](https://img.shields.io/badge/Python-3.11+-0A2540?logo=python)](https://python.org)
[![Framework](https://img.shields.io/badge/Framework-Flask_3.1-0284C7?logo=flask)](https://flask.palletsprojects.com/)
[![Design](https://img.shields.io/badge/Design_System-Royal_Sapphire_%26_Gold-D97706)](https://github.com/cmaxtt/ParkViewAgWebsite.git)
[![Server](https://img.shields.io/badge/Production_Server-Waitress-10B981)](https://docs.pylonsproject.org/projects/waitress/en/latest/)

---

## 🌟 Modern Upgrades & Features

### 1. Brand Identity & Visual System
- **Royal Sapphire & Amber Gold Theme**: Built around deep authoritative sapphire navy (`#0A2540`, `#0284C7`), warm amber gold accents (`#D97706`, `#F59E0B`, `#FBBF24`), emerald healthcare badges (`#10B981`), and clinical slate surfaces (`#F8FAFC`, `#FFFFFF`).
- **High-Definition Vector Logo**: Custom-crafted wide vector mark (`logo.svg` & `logo-white.svg`) featuring a sapphire squircle, metallic gold rim, medical cross, and an emerald Tree of Life / Park View wellness emblem. Includes 2x retina PNG fallback and custom SVG/PNG favicon.

### 2. Navigation & Header
- **Live Status Announcement Bar**: Pulsing emerald indicator displaying live store operating hours (`Open Today: 8:00 AM – 11:00 PM`), direct telephone click-to-call link, location pill, and social links.
- **Search & Quick Action**: Embedded search bar with lead icon, "Refill Rx" quick action button, and store directions modal trigger.
- **Categorized 2-Column Mega Dropdowns**:
  - **Clinical & Pharmacy Services**: Clinical assessment, compliance blister packaging, vaccination clinic, medication review, and private pharmacist consultation badge.
  - **Aisle & Category Showcase**: Over-the-Counter, Vitamins & Supplements, Natural Health Remedies, Personal Care & Hygiene, and Weekly Flyer promo card.

### 3. Homepage Experience
- **Cinematic Sapphire Carousel**: Deep sapphire overlay gradients (`rgba(8, 28, 46, 0.90)` to `rgba(2, 132, 199, 0.45)`), sparkle pill chips, and dual call-to-action buttons (`Refill Rx Online` & `Minor Ailment Care`).
- **4-Column Credibility Strip**: Board Certified Pharmacists, Fast & Accurate Dispensing, Full-Service Family Care, and Local Delivery.
- **Aisle & Category Showcase**: OTC, Vitamins, Natural Remedies, and Personal Care cards.
- **Clinical Excellence Section**: Asymmetric 2-column layout with accredited clinical checklist and elevated community trust card.

### 4. Interactive Pages & Services
- **Product Catalog (`/products`)**: Interactive category filter pills, real-time keyword search toolbar, Trinidad & Tobago Dollar (`TT$`) currency tags, and a 3-step rewards banner.
- **Weekly Flyer & Savings (`/weekly-flyer`)**: Deal cards with badge tags, store invitation banner, and view switcher.
- **Minor Ailment Assessment Clinic (`/minor-ailment`)**: 8 condition cards with specific treatments, clinical overview bar, and 3-step consultation workflow.
- **Contact & Visit (`/contact`)**: 4 contact info cards, modern focus-ring inquiry form with CSRF validation, and embedded Google Maps card.
- **Executive Footer**: 4-column structured footer with pharmacy board accreditation chips, dispensary hours card, and staff portal link.

---

## 🌐 Network Access & Endpoints

| Environment | URL | Description |
|---|---|---|
| **Localhost** | `http://127.0.0.1:5050/` | Local workstation access |
| **Remote (Machine IP)** | `http://192.168.100.131:5050/` | Remote network access via machine's primary IPv4 |
| **Tailscale Mesh** | `http://100.93.42.64:5050/` | Encrypted WireGuard mesh access |
| **Staff Admin** | `http://127.0.0.1:5050/admin/login` | Administrative dashboard |
| **Health Check** | `http://127.0.0.1:5050/healthz` | System & database health probe |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11+, Flask 3.1 |
| **Database** | SQLite3 (WAL mode, foreign keys, busy timeout) |
| **WSGI Server** | Waitress (production multi-threaded, binds `0.0.0.0:5050`) |
| **Frontend** | Semantic HTML5, Vanilla CSS3 (Custom Properties), Vanilla JS (ES6+) |
| **Icons & Fonts** | FontAwesome 6.4.2, Google Fonts (Outfit, Poppins, Inter, Plus Jakarta Sans) |
| **Templates** | Jinja2 (template inheritance & modular partials) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Git

### Installation & Run

```bash
# Clone the repository
git clone https://github.com/cmaxtt/ParkViewAgWebsite.git
cd ParkViewAgWebsite

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Start Production Server (Waitress)
python run_prod.py

# Or Start Development Server
python app.py
```

The database initializes automatically on first run with seeded clinical services, weekly flyer deals, and site settings.

---

## 📁 Project Structure

```
ParkViewAgWebsite/
├── app.py                    # Flask application core (routes, admin CRUD, DB helpers)
├── run_prod.py               # Production entry point (Waitress multi-threaded runner)
├── requirements.txt          # Python package dependencies
├── persistmemory.md          # Architectural context and design specifications
├── .gitignore                # Git ignore configuration
├── README.md                 # Project documentation
│
├── database/
│   └── schema.sql            # SQLite schema with seed data
│
├── static/
│   ├── css/
│   │   ├── styles.css        # Core design system tokens, header, hero, footer, responsive
│   │   └── pages.css         # Catalog, flyer, minor ailment clinic, contact pages
│   ├── js/
│   │   └── scripts.js        # Carousel touch/swipe, modal controls, flyer view switcher
│   └── images/
│       ├── logo.svg          # Modern wide brand logo (light header)
│       ├── logo-white.svg    # Modern wide brand logo (dark footer)
│       ├── logo.png          # High-res 2x retina fallback
│       ├── favicon.svg       # Brand favicon vector
│       └── favicon.png       # 64x64 favicon fallback
│
├── templates/
│   ├── base.html             # Base layout template
│   ├── index.html            # Modern homepage with carousel and aisles
│   ├── services.html         # Clinical services directory
│   ├── service_detail.html   # Dedicated clinical service view
│   ├── products.html         # Product catalog with category pills
│   ├── weekly-flyer.html     # Promotional flyer and deal switcher
│   ├── minor-ailment.html    # Minor ailment clinic assessment guide
│   ├── contact.html          # Contact form and interactive locator
│   ├── about.html            # About us and history
│   ├── 404.html              # Custom 404 page
│   ├── 500.html              # Custom 500 page
│   ├── partials/
│   │   ├── header.html       # Navigation with mega dropdowns and safe endpoint guards
│   │   ├── footer.html       # Executive 4-column footer
│   │   ├── contact_bar.html  # Live status bar and quick contact
│   │   └── modal.html        # Store directions and hours popup
│   └── admin/
│       ├── base_admin.html   # Admin portal layout (Royal Sapphire style)
│       ├── login.html        # Staff login
│       ├── dashboard.html    # Operational KPI dashboard
│       ├── table_list.html   # Dynamic CRUD data table
│       └── table_edit.html   # Dynamic record editor
│
├── start_hidden.vbs          # Silent background Windows Startup runner
├── start_server.bat          # Batch script launcher
└── check_firewall.ps1        # Network port diagnostic
```

---

## 🔒 Security & Performance Features

- **CSRF Protection**: Cryptographic token verification on all POST routes.
- **Safe Route Guards**: Hardened Jinja template evaluations prevent unhandled exceptions during 404 or unrouted page requests.
- **Database Concurrency**: SQLite with WAL (`Write-Ahead Logging`), 5000ms busy timeout, and enforced foreign key constraints.
- **Rate Limiting**: Built-in rate limiter for contact form, newsletter, and admin login attempts.
- **Multi-Interface Support**: Waitress binds to `0.0.0.0:5050` with automatic detection and logging of the machine's primary IPv4 address for remote access.

---

## 📄 License

© 2026 Park View Drugs. All rights reserved. S.S. Erin Road, Esperance, San Fernando, Trinidad & Tobago.

