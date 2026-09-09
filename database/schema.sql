-- Park View Drugs Database Schema

CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL DEFAULT 'fas fa-circle',
    slug TEXT NOT NULL UNIQUE,
    page_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL DEFAULT 'General',
    price DECIMAL(10,2),
    list_price DECIMAL(10,2),
    savings DECIMAL(10,2),
    savings_percent DECIMAL(5,2),
    image TEXT,
    featured INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS flyer_deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    image TEXT,
    price DECIMAL(10,2),
    list_price DECIMAL(10,2),
    savings DECIMAL(10,2),
    savings_percent DECIMAL(5,2),
    icon TEXT NOT NULL DEFAULT 'fas fa-tag',
    color_start TEXT DEFAULT '#E8F5E9',
    color_end TEXT DEFAULT '#A5D6A7',
    icon_color TEXT DEFAULT '#1E7D29',
    valid_until TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (title, description, valid_until)
);

CREATE TABLE IF NOT EXISTS contact_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT,
    message TEXT NOT NULL,
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS site_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Seed site settings
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('business_name', 'Park View Drugs');
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('phone', '(868) 223-7508');
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('address', 'Esperance, San Fernando, Trinidad & Tobago');
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('full_address', 'S.S. Erin Road, Esperance, Trinidad & Tobago');
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('hours_weekday', 'Mon-Fri: 8AM-6PM');
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('hours_saturday', 'Sat: 8AM-3PM');
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('hours_sunday', 'Sun: Closed');
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('facebook_url', 'https://www.facebook.com/pvdrugs/');
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('tagline', 'Your trusted local pharmacy serving the San Fernando community.');
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('hero_title_1', 'Your Health, Our Priority');
INSERT OR IGNORE INTO site_settings (key, value) VALUES ('hero_desc_1', 'At Park View Drugs, we''re committed to providing personalized pharmacy care for you and your family.');

-- Seed services
INSERT OR IGNORE INTO services (title, description, icon, slug) VALUES ('Minor Ailment Assessment', 'Get assessed and prescribed for common minor ailments by your pharmacist.', 'fas fa-stethoscope', 'minor-ailment');
INSERT OR IGNORE INTO services (title, description, icon, slug) VALUES ('Vaccinations', 'Protect yourself with a full range of vaccinations including flu, COVID-19, and more.', 'fas fa-syringe', 'vaccinations');
INSERT OR IGNORE INTO services (title, description, icon, slug) VALUES ('Prescription Refills', 'Quick and easy prescription refills. Call ahead or visit us.', 'fas fa-prescription', 'prescription-refills');
INSERT OR IGNORE INTO services (title, description, icon, slug) VALUES ('Compounding', 'Customized medications formulated to meet your specific health needs.', 'fas fa-pills', 'compounding');
INSERT OR IGNORE INTO services (title, description, icon, slug) VALUES ('Medication Review', 'Comprehensive review of all your medications to ensure they work safely together.', 'fas fa-notes-medical', 'medication-review');
INSERT OR IGNORE INTO services (title, description, icon, slug) VALUES ('Home Delivery', 'Convenient home delivery of your prescriptions and health essentials.', 'fas fa-truck', 'delivery');

-- Seed featured vitamin products for the weekly flyer.
INSERT INTO products (name, description, category, price, list_price, savings, savings_percent, image, featured)
SELECT 'Nature Made Vitamin D3 2000 IU, 100 ct', 'Daily vitamin D3 supplement, 100 tablets.', 'Vitamins', 24.60, 54.66, 30.06, 55, 'images/nature-made-vitamin-d3-100ct.jpg', 1
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Nature Made Vitamin D3 2000 IU, 100 ct');
INSERT INTO products (name, description, category, price, list_price, savings, savings_percent, image, featured)
SELECT 'Centrum Silver Adult Multivitamin, 80 ct', 'Complete adult multivitamin tablets for daily wellness.', 'Vitamins', 21.52, 53.79, 32.27, 60, 'images/centrum-silver-80ct.jpg', 1
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Centrum Silver Adult Multivitamin, 80 ct');
INSERT INTO products (name, description, category, price, list_price, savings, savings_percent, image, featured)
SELECT 'Vitafusion MultiVites Adult Gummies, 70 ct', 'Berry, peach and orange-flavored complete multivitamin gummies.', 'Vitamins', 20.13, 40.26, 20.13, 50, 'images/vitafusion-multivites-70ct.jpg', 1
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Vitafusion MultiVites Adult Gummies, 70 ct');
INSERT INTO products (name, description, category, price, list_price, savings, savings_percent, image, featured)
SELECT 'Nature''s Truth Vitamin B-12 1000 mcg, 100 ct', 'Vitamin B-12 tablets, 1000 mcg, 100 count.', 'Vitamins', 20.00, 57.15, 37.15, 65, 'images/natures-truth-vitamin-b12-100ct.jpg', 1
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Nature''s Truth Vitamin B-12 1000 mcg, 100 ct');
INSERT INTO products (name, description, category, price, list_price, savings, savings_percent, image, featured)
SELECT 'Nature''s Nutrition Magnesium Glycinate 250 mg, 60 ct', 'Chelated magnesium glycinate tablets, 250 mg per serving.', 'Vitamins', 26.72, 59.38, 32.66, 55, 'images/natures-nutrition-magnesium-glycinate-60ct.jpg', 1
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'Nature''s Nutrition Magnesium Glycinate 250 mg, 60 ct');
INSERT INTO products (name, description, category, price, list_price, savings, savings_percent, image, featured)
SELECT 'One A Day Men''s VitaCraves Gummies, 70 ct', 'Daily multivitamin gummies for men, assorted fruit flavors.', 'Vitamins', 24.56, 61.40, 36.84, 60, 'images/one-a-day-vitacraves-70ct.jpg', 1
WHERE NOT EXISTS (SELECT 1 FROM products WHERE name = 'One A Day Men''s VitaCraves Gummies, 70 ct');

-- Seed flyer deals
INSERT INTO flyer_deals (title, description, icon, color_start, color_end, icon_color, valid_until)
SELECT 'Vitamins & Supplements', 'Save up to 25% on select vitamin and supplement brands.', 'fas fa-tablets', '#E8F5E9', '#A5D6A7', '#1E7D29', '2026-07-12'
WHERE NOT EXISTS (SELECT 1 FROM flyer_deals WHERE title = 'Vitamins & Supplements' AND description = 'Save up to 25% on select vitamin and supplement brands.' AND valid_until = '2026-07-12');
INSERT INTO flyer_deals (title, description, icon, color_start, color_end, icon_color, valid_until)
SELECT 'First Aid Essentials', 'Buy one, get one 50% off on all first aid supplies.', 'fas fa-hand-holding-heart', '#FFF3E0', '#FFCC80', '#E65100', '2026-07-12'
WHERE NOT EXISTS (SELECT 1 FROM flyer_deals WHERE title = 'First Aid Essentials' AND description = 'Buy one, get one 50% off on all first aid supplies.' AND valid_until = '2026-07-12');
INSERT INTO flyer_deals (title, description, icon, color_start, color_end, icon_color, valid_until)
SELECT 'Natural Health Products', '20% off all natural health products from top brands.', 'fas fa-apple-alt', '#E8F5E9', '#81C784', '#2E7D32', '2026-07-12'
WHERE NOT EXISTS (SELECT 1 FROM flyer_deals WHERE title = 'Natural Health Products' AND description = '20% off all natural health products from top brands.' AND valid_until = '2026-07-12');
INSERT INTO flyer_deals (title, description, icon, color_start, color_end, icon_color, valid_until)
SELECT 'Baby & Kids Care', 'Save $5 on all baby care purchases over $25.', 'fas fa-baby', '#F3E5F5', '#CE93D8', '#6A1B9A', '2026-07-12'
WHERE NOT EXISTS (SELECT 1 FROM flyer_deals WHERE title = 'Baby & Kids Care' AND description = 'Save $5 on all baby care purchases over $25.' AND valid_until = '2026-07-12');
INSERT INTO flyer_deals (title, description, icon, color_start, color_end, icon_color, valid_until)
SELECT 'Summer Essentials', '25% off sunscreen, insect repellent, and travel sizes.', 'fas fa-sun', '#FFF8E1', '#FFD54F', '#F57F17', '2026-07-12'
WHERE NOT EXISTS (SELECT 1 FROM flyer_deals WHERE title = 'Summer Essentials' AND description = '25% off sunscreen, insect repellent, and travel sizes.' AND valid_until = '2026-07-12');
INSERT INTO flyer_deals (title, description, icon, color_start, color_end, icon_color, valid_until)
SELECT 'Heart Health', 'Buy 2, get 1 free on all heart health supplements.', 'fas fa-heart', '#FCE4EC', '#F48FB1', '#C62828', '2026-07-12'
WHERE NOT EXISTS (SELECT 1 FROM flyer_deals WHERE title = 'Heart Health' AND description = 'Buy 2, get 1 free on all heart health supplements.' AND valid_until = '2026-07-12');
