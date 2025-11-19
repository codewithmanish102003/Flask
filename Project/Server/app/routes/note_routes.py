import datetime

from bson.objectid import ObjectId
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..models.note_model import Note

note_bp = Blueprint('note_bp', __name__)

# Helper function to serialize note
def serialize_note(n):
    return {
        "id": str(n["_id"]),
        "title": n["title"],
        "content": n["content"],
        "author_id": str(n["author_id"]),
        "author_username": n.get("author_username"),
        "likes": n.get("likes", []),
        "comments": n.get("comments", []),   
        "created_at": n.get("created_at")
    }

@note_bp.route("/", methods=["GET"])
@note_bp.route("", methods=["GET"])
def list_notes():
    db = current_app.db
    q = db.notes.find().sort("created_at", -1)
    result = [serialize_note(n) for n in q]
    return jsonify(result), 200

@note_bp.route("/<note_id>", methods=["GET"])
def get_note(note_id):
    db = current_app.db
    n = db.notes.find_one({"_id": ObjectId(note_id)})
    if not n:
        return jsonify({"msg":"not found"}), 404
    return jsonify(serialize_note(n)), 200

@note_bp.route("/", methods=["POST"])
@note_bp.route("", methods=["POST"])
@jwt_required()
def create_note():
    current_user_id = get_jwt_identity()
    db = current_app.db
    user = db.users.find_one({"_id": ObjectId(current_user_id)})
    if not user:
        return jsonify({"msg":"user not found"}), 404
    data = request.json
    title = data.get("title")
    content = data.get("content")
    if not title or not content:
        return jsonify({"msg":"title and content required"}), 400
    
    note = Note(
        title=title,
        content=content,
        author_id=current_user_id,
        author_username=user["username"]
    )
    
    res = db.notes.insert_one(note.to_dict())
    note_dict = note.to_dict()
    note_dict["_id"] = res.inserted_id
    return jsonify(serialize_note(note_dict)), 201

@note_bp.route("/<note_id>", methods=["DELETE"])
@note_bp.route("/<note_id>/", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    current_user_id = get_jwt_identity()
    db = current_app.db
    n = db.notes.find_one({"_id": ObjectId(note_id)})
    if not n:
        return jsonify({"msg":"not found"}), 404
    if str(n["author_id"]) != current_user_id:
        return jsonify({"msg":"forbidden"}), 403
    db.notes.delete_one({"_id": ObjectId(note_id)})
    return jsonify({"msg":"deleted"}), 200

# Like toggle
@note_bp.route("/<note_id>/like", methods=["POST"])
@note_bp.route("/<note_id>/like/", methods=["POST"])
@jwt_required()
def like_note(note_id):
    user_id = get_jwt_identity()
    db = current_app.db
    n = db.notes.find_one({"_id": ObjectId(note_id)})
    if not n:
        return jsonify({"msg":"not found"}), 404
    likes = n.get("likes", [])
    if user_id in likes:
        # unlike
        db.notes.update_one({"_id": ObjectId(note_id)}, {"$pull": {"likes": user_id}})
        return jsonify({"liked": False, "count": len(likes)-1}), 200
    else:
        db.notes.update_one({"_id": ObjectId(note_id)}, {"$push": {"likes": user_id}})
        return jsonify({"liked": True, "count": len(likes)+1}), 200

# Comment
@note_bp.route("/<note_id>/comment", methods=["POST"])
@note_bp.route("/<note_id>/comment/", methods=["POST"])
@jwt_required()
def comment_note(note_id):
    user_id = get_jwt_identity()
    db = current_app.db
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({"msg":"user not found"}), 404
    n = db.notes.find_one({"_id": ObjectId(note_id)})
    if not n:
        return jsonify({"msg":"not found"}), 404
    data = request.json
    text = data.get("content")
    if not text:
        return jsonify({"msg":"content required"}), 400
    comment = {
        "id": str(ObjectId()),
        "user_id": user_id,
        "username": user["username"],
        "content": text,
        "created_at": datetime.datetime.utcnow()
    }
    db.notes.update_one({"_id": ObjectId(note_id)}, {"$push": {"comments": comment}})
    return jsonify(comment), 201

# Delete comment (author of comment or note can delete)
@note_bp.route("/<note_id>/comment/<comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(note_id, comment_id):
    user_id = get_jwt_identity()
    db = current_app.db
    n = db.notes.find_one({"_id": ObjectId(note_id)})
    if not n:
        return jsonify({"msg":"not found"}), 404
    comment = next((c for c in n.get("comments", []) if c["id"] == comment_id), None)
    if not comment:
        return jsonify({"msg":"comment not found"}), 404
    # allow if comment author or note author
    if comment["user_id"] != user_id and str(n["author_id"]) != user_id:
        return jsonify({"msg":"forbidden"}), 403
    db.notes.update_one({"_id": ObjectId(note_id)}, {"$pull": {"comments": {"id": comment_id}}})
    return jsonify({"msg":"deleted"}), 200