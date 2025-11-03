import os

from flask import Flask, jsonify, request
from pymongo import MongoClient
from this import d

app = Flask(__name__)
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URI)
db = client['flask_db']

@app.route('/')
def home():
    try:
        db.command('ping')
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    return "Mongo db connected successfully!"


# create
@app.route('/api/users', methods=['POST'])
def create_user():
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
    try:
        user = db.users.find_one({'_id': user_id})
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
@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):   
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
        db.users.update_one({'_id': user_id}, {'$set': user})
        return jsonify({'status': 'success', 'message': 'User updated successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# delete
@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        db.users.delete_one({'_id': user_id})
        return jsonify({'status': 'success', 'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)