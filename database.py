import sqlite3

def setup_database() -> sqlite3.Connection:
    conn = sqlite3.connect('logistics.sqlite')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS warehouses (
        id INTEGER PRIMARY KEY, city TEXT NOT NULL, capacity INTEGER NOT NULL);''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
        sku TEXT PRIMARY KEY, name TEXT NOT NULL, weight_kg REAL NOT NULL);''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
        warehouse_id INTEGER, sku TEXT, quantity INTEGER NOT NULL, status TEXT NOT NULL,
        PRIMARY KEY (warehouse_id, sku),
        FOREIGN KEY (warehouse_id) REFERENCES warehouses (id),
        FOREIGN KEY (sku) REFERENCES products (sku));''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS queries (
        id TEXT PRIMARY KEY, status TEXT NOT NULL, result TEXT);''')
    cursor.executemany('INSERT OR IGNORE INTO warehouses VALUES (?, ?, ?)',
        [(1, 'Madrid', 5000), (2, 'Barcelona', 8000)])
    cursor.executemany('INSERT OR IGNORE INTO products VALUES (?, ?, ?)',
        [('P001', 'Monitor 24', 3.5), ('P002', 'Teclado', 0.8)])
    cursor.executemany('INSERT OR IGNORE INTO inventory VALUES (?, ?, ?, ?)',
        [(1, 'P001', 100, 'AVAILABLE'), (2, 'P001', 20, 'DAMAGED')])
    conn.commit()
    return conn
