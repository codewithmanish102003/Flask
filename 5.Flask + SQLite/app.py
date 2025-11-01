import sqlite3
from flask import Flask, abort, g, jsonify, request

app = Flask(__name__)
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )
    """)
    db.commit()

with app.app_context():
    init_db()

@app.route('/items', methods=['GET'])
def list_items():
    db = get_db()
    cur = db.execute('SELECT id, name, description FROM items')
    rows = cur.fetchall()
    items = [dict(row) for row in rows]
    return jsonify(items)

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    db = get_db()
    cur = db.execute('SELECT id, name, description FROM items WHERE id = ?', (item_id,))
    row = cur.fetchone()
    if row is None:
        abort(404, description='Item not found')
    return jsonify(dict(row))

@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description', '')
    if not name:
        abort(400, description='Missing "name" field')
    db = get_db()
    cur = db.execute('INSERT INTO items (name, description) VALUES (?, ?)', (name, description))
    db.commit()
    item_id = cur.lastrowid
    return jsonify({'id': item_id, 'name': name, 'description': description}), 201

@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description')
    if name is None and description is None:
        abort(400, description='Provide "name" or "description" to update')
    db = get_db()
    cur = db.execute('SELECT id FROM items WHERE id = ?', (item_id,))
    if cur.fetchone() is None:
        abort(404, description='Item not found')
    fields = []
    values = []
    if name is not None:
        fields.append('name = ?')
        values.append(name)
    if description is not None:
        fields.append('description = ?')
        values.append(description)
    values.append(item_id)
    db.execute(f'UPDATE items SET {", ".join(fields)} WHERE id = ?', tuple(values))
    db.commit()
    cur = db.execute('SELECT id, name, description FROM items WHERE id = ?', (item_id,))
    return jsonify(dict(cur.fetchone()))

@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    db = get_db()
    cur = db.execute('SELECT id FROM items WHERE id = ?', (item_id,))
    if cur.fetchone() is None:
        abort(404, description='Item not found')
    db.execute('DELETE FROM items WHERE id = ?', (item_id,))
    db.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
