# Park View Drugs — Project Memory

## Project Overview
**Park View Drugs** — a locally owned pharmacy in **Esperance, San Fernando, Trinidad & Tobago**. Full-stack Flask + SQLite web application with admin panel.

**Live at (Tailscale):** http://100.89.199.87:5050/ (hpwin11 — tailnet wecaregd2026@)
**Local:** http://127.0.0.1:5050/
**Admin:** http://127.0.0.1:5050/admin/login — username `Admin`, password configured via the private runtime settings
**Facebook:** https://www.facebook.com/pvdrugs/

---

## Tech Stack
- **Backend:** Python 3.11 + Flask (debug mode, port 5050)
- **Database:** SQLite at `instance/parkview.db`
- **Frontend:** HTML5, Vanilla CSS3 (CSS variable tokens), Vanilla JavaScript
- **Fonts:** Google Fonts — Open Sans, Poppins, Raleway, Inter, Outfit
- **Icons:** FontAwesome 6.4.2
- **Template Engine:** Jinja2

---

## Directory Structure
```
C:\aa-NewWeb\
├── app.py                    # Flask app (routes, admin CRUD, DB helpers)
├── requirements.txt          # Flask, Flask-SQLAlchemy, Flask-Migrate
├── database/
│   └── schema.sql            # Full schema + seed data (6 tables)
├── instance/
│   └── parkview.db           # SQLite database (auto-created on first run)
├── static/
│   ├── css/
│   │   ├── styles.css        # Main CSS with variable tokens
│   │   └── pages.css         # Inner page styles
│   ├── js/
│   │   └── scripts.js        # Vanilla JS (carousel, modal, scroll animations)
│   └── images/
│       └── logo.png          # Your logo from N:\PV-Pics\pvsuplogo.png
├── templates/
│   ├── base.html             # Base template (header/footer/modal partials)
│   ├── index.html            # Homepage (carousel, service cards, features)
│   ├── services.html         # DB-driven services list
│   ├── service_detail.html   # Individual service page
│   ├── about.html            # About page with values
│   ├── contact.html          # Contact form (saves to DB, AJAX submit)
│   ├── weekly-flyer.html     # DB-driven flyer deals
│   ├── products.html         # Category-filtered products
│   ├── minor-ailment.html    # Minor ailment info
│   ├── partials/
│   │   ├── header.html       # Nav with url_for() links + dropdowns
│   │   ├── footer.html       # Dynamic year, social links, settings
│   │   ├── contact_bar.html  # Phone, address, hours bar
│   │   └── modal.html        # Store info popup modal
│   └── admin/
│       ├── base_admin.html   # Admin layout (sidebar, nav, theme)
│       ├── login.html        # Admin login form
│       ├── dashboard.html    # Stats grid + quick actions
│       ├── table_list.html   # Dynamic table view for any table
│       └── table_edit.html   # Dynamic add/edit form (field types)
├── index.html                # OLD static homepage (keep for reference)
├── css/                      # OLD static CSS (keep for reference)
├── js/                       # OLD static JS (keep for reference)
├── images/                   # OLD static images (keep for reference)
└── pages/                    # OLD static HTML pages (keep for reference)
```

---

## Database Schema (6 tables)

### 1. `services`
| Field | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| title | TEXT | Required |
| description | TEXT | Required |
| icon | TEXT | FontAwesome class, e.g. "fas fa-prescription" |
| slug | TEXT UNIQUE | URL slug, e.g. "prescription-refills" |
| page_content | TEXT | Optional long-form content |
| created_at | TIMESTAMP | Auto |

**Seeded:** 6 services (Minor Ailment, Vaccinations, Refills, Compounding, Review, Delivery)

### 2. `products`
| Field | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| name | TEXT | Required |
| description | TEXT | Optional |
| category | TEXT | "OTC", "Vitamins", "Natural", "Personal Care", "General" |
| price | DECIMAL | Optional |
| image | TEXT | Optional image URL |
| featured | INTEGER | 0/1 flag |
| created_at | TIMESTAMP | Auto |

**Seeded:** 0 products (needs population — TODO)

### 3. `flyer_deals`
| Field | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| title | TEXT | Required |
| description | TEXT | Required |
| icon | TEXT | FontAwesome class |
| color_start | TEXT | CSS gradient start color |
| color_end | TEXT | CSS gradient end color |
| icon_color | TEXT | CSS icon color |
| valid_until | TEXT | Date string |
| created_at | TIMESTAMP | Auto |

**Seeded:** 6 deals (Vitamins, First Aid, Natural, Baby, Summer, Heart Health)

### 4. `contact_messages`
| Field | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| name | TEXT | Sender name |
| email | TEXT | Sender email |
| subject | TEXT | Optional |
| message | TEXT | Message body |
| is_read | INTEGER | 0=unread, 1=read |
| created_at | TIMESTAMP | Auto |

### 5. `newsletter_subscribers`
| Field | Type | Notes |
|---|---|---|
| id | INTEGER PK | Auto-increment |
| email | TEXT UNIQUE | Subscriber email |
| subscribed_at | TIMESTAMP | Auto |

### 6. `site_settings`
| Field | Type | Notes |
|---|---|---|
| key | TEXT PK | Setting key |
| value | TEXT | Setting value |

**Seeded:** 11 settings (business_name, phone, address, full_address, hours_weekday, hours_saturday, hours_sunday, facebook_url, tagline, hero_title_1, hero_desc_1)

---

## Brand Assets
- **Logo:** `static/images/logo.png` (374×164 PNG from N:\PV-Pics\pvsuplogo.png)
- **Primary Color:** `#1E7D29` (green)
- **Dark Green:** `#1E471C`
- **Light Green:** `#4FB151`
- **Text Color:** `#3F322D` (warm dark brown)
- **Body Text:** `#5C524C`
- **Footer BG:** `#1E471C` (dark green)

## Business Details
- **Name:** Park View Drugs
- **Phone:** (868) 223-7508
- **Address:** S.S. Erin Road, Esperance, San Fernando, Trinidad & Tobago
- **Hours:** Mon-Fri 8AM-6PM, Sat 8AM-3PM, Sun Closed
- **Facebook:** https://www.facebook.com/pvdrugs/

---

## Admin Panel

### Access
- **URL:** http://127.0.0.1:5050/admin/login (or http://100.89.199.87:5050/admin/login over Tailscale)
- **Password:** set via machine-level env var `PARKVIEW_ADMIN_PASSWORD_HASH` (werkzeug scrypt hash, generated 2026-08-22). The SYSTEM scheduled task reads machine env vars, so user-level vars won't work.
- **Secret key:** machine env var `PARKVIEW_SECRET_KEY` (also required for the SYSTEM task).

### Dynamic CRUD
The admin panel uses a table metadata dict (`TABLES` in app.py) for dynamic form generation. Each field type maps to proper HTML inputs:

| Field Type | HTML Input |
|---|---|
| `text` | `<input type="text">` |
| `textarea` | `<textarea>` |
| `number` | `<input type="number">` |
| `select` | `<select>` with options array |
| `checkbox` | `<input type="checkbox">` |
| `color` | `<input type="color">` (color picker) |
| `date` | `<input type="date">` |
| `readonly` | Display only |
| `id` | Auto-increment, read-only |

### Read-Only Tables
Tables with `readonly: True` in metadata (contact_messages, newsletter_subscribers) have edit/delete hidden. Contact messages have a toggle-read button.

### Features
- Session-based auth (`session['admin_logged_in']`)
- Dashboard with record counts
- Quick action buttons (Add Service, Add Deal, Add Product, View Messages, Settings)
- Edit/Delete on all writable tables
- Color pickers for flyer deal gradients
- Category dropdown for products
- Dynamic form field rendering

---

## Routes

### Public Routes
| Method | Route | Function |
|---|---|---|
| GET | `/` | Homepage |
| GET | `/services` | Services list |
| GET | `/services/<slug>` | Service detail |
| GET | `/about` | About page |
| GET/POST | `/contact` | Contact form |
| GET | `/weekly-flyer` | Flyer deals |
| GET | `/products` | Products (with `?category=` filter) |
| GET | `/minor-ailment` | Minor ailment page |
| POST | `/newsletter` | Newsletter subscribe API |

### Admin Routes
| Method | Route | Function |
|---|---|---|
| GET/POST | `/admin/login` | Admin login |
| GET | `/admin/logout` | Logout |
| GET | `/admin/` | Dashboard |
| GET | `/admin/<table>/` | List records |
| GET/POST | `/admin/<table>/add` | Add record |
| GET/POST | `/admin/<table>/<id>/edit` | Edit record |
| POST | `/admin/<table>/<id>/delete` | Delete record |
| POST | `/admin/messages/<id>/toggle-read` | Toggle read status |

---

## What's Been Done

- [x] Static PharmaChoice replica → **Park View Drugs** rebrand
- [x] Logo from N:\PV-Pics applied site-wide
- [x] Real business details from existing Node.js app (phone, address, hours)
- [x] Green color palette extracted from logo
- [x] Full Flask + SQLite backend
- [x] 6 database tables with seed data
- [x] Jinja2 template inheritance (base → pages)
- [x] CSS variable tokens (`--font-heading`, `--font-body`, `--shadow-*`, `--radius-*`)
- [x] Multiple Google Fonts (Open Sans, Poppins, Raleway, Inter, Outfit)
- [x] Interactive hero carousel with badges
- [x] Scroll animations (IntersectionObserver)
- [x] Responsive design (mobile, tablet, desktop)
- [x] Contact form with DB persistence
- [x] Newsletter API endpoint
- [x] Admin panel with full CRUD for all tables
- [x] Contact message management (read/unread toggle)
- [x] Site settings editor (phone, hours, address, tagline)

---

## What Needs To Be Done (TODOs)

- [ ] **Seed products** — Products table is empty; add sample products via admin or seed SQL
- [ ] **Legal pages** — Terms & Conditions, Privacy Policy, Cookie Policy, Disclaimers are placeholder links
- [ ] **Health Advice pages** — Medication Search, Medical Conditions, Health Blog, Community Support are placeholder links
- [ ] **Newsletter UI** — API exists at POST `/newsletter` but there's no subscribe form on the public site (footer has one in the old design)
- [ ] **404 handler** — Add a proper 404 error page template
- [ ] **Product detail pages** — Individual product pages would be useful
- [ ] **Migrate Node.js features** — The existing app at N:\POS-SRC\PARKVIEWWEB\ has user auth, cart, checkout, and more products; could be ported
- [ ] **Deploy config** — Add Gunicorn/WSGI config for production deployment
- [ ] **Admin password** — Change from default `admin123` in production
- [ ] **Image assets** — Add hero images, pharmacist photo, store interior photos
- [ ] **SEO** — Add meta tags, sitemap, robots.txt
- [ ] **Database migrations** — For future schema changes

---

## Related Files on Disk

- **N:\POS-SRC\PARKVIEWWEB\** — Original Node.js/Express app (reference for features, branding)
- **N:\PV-Pics\pvsuplogo.png** — Original logo source (374×164 PNG)
- **C:\GoldenCareMedicalWeb\** — Previous unrelated project
