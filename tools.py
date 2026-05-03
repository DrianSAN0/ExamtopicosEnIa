import sqlite3, csv, os

def execute_sql(conn: sqlite3.Connection, query: str, query_history=None) -> str:
    if not query.strip().upper().startswith('SELECT'):
        return 'Error de permisos: Solo se permiten operaciones SELECT. Sin permisos de escritura.'
    if query_history is not None:
        query_history.append(query)
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        if cursor.description:
            return str(cursor.fetchall())
        conn.commit()
        return 'Operacion realizada.'
    except sqlite3.Error as e:
        return f'Error SQL: {e}'

def get_schema(conn: sqlite3.Connection, table_name=None) -> str:
    cursor = conn.cursor()
    if table_name:
        cursor.execute(f'PRAGMA table_info({table_name});')
        return str([(col[1], col[2]) for col in cursor.fetchall()])
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return str([t[0] for t in cursor.fetchall()])

def export_shipping_manifest(data: list, filename: str) -> str:
    print(f'   [Tool Action] Exportando manifiesto a {filename}...')
    try:
        directory = os.path.dirname(filename)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['SKU', 'Nombre', 'Cantidad'])
            writer.writerows(data)
        return f'Manifiesto exportado en: {os.path.abspath(filename)}'
    except Exception as e:
        return f'Error al exportar manifiesto: {e}'