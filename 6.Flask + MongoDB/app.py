import os
from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import Flask, jsonify, request
from pymongo import MongoClient

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
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    age = data.get('age')

    if not name or not email:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    user = {'name': name, 'email': email}
    if age is not None:
        try:
            user['age'] = int(age)
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Invalid age'}), 400

    try:
        res = db.users.insert_one(user)
        created = db.users.find_one({'_id': res.inserted_id})
        created['id'] = str(created.pop('_id'))
        return jsonify({'status': 'success', 'user': created}), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# read all
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = db.users.find()
        user_list = []
        for user in users:
            user_list.append({
                'id': str(user['_id']),
                'name': user.get('name'),
                'email': user.get('email'),
                'age': user.get('age')
            })
        return jsonify({'status': 'success', 'users': user_list}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# read by id
@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        oid = ObjectId(user_id)
    except (InvalidId, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid id'}), 400

    try:
        user = db.users.find_one({'_id': oid})
        if user:
            return jsonify({
                'id': str(user['_id']),
                'name': user.get('name'),
                'email': user.get('email'),
                'age': user.get('age')
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# update by id (partial allowed)
@app.route('/api/users/update/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        oid = ObjectId(user_id)
    except (InvalidId, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid id'}), 400

    data = request.get_json() or {}
    update = {}
    if 'name' in data:
        update['name'] = data['name']
    if 'email' in data:
        update['email'] = data['email']
    if 'age' in data:
        try:
            update['age'] = int(data['age'])
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Invalid age'}), 400

    if not update:
        return jsonify({'status': 'error', 'message': 'Provide at least one field to update'}), 400

    try:
        res = db.users.update_one({'_id': oid}, {'$set': update})
        if res.matched_count == 0:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        user = db.users.find_one({'_id': oid})
        user['id'] = str(user.pop('_id'))
        return jsonify({'status': 'success', 'user': user}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# delete
@app.route('/api/users/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        oid = ObjectId(user_id)
    except (InvalidId, TypeError):
        return jsonify({'status': 'error', 'message': 'Invalid id'}), 400

    try:
        res = db.users.delete_one({'_id': oid})
        if res.deleted_count == 0:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        return jsonify({'status': 'success', 'message': 'User deleted successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)