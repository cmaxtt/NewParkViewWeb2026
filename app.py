"""
Park View Drugs — Flask Application
"""
import os
import sqlite3
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, jsonify, g, session, redirect, url_for, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'park-view-drugs-secret-key-2026'
app.config['DATABASE'] = os.path.join(app.instance_path, 'parkview.db')
app.config['ADMIN_PASSWORD'] = 'admin123'  # change this in production

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
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(exception=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

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

def get_table_columns(table_name):
    db = get_db()
    cursor = db.execute(f'PRAGMA table_info({table_name})')
    return [row['name'] for row in cursor.fetchall()]

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
    return {'settings': settings, 'now': datetime.now, 'tables_meta': TABLES}

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
        if name and email and message:
            db = get_db()
            db.execute(
                'INSERT INTO contact_messages (name, email, subject, message) VALUES (?, ?, ?, ?)',
                (name, email, subject, message)
            )
            db.commit()
            return jsonify({'success': True, 'message': 'Thank you! We will get back to you shortly.'})
        return jsonify({'success': False, 'message': 'Please fill in all required fields.'}), 400
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
        if category:
            products_list = db.execute('SELECT * FROM products WHERE category = ?', (category,)).fetchall()
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
    if email:
        try:
            db = get_db()
            db.execute('INSERT OR IGNORE INTO newsletter_subscribers (email) VALUES (?)', (email,))
            db.commit()
            return jsonify({'success': True, 'message': 'Subscribed successfully!'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    return jsonify({'success': False, 'message': 'Email is required.'}), 400

# ── Admin Routes ──────────────────────────────────────────

ADMIN_TABLES = ['services', 'products', 'flyer_deals', 'contact_messages', 'newsletter_subscribers', 'site_settings']

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            next_page = request.args.get('next', url_for('admin_dashboard'))
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

@app.route('/admin/<table_name>/<int:record_id>/edit', methods=['GET', 'POST'])
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

@app.route('/admin/<table_name>/<int:record_id>/delete', methods=['POST'])
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
        pass
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
        pass
    return redirect(url_for('admin_table_list', table_name='contact_messages'))

# ── Main ──────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
