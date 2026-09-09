# Park View Drugs — Pharmacy Web Application

A full-stack pharmacy website built with **Flask**, **SQLite**, and **Vanilla JS/CSS**, serving the Esperance, San Fernando community in Trinidad & Tobago.

**Live (Tailscale):** http://100.89.199.87:5050/
**Admin Panel:** http://100.89.199.87:5050/admin/login
**Facebook:** https://www.facebook.com/pvdrugs/

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11+, Flask 3.1 |
| **Database** | SQLite (single-file, zero-config) |
| **Frontend** | HTML5, Vanilla CSS3 (variable tokens), Vanilla JavaScript |
| **Fonts** | Google Fonts — Open Sans, Poppins, Raleway, Inter, Outfit |
| **Icons** | FontAwesome 6.4.2 |
| **Templates** | Jinja2 (template inheritance + partials) |
| **Server** | Waitress (production-grade, multi-threaded) |
| **Network** | Tailscale (secure WireGuard mesh VPN) |

---

## Quick Start

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# Clone
git clone https://github.com/cmaxtt/NewParkViewWeb2026.git
cd NewParkViewWeb2026

# Install dependencies
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt

# Configure secrets before starting the app. See .env.example.
# The scheduled task runs as SYSTEM, so use machine-level environment variables.

# Run (development)
.venv\Scripts\python.exe app.py

# Run (production)
.venv\Scripts\python.exe run_prod.py
```

The app initializes the SQLite database automatically on first run with seed data (services, flyer deals, site settings).

### Access
- **Main site:** http://127.0.0.1:5050/
- **Admin panel:** http://127.0.0.1:5050/admin/login — username is configured through `PARKVIEW_ADMIN_USERNAME`, password through `PARKVIEW_ADMIN_PASSWORD_HASH`

---

## Project Structure

```
C:\aa-NewWeb\
├── app.py                    # Flask application (routes, admin CRUD, DB helpers)
├── run_prod.py               # Production entry point (Waitress server)
├── requirements.txt          # Python dependencies
├── persistmemory.md          # Session context and TODO tracking
├── .gitignore
├── README.md
│
├── database/
│   └── schema.sql            # Full SQLite schema + seed data
│
├── instance/                 # SQLite database (auto-created, gitignored)
│   └── parkview.db
│
├── static/
│   ├── css/
│   │   ├── styles.css        # Main stylesheet with CSS variable tokens
│   │   └── pages.css         # Inner page styles
│   ├── js/
│   │   └── scripts.js        # Vanilla JS (carousel, modal, scroll animations)
│   └── images/
│       └── logo.png          # Brand logo
│
├── templates/
│   ├── base.html             # Base template (header, footer, modal partials)
│   ├── index.html            # Homepage with carousel, services, features
│   ├── services.html         # Services listing (DB-driven)
│   ├── service_detail.html   # Individual service page
│   ├── about.html            # About us with values
│   ├── contact.html          # Contact form (AJAX, saves to DB)
│   ├── weekly-flyer.html     # Flyer deals (DB-driven)
│   ├── products.html         # Product categories with filter
│   ├── minor-ailment.html    # Minor ailment information
│   ├── partials/
│   │   ├── header.html       # Navigation with dropdowns
│   │   ├── footer.html       # Footer with dynamic year/settings
│   │   ├── contact_bar.html  # Top bar with phone, address, hours
│   │   └── modal.html        # Store info popup
│   └── admin/
│       ├── base_admin.html   # Admin layout (sidebar, nav)
│       ├── login.html        # Admin login form
│       ├── dashboard.html    # Stats dashboard
│       ├── table_list.html   # Dynamic table view (any table)
│       └── table_edit.html   # Dynamic add/edit form (any table)
│
├── start_hidden.vbs          # Silent launcher (Windows Startup folder)
├── start_server.bat          # Batch launcher
├── install_service.ps1       # Scheduled task installer (admin)
├── install_task.ps1          # Task scheduler setup (admin)
└── check_firewall.ps1        # Firewall diagnostic
```

---

## Database

Six tables, auto-initialized with seed data.

### Tables

| Table | Purpose | Read-Only? | Seed Data |
|---|---|---|---|
| `services` | Pharmacy services offered | No | 6 services |
| `products` | Product catalog | No | Empty |
| `flyer_deals` | Weekly promotional deals | No | 6 deals |
| `contact_messages` | Contact form submissions | Yes | — |
| `newsletter_subscribers` | Email newsletter list | Yes | — |
| `site_settings` | Business info, hours, tagline | No | 11 settings |

### Schema

```sql
services (id, title, description, icon, slug, page_content, created_at)
products (id, name, description, category, price, image, featured, created_at)
flyer_deals (id, title, description, icon, color_start, color_end, icon_color, valid_until, created_at)
contact_messages (id, name, email, subject, message, is_read, created_at)
newsletter_subscribers (id, email, subscribed_at)
site_settings (key, value)
```

---

## Admin Panel

Access at `/admin/login` with the username configured through `PARKVIEW_ADMIN_USERNAME` and the password configured through `PARKVIEW_ADMIN_PASSWORD_HASH` (or the temporary `PARKVIEW_ADMIN_PASSWORD` compatibility setting).

### Features
- **Dashboard** — Record counts for all tables with quick-action buttons
- **Dynamic CRUD** — Add, edit, delete on all writable tables
- **Field types** — text, textarea, number, select (dropdown), checkbox, color picker, date
- **Read-only tables** — contact_messages, newsletter_subscribers (view only)
- **Message management** — Toggle read/unread on contact form submissions
- **Site settings** — Edit business name, phone, address, hours, tagline directly in DB

### Admin Routes

| Route | Function |
|---|---|
| `/admin/login` | Login |
| `/admin/logout` | Logout |
| `/admin/` | Dashboard |
| `/admin/services/` | Manage services |
| `/admin/products/` | Manage products |
| `/admin/flyer_deals/` | Manage flyer deals |
| `/admin/contact_messages/` | View messages |
| `/admin/newsletter_subscribers/` | View subscribers |
| `/admin/site_settings/` | Edit settings |

---

## Business Details

| Field | Value |
|---|---|
| **Name** | Park View Drugs |
| **Phone** | (868) 223-7508 |
| **Address** | S.S. Erin Road, Esperance, San Fernando, Trinidad & Tobago |
| **Hours** | Mon-Fri 8AM-6PM, Sat 8AM-3PM |
| **Facebook** | https://www.facebook.com/pvdrugs/ |

### Brand Colors

| Token | Value | Usage |
|---|---|---|
| `--color-primary` | `#1E7D29` | Buttons, links, accents |
| `--color-primary-dark` | `#1E471C` | Footer, hover states |
| `--color-primary-light` | `#4FB151` | Highlights, icons |
| `--color-text` | `#3F322D` | Headings |
| `--color-text-body` | `#5C524C` | Body text |
| `--color-bg-light` | `#F5F7F2` | Section backgrounds |

### Font Tokens

| Token | Font Stack |
|---|---|
| `--font-heading` | `'Outfit', 'Poppins', sans-serif` |
| `--font-body` | `'Inter', 'Open Sans', sans-serif` |
| `--font-alt` | `'Raleway', sans-serif` |

---

## Tailscale Access

The app is published on a Tailscale mesh network for secure remote access:

```
http://100.89.199.87:5050/   — Tailscale IP (hpwin11)
http://hpwin11:5050/         — Tailscale MagicDNS hostname
```

The production server binds to 127.0.0.1 and the Tailscale IP only — it is NOT exposed on the LAN.

To connect from another device:
1. Install [Tailscale](https://tailscale.com/download) on your device
2. Sign in to the same Tailscale account (`wecaregd2026@`)
3. Open `http://hpwin11:5050/` in your browser

### Persistence

The app is configured to start automatically at Windows login via a VBS launcher in the Startup folder. It runs silently (no console window) and auto-restarts up to 5 times if it crashes.

---

## Development

### Adding a New Service

```sql
INSERT INTO services (title, description, icon, slug) VALUES (
    'Diabetes Management',
    'Comprehensive diabetes care and monitoring.',
    'fas fa-droplet',
    'diabetes-management'
);
```

Or use the admin panel at `/admin/services/add`.

### Adding a Flyer Deal

Use the admin panel at `/admin/flyer_deals/add` — includes color pickers for gradient backgrounds.

### Customizing Site Settings

All site-wide text (business name, phone, hours, tagline) is stored in `site_settings` table. Edit via admin at `/admin/site_settings/`.

---

## TODO

- [ ] Seed products table with inventory
- [ ] Add product detail pages
- [ ] Legal pages (Terms, Privacy, Cookies)
- [ ] Health Advice section (medication search, conditions, blog)
- [ ] Newsletter signup form on public pages
- [ ] 404 error page template
- [ ] Port user auth/cart from legacy Node.js app
- [x] Production deployment entry point and database initialization
- [x] CSRF protection, secure session defaults, validation, error pages, sitemap, and robots.txt
- [ ] HTTPS/reverse proxy, monitoring, backup/restore automation, and browser-based release QA

---

## License

© 2026 Park View Drugs. All rights reserved.
