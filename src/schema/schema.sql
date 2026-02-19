/*
Schéma PostgreSQL pour le dataset Brazilian E-commerce

Ce schéma est optimisé pour:
- Analytics et business intelligence
- Intégrité des données
- Performances de requêtes
*/

-- ============================================================================
-- TABLES DE DIMENSIONS
-- ============================================================================

-- 1. CUSTOMERS (base de données clients)
CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(32) PRIMARY KEY,
    customer_unique_id VARCHAR(32) NOT NULL,
    zip_code_prefix INTEGER NOT NULL,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL
);

CREATE INDEX idx_customers_state ON customers(state);
CREATE INDEX idx_customers_unique_id ON customers(customer_unique_id);


-- 2. GEOLOCATION (codes postaux et localisation)
CREATE TABLE IF NOT EXISTS geolocation (
    zip_code_prefix INTEGER PRIMARY KEY,
    city VARCHAR(255) NOT NULL,
    state VARCHAR(2) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

CREATE INDEX idx_geo_state ON geolocation(state);
CREATE INDEX idx_geo_city ON geolocation(city);


-- 3. PRODUCTS (catalogue de produits)
CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(32) PRIMARY KEY,
    category_pt VARCHAR(100),
    category_en VARCHAR(100),
    name_length FLOAT,
    description_length FLOAT,
    photo_qty FLOAT,
    weight_g FLOAT,
    length_cm FLOAT,
    height_cm FLOAT,
    width_cm FLOAT
);

CREATE INDEX idx_products_category ON products(category_en);


-- 4. SELLERS (vendeurs)
CREATE TABLE IF NOT EXISTS sellers (
    seller_id VARCHAR(32) PRIMARY KEY,
    zip_code_prefix INTEGER,
    city VARCHAR(255),
    state VARCHAR(2),
    FOREIGN KEY (zip_code_prefix) REFERENCES geolocation(zip_code_prefix)
);

CREATE INDEX idx_sellers_state ON sellers(state);
CREATE INDEX idx_sellers_zip ON sellers(zip_code_prefix);


-- ============================================================================
-- TABLES DE FAITS (Facts)
-- ============================================================================

-- 5. ORDERS (commandes)
CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32) NOT NULL,
    status VARCHAR(20) NOT NULL,
    purchase_date TIMESTAMP NOT NULL,
    purchase_year INTEGER,
    purchase_month INTEGER,
    approved_date TIMESTAMP,
    carrier_delivery_date TIMESTAMP,
    customer_delivery_date TIMESTAMP,
    estimated_delivery_date TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_purchase_date ON orders(purchase_date);
CREATE INDEX idx_orders_year_month ON orders(purchase_year, purchase_month);


-- 6. ORDER_ITEMS (articles dans les commandes)
CREATE TABLE IF NOT EXISTS order_items (
    order_id VARCHAR(32) NOT NULL,
    product_id VARCHAR(32) NOT NULL,
    seller_id VARCHAR(32) NOT NULL,
    price FLOAT NOT NULL,
    freight_value FLOAT NOT NULL,
    total_price FLOAT NOT NULL,
    PRIMARY KEY (order_id, product_id, seller_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);
CREATE INDEX idx_order_items_seller ON order_items(seller_id);


-- 7. ORDER_PAYMENTS (paiements des commandes)
CREATE TABLE IF NOT EXISTS order_payments (
    order_id VARCHAR(32) NOT NULL,
    type VARCHAR(20),
    installments INTEGER DEFAULT 1,
    value FLOAT NOT NULL,
    PRIMARY KEY (order_id, type),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE INDEX idx_payments_order ON order_payments(order_id);
CREATE INDEX idx_payments_type ON order_payments(type);


-- 8. ORDER_REVIEWS (avis des clients)
CREATE TABLE IF NOT EXISTS order_reviews (
    review_id VARCHAR(32) PRIMARY KEY,
    order_id VARCHAR(32) NOT NULL,
    score INTEGER CHECK (score >= 1 AND score <= 5),
    comment_title VARCHAR(255),
    comment_message TEXT,
    creation_date TIMESTAMP,
    answer_timestamp TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE INDEX idx_reviews_order ON order_reviews(order_id);
CREATE INDEX idx_reviews_score ON order_reviews(score);
CREATE INDEX idx_reviews_date ON order_reviews(creation_date);


-- ============================================================================
-- TABLES ANALYTIQUES (Optional - pour optimiser les requêtes)
-- ============================================================================

-- 9. FACT_ORDERS (table précalculée pour l'analyse)
CREATE TABLE IF NOT EXISTS fact_orders (
    order_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32),
    purchase_date TIMESTAMP,
    purchase_year INTEGER,
    purchase_month INTEGER,
    status VARCHAR(20),
    items_count INTEGER,
    total_items_price FLOAT,
    total_payment FLOAT,
    avg_review_score FLOAT,
    approved_date TIMESTAMP,
    carrier_delivery_date TIMESTAMP,
    customer_delivery_date TIMESTAMP,
    estimated_delivery_date TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE INDEX idx_fact_orders_customer ON fact_orders(customer_id);
CREATE INDEX idx_fact_orders_date ON fact_orders(purchase_date);
CREATE INDEX idx_fact_orders_status ON fact_orders(status);


-- ============================================================================
-- STATISTIQUES SOL
-- ============================================================================

-- Créer des statistiques pour les colonnes importantes
ANALYZE customers;
ANALYZE products;
ANALYZE orders;
ANALYZE order_items;
ANALYZE geolocation;
ANALYZE sellers;
