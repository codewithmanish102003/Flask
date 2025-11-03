import os

from bson import ObjectId
from flask import Flask, jsonify, request
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

app = Flask(__name__)
# Use a more explicit default for local MongoDB
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/flask_db')

def get_db():
    """Get database connection or return error response"""
    global db
    if db is None:
        return None
    return db

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.server_info()  # Will raise an exception if can't connect
    db = client['flask_db']
    print("MongoDB connected successfully!")
except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    print(f"Failed to connect to MongoDB: {e}")
    db = None

@app.route('/')
def home():
    if db is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
    try:
        db.command('ping')
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    return "Mongo db connected successfully!"


# create
@app.route('/api/users', methods=['POST'])
def create_user():
    if db is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
        
    data = request.get_json()
    name=data.get('name')
    email=data.get('email')
    age=data.get('age')

    if not name or not email or not age:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    user = {
        'name': name,
        'email': email,
        'age': age
    }

    try:
        db.users.insert_one(user)
        return jsonify({'status': 'success', 'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# read
@app.route('/api/users', methods=['GET'])
def get_users():
    if db is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
        
    try:
        users = db.users.find()
        user_list = []
        for user in users:
            user_list.append({
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'age': user['age']
            })
        return jsonify({'status': 'success', 'users': user_list}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# read by id
@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    if db is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
        
    try:
        user = db.users.find_one({'_id':ObjectId(user_id)})
        if user:
            return jsonify({
                'id': str(user['_id']),
                'name': user['name'],
                'email': user['email'],
                'age': user['age']
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# update by id
# update
from bson.errors import InvalidId


# 🔹 UPDATE USER
@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    if db is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
        
    try:
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'message': 'Empty request body'}), 400

        # Build update dictionary dynamically
        update_data = {k: v for k, v in data.items() if v is not None}

        if not update_data:
            return jsonify({'status': 'error', 'message': 'No fields to update'}), 400

        # Convert string ID to ObjectId safely
        try:
            oid = ObjectId(user_id)
        except InvalidId:
            return jsonify({'status': 'error', 'message': 'Invalid user ID format'}), 400

        result = db.users.update_one({'_id': oid}, {'$set': update_data})

        if result.matched_count == 0:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        updated_user = db.users.find_one({'_id': oid})
        if updated_user:
            updated_user['_id'] = str(updated_user['_id'])
            return jsonify({'status': 'success', 'message': 'User updated successfully', 'user': updated_user}), 200
        else:
            return jsonify({'status': 'error', 'message': 'User not found after update'}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 🔹 DELETE USER
@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    if db is None:
        return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
        
    try:
        # Convert ID safely
        try:
            oid = ObjectId(user_id)
        except InvalidId:
            return jsonify({'status': 'error', 'message': 'Invalid user ID format'}), 400

        # Find the user before deleting to return their info
        user = db.users.find_one({'_id': oid})
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
            
        # Format user data before deletion
        user_data = {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'age': user['age']
        }

        result = db.users.delete_one({'_id': oid})

        if result.deleted_count == 0:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        return jsonify({'status': 'success', 'message': 'User deleted successfully', 'user': user_data}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)