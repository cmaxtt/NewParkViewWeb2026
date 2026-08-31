"""
Park View Drugs — Flask Application
"""
import os
import sqlite3
import re
import secrets
import hmac
import time
from functools import wraps
from datetime import datetime
from urllib.parse import urlparse
from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for, abort, make_response
from werkzeug.security import check_password_hash

app = Flask(__name__)
_secret_key = os.environ.get('PARKVIEW_SECRET_KEY')
app.config['SECRET_KEY'] = _secret_key or secrets.token_hex(32)
if not _secret_key:
    app.logger.warning('PARKVIEW_SECRET_KEY is not set - using a RANDOM session key. '
                       'Admin sessions will be invalidated on every restart. '
                       'Run setup_env.ps1 (Windows) or set PARKVIEW_SECRET_KEY (Linux).')
app.config['DATABASE'] = os.path.join(app.instance_path, 'parkview.db')
app.config['ADMIN_PASSWORD'] = os.environ.get('PARKVIEW_ADMIN_PASSWORD', '')
app.config['ADMIN_PASSWORD_HASH'] = os.environ.get('PARKVIEW_ADMIN_PASSWORD_HASH', '')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('PARKVIEW_COOKIE_SECURE', '').lower() in ('1', 'true', 'yes')

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
_rate_limit_buckets = {}

# ── Table Metadata ─────────────────────────────────────────
# Defines columns, labels, field types for the admin CRUD

TABLES = {
    'services': {
        'label': 'Services',
        'icon': 'fas fa-stethoscope',
        'order': 'id ASC',
        'fields': {
            'id':          {'label': 'ID',          'type': 'id'},
            'title':       {'label': 'Title',       'type': 'text',      'required': True},
            'description': {'label': 'Description', 'type': 'textarea',  'required': True},
            'icon':        {'label': 'Icon Class',  'type': 'text',      'required': True, 'placeholder': 'fas fa-prescription'},
            'slug':        {'label': 'URL Slug',    'type': 'text',      'required': True, 'placeholder': 'prescription-refills'},
            'page_content':{'label': 'Page Content', 'type': 'textarea',  'required': False},
            'created_at':  {'label': 'Created',     'type': 'readonly'},
        }
    },
    'products': {
        'label': 'Products',
        'icon': 'fas fa-capsules',
        'order': 'id DESC',
        'fields': {
            'id':          {'label': 'ID',          'type': 'id'},
            'name':        {'label': 'Name',        'type': 'text',      'required': True},
            'description': {'label': 'Description', 'type': 'textarea',  'required': False},
            'category':    {'label': 'Category',    'type': 'select',    'required': True, 'options': ['OTC','Vitamins','Natural','Personal Care','General']},
            'price':       {'label': 'Price',       'type': 'number',    'required': False, 'step': '0.01'},
            'image':       {'label': 'Image URL',   'type': 'text',      'required': False},
            'featured':    {'label': 'Featured',    'type': 'checkbox',  'required': False},
            'created_at':  {'label': 'Created',     'type': 'readonly'},
        }
    },
    'flyer_deals': {
        'label': 'Flyer Deals',
        'icon': 'fas fa-tag',
        'order': 'id DESC',
        'fields': {
            'id':          {'label': 'ID',          'type': 'id'},
            'title':       {'label': 'Title',       'type': 'text',      'required': True},
            'description': {'label': 'Description', 'type': 'textarea',  'required': True},
            'icon':        {'label': 'Icon Class',  'type': 'text',      'required': True, 'placeholder': 'fas fa-tag'},
            'color_start': {'label': 'Start Color', 'type': 'color',     'required': False, 'placeholder': '#E8F5E9'},
            'color_end':   {'label': 'End Color',   'type': 'color',     'required': False, 'placeholder': '#A5D6A7'},
            'icon_color':  {'label': 'Icon Color',  'type': 'color',     'required': False, 'placeholder': '#1E7D29'},
            'valid_until': {'label': 'Valid Until', 'type': 'date',      'required': False},
            'created_at':  {'label': 'Created',     'type': 'readonly'},
        }
    },
    'contact_messages': {
        'label': 'Contact Messages',
        'icon': 'fas fa-envelope',
        'order': 'id DESC',
        'readonly': True,
        'fields': {
            'id':          {'label': 'ID',          'type': 'id'},
            'name':        {'label': 'Name',        'type': 'readonly'},
            'email':       {'label': 'Email',       'type': 'readonly'},
            'subject':     {'label': 'Subject',     'type': 'readonly'},
            'message':     {'label': 'Message',     'type': 'readonly'},
            'is_read':     {'label': 'Read',        'type': 'readonly'},
            'created_at':  {'label': 'Received',    'type': 'readonly'},
        }
    },
    'newsletter_subscribers': {
        'label': 'Newsletter Subscribers',
        'icon': 'fas fa-newspaper',
        'order': 'id DESC',
        'readonly': True,
        'fields': {
            'id':           {'label': 'ID',           'type': 'id'},
            'email':        {'label': 'Email',        'type': 'readonly'},
            'subscribed_at':{'label': 'Subscribed',   'type': 'readonly'},
        }
    },
    'site_settings': {
        'label': 'Site Settings',
        'icon': 'fas fa-cog',
        'order': 'key ASC',
        'pk': 'key',
        'fields': {
            'key':   {'label': 'Key',   'type': 'text', 'required': True},
            'value': {'label': 'Value', 'type': 'textarea', 'required': True},
        }
    },
}

# ── Database Helpers ──────────────────────────────────────

def get_db():
    if 'db' not in g:
        conn = sqlite3.connect(app.config['DATABASE'], timeout=30)
        conn.row_factory = sqlite3.Row
        # WAL: safe concurrent reads under Waitress's threads; busy_timeout avoids lock errors
        conn.execute('PRAGMA journal_mode=WAL')
        conn.execute('PRAGMA busy_timeout=5000')
        conn.execute('PRAGMA foreign_keys=ON')
        g.db = conn
    return g.db

def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_urlsafe(32)
    return session['_csrf_token']

@app.before_request
def protect_post_requests():
    if request.method == 'POST' and request.endpoint in {'admin_login', 'contact', 'newsletter'}:
        key = (request.remote_addr or 'unknown', request.endpoint)
        now = time.monotonic()
        # prune stale buckets so the in-memory limiter cannot grow unbounded
        if len(_rate_limit_buckets) > 1024:
            stale = {k: [t for t in v if now - t < 60] for k, v in _rate_limit_buckets.items()}
            _rate_limit_buckets.clear()
            _rate_limit_buckets.update({k: v for k, v in stale.items() if v})
        recent = [stamp for stamp in _rate_limit_buckets.get(key, []) if now - stamp < 60]
        if len(recent) >= (10 if request.endpoint == 'admin_login' else 5):
            abort(429, description='Too many requests. Please try again shortly.')
        recent.append(now)
        _rate_limit_buckets[key] = recent
    if request.method == 'POST':
        expected = session.get('_csrf_token', '')
        supplied = request.form.get('_csrf_token', '') or request.headers.get('X-CSRF-Token', '')
        if not expected or not supplied or not hmac.compare_digest(expected, supplied):
            abort(400, description='Invalid or missing security token.')

@app.after_request
def add_security_headers(response):
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
    response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
    response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
    return response

def init_db():
    os.makedirs(app.instance_path, exist_ok=True)
    db = get_db()
    with app.open_resource('database/schema.sql', mode='r') as f:
        db.executescript(f.read())
    db.commit()

def dict_from_row(row):
    """Convert a sqlite3.Row to a plain dict."""
    if row is None:
        return None
    return dict(row)

@app.cli.command('init-db')
def init_db_command():
    init_db()
    print('Database initialized.')

@app.teardown_appcontext
def teardown_db(exception=None):
    close_db(exception)

# ── Admin Auth Helpers ────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

# ── Context Processors ────────────────────────────────────

@app.context_processor
def inject_settings():
    try:
        db = get_db()
        rows = db.execute('SELECT key, value FROM site_settings').fetchall()
        settings = {row['key']: row['value'] for row in rows}
    except Exception:
        settings = {}
    settings.setdefault('business_name', 'Park View Drugs')
    settings.setdefault('phone', '(868) 223-7508')
    settings.setdefault('address', 'Esperance, San Fernando, Trinidad & Tobago')
    settings.setdefault('full_address', 'S.S. Erin Road, Esperance, Trinidad & Tobago')
    settings.setdefault('hours_weekday', 'Mon-Fri: 8AM-6PM')
    settings.setdefault('hours_saturday', 'Sat: 8AM-3PM')
    settings.setdefault('facebook_url', 'https://www.facebook.com/pvdrugs/')
    settings.setdefault('tagline', 'Your trusted local pharmacy serving the San Fernando community.')
    settings.setdefault('hero_title_1', 'Your Health, Our Priority')
    settings.setdefault('hero_desc_1', 'At Park View Drugs, we care.')
    return {'settings': settings, 'now': datetime.now, 'tables_meta': TABLES, 'csrf_token': csrf_token}

# ── Public Routes ─────────────────────────────────────────

@app.route('/')
def home():
    db = get_db()
    try:
        services = db.execute('SELECT * FROM services LIMIT 4').fetchall()
        deals = db.execute('SELECT * FROM flyer_deals LIMIT 6').fetchall()
    except Exception:
        services = []
        deals = []
    return render_template('index.html', services=services, deals=deals)

@app.route('/services')
def services():
    db = get_db()
    try:
        services_list = db.execute('SELECT * FROM services').fetchall()
    except Exception:
        services_list = []
    return render_template('services.html', services=services_list)

@app.route('/services/<slug>')
def service_detail(slug):
    db = get_db()
    try:
        service = db.execute('SELECT * FROM services WHERE slug = ?', (slug,)).fetchone()
    except Exception:
        service = None
    if not service:
        return render_template('services.html'), 404
    return render_template('service_detail.html', service=service)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        if (1 <= len(name) <= 120 and EMAIL_RE.fullmatch(email) and len(email) <= 254
                and 1 <= len(message) <= 5000 and len(subject) <= 200):
            db = get_db()
            db.execute(
                'INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)',
                (name, email, subject, message)
            )
            db.commit()
            return jsonify({'success': True, 'message': 'Thank you! We will get back to you shortly.'})
        return jsonify({'success': False, 'message': 'Please provide a valid name, email, and message.'}), 400
    return render_template('contact.html')

@app.route('/weekly-flyer')
def weekly_flyer():
    db = get_db()
    try:
        deals = db.execute('SELECT * FROM flyer_deals').fetchall()
    except Exception:
        deals = []
    return render_template('weekly-flyer.html', deals=deals)

@app.route('/products')
def products():
    db = get_db()
    try:
        category = request.args.get('category', '')
        keywords = request.args.get('keywords', '').strip()[:100]
        if category and keywords:
            like = f'%{keywords}%'
            products_list = db.execute('SELECT * FROM products WHERE category = ? AND (name LIKE ? OR description LIKE ?)', (category, like, like)).fetchall()
        elif category:
            products_list = db.execute('SELECT * FROM products WHERE category = ?', (category,)).fetchall()
        elif keywords:
            like = f'%{keywords}%'
            products_list = db.execute('SELECT * FROM products WHERE name LIKE ? OR description LIKE ? OR category LIKE ?', (like, like, like)).fetchall()
        else:
            products_list = db.execute('SELECT * FROM products').fetchall()
    except Exception:
        products_list = []
    return render_template('products.html', products=products_list)

@app.route('/minor-ailment')
def minor_ailment():
    return render_template('minor-ailment.html')

@app.route('/newsletter', methods=['POST'])
def newsletter():
    email = request.form.get('email', '').strip()
    if EMAIL_RE.fullmatch(email) and len(email) <= 254:
        try:
            db = get_db()
            db.execute('INSERT OR IGNORE INTO newsletter_subscribers (email) VALUES (?)', (email,))
            db.commit()
            return jsonify({'success': True, 'message': 'Subscribed successfully!'})
        except Exception as e:
            app.logger.exception('Newsletter subscription failed')
            return jsonify({'success': False, 'message': 'Unable to subscribe right now.'}), 500
    return jsonify({'success': False, 'message': 'Please enter a valid email address.'}), 400

# ── Admin Routes ──────────────────────────────────────────

ADMIN_TABLES = ['services', 'products', 'flyer_deals', 'contact_messages', 'newsletter_subscribers', 'site_settings']

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        configured_hash = app.config['ADMIN_PASSWORD_HASH']
        valid_password = bool(configured_hash and check_password_hash(configured_hash, password))
        if not configured_hash and app.config['ADMIN_PASSWORD']:
            valid_password = hmac.compare_digest(password, app.config['ADMIN_PASSWORD'])
        if valid_password:
            session['admin_logged_in'] = True
            session.pop('_csrf_token', None)
            next_page = request.args.get('next', '')
            parsed_next = urlparse(next_page)
            if not next_page or parsed_next.scheme or parsed_next.netloc or not next_page.startswith('/'):
                next_page = url_for('admin_dashboard')
            return redirect(next_page)
        return render_template('admin/login.html', error='Invalid password.')
    return render_template('admin/login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/')
@login_required
def admin_dashboard():
    db = get_db()
    stats = {}
    for tbl in ADMIN_TABLES:
        try:
            count = db.execute(f'SELECT COUNT(*) as c FROM {tbl}').fetchone()['c']
        except Exception:
            count = 0
        stats[tbl] = count
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/<table_name>/')
@login_required
def admin_table_list(table_name):
    if table_name not in ADMIN_TABLES:
        abort(404)
    meta = TABLES.get(table_name, {})
    db = get_db()
    try:
        order = meta.get('order', 'id DESC')
        rows = db.execute(f'SELECT * FROM {table_name} ORDER BY {order}').fetchall()
    except Exception:
        rows = []
    return render_template('admin/table_list.html', table_name=table_name, meta=meta, rows=rows)

@app.route('/admin/<table_name>/add', methods=['GET', 'POST'])
@login_required
def admin_table_add(table_name):
    if table_name not in ADMIN_TABLES:
        abort(404)
    meta = TABLES.get(table_name, {})
    if meta.get('readonly'):
        return redirect(url_for('admin_table_list', table_name=table_name))
    
    if request.method == 'POST':
        db = get_db()
        pk = meta.get('pk', 'id')
        cols = []
        vals = []
        placeholders = []
        for field_name, field_meta in meta['fields'].items():
            if field_name == pk or field_meta['type'] == 'readonly':
                continue
            val = request.form.get(field_name, '').strip()
            if field_name == 'featured':
                val = 1 if request.form.get(field_name) == 'on' else 0
            cols.append(field_name)
            vals.append(val if val else None)
            placeholders.append('?')
        sql = f'INSERT INTO {table_name} ({", ".join(cols)}) VALUES ({", ".join(placeholders)})'
        try:
            db.execute(sql, vals)
            db.commit()
            return redirect(url_for('admin_table_list', table_name=table_name, _anchor=''))
        except Exception as e:
            return render_template('admin/table_edit.html', table_name=table_name, meta=meta,
                                   record=None, error=str(e))
    return render_template('admin/table_edit.html', table_name=table_name, meta=meta, record=None)

@app.route('/admin/<table_name>/<record_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_table_edit(table_name, record_id):
    if table_name not in ADMIN_TABLES:
        abort(404)
    meta = TABLES.get(table_name, {})
    if meta.get('readonly'):
        return redirect(url_for('admin_table_list', table_name=table_name))
    
    pk = meta.get('pk', 'id')
    db = get_db()
    try:
        row = db.execute(f'SELECT * FROM {table_name} WHERE {pk} = ?', (record_id,)).fetchone()
    except Exception:
        row = None
    if not row:
        abort(404)
    
    if request.method == 'POST':
        set_clauses = []
        vals = []
        for field_name, field_meta in meta['fields'].items():
            if field_name == pk or field_meta['type'] == 'readonly':
                continue
            val = request.form.get(field_name, '').strip()
            if field_name == 'featured':
                val = 1 if request.form.get(field_name) == 'on' else 0
            set_clauses.append(f'{field_name} = ?')
            vals.append(val if val else None)
        vals.append(record_id)
        sql = f'UPDATE {table_name} SET {", ".join(set_clauses)} WHERE {pk} = ?'
        try:
            db.execute(sql, vals)
            db.commit()
            return redirect(url_for('admin_table_list', table_name=table_name))
        except Exception as e:
            return render_template('admin/table_edit.html', table_name=table_name, meta=meta,
                                   record=dict_from_row(row), error=str(e))
    return render_template('admin/table_edit.html', table_name=table_name, meta=meta, record=dict_from_row(row))

@app.route('/admin/<table_name>/<record_id>/delete', methods=['POST'])
@login_required
def admin_table_delete(table_name, record_id):
    if table_name not in ADMIN_TABLES:
        abort(404)
    meta = TABLES.get(table_name, {})
    if meta.get('readonly'):
        return redirect(url_for('admin_table_list', table_name=table_name))
    pk = meta.get('pk', 'id')
    db = get_db()
    try:
        db.execute(f'DELETE FROM {table_name} WHERE {pk} = ?', (record_id,))
        db.commit()
    except Exception as e:
        app.logger.exception('Delete failed on %s (id %s)', table_name, record_id)
    return redirect(url_for('admin_table_list', table_name=table_name))

@app.route('/admin/messages/<int:msg_id>/toggle-read', methods=['POST'])
@login_required
def admin_toggle_read(msg_id):
    db = get_db()
    try:
        msg = db.execute('SELECT is_read FROM contact_messages WHERE id = ?', (msg_id,)).fetchone()
        if msg:
            new_val = 0 if msg['is_read'] else 1
            db.execute('UPDATE contact_messages SET is_read = ? WHERE id = ?', (new_val, msg_id))
            db.commit()
    except Exception:
        app.logger.exception('Toggle-read failed for message %s', msg_id)
    return redirect(url_for('admin_table_list', table_name='contact_messages'))

@app.route('/healthz')
def healthz():
    """Lightweight health probe for the installer, task scheduler and uptime checks."""
    try:
        get_db().execute('SELECT 1').fetchone()
        return jsonify({'status': 'ok', 'database': 'ok'})
    except Exception:
        app.logger.exception('Health check failed')
        return jsonify({'status': 'error', 'database': 'error'}), 500

@app.route('/robots.txt')
def robots():
    response = make_response(f"User-agent: *\nDisallow: /admin/\nSitemap: {url_for('sitemap', _external=True)}\n")
    response.mimetype = 'text/plain'
    return response

@app.route('/sitemap.xml')
def sitemap():
    static_endpoints = ['home', 'services', 'about', 'contact', 'weekly_flyer', 'products', 'minor_ailment']
    urls = [url_for(endpoint, _external=True) for endpoint in static_endpoints]
    try:
        rows = get_db().execute('SELECT slug FROM services').fetchall()
        urls.extend(url_for('service_detail', slug=row['slug'], _external=True) for row in rows)
    except Exception:
        app.logger.exception('Unable to load service URLs for sitemap')
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    xml += ''.join(f'<url><loc>{url}</loc></url>' for url in urls)
    xml += '</urlset>'
    response = make_response(xml)
    response.mimetype = 'application/xml'
    return response

@app.route('/legal/<page>')
def legal(page):
    titles = {'privacy': 'Privacy Policy', 'terms': 'Terms & Conditions', 'disclaimer': 'Health Disclaimer'}
    if page not in titles:
        abort(404)
    return render_template('legal.html', legal_title=titles[page])

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(error):
    app.logger.exception('Unhandled application error')
    return render_template('500.html'), 500

# ── Main ──────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        init_db()
    # Development entry only: loopback-bound, debugger OFF unless FLASK_DEBUG=1.
    # Production must use run_prod.py (Waitress, loopback + Tailscale only).
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    app.run(host='127.0.0.1', port=5000, debug=debug)
