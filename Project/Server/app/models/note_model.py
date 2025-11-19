import datetime

from bson.objectid import ObjectId


class Note:
    def __init__(self, title, content, author_id, author_username=None, likes=None, comments=None, created_at=None):
        self.title = title
        self.content = content
        self.author_id = ObjectId(author_id) if isinstance(author_id, str) else author_id
        self.author_username = author_username
        self.likes = likes or []
        self.comments = comments or []
        self.created_at = created_at or datetime.datetime.utcnow()
    
    def to_dict(self):
        return {
            "title": self.title,
            "content": self.content,
            "author_id": self.author_id,
            "author_username": self.author_username,
            "likes": self.likes,
            "comments": self.comments,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        note = cls(
            title=data.get("title"),
            content=data.get("content"),
            author_id=data.get("author_id"),
            author_username=data.get("author_username"),
            likes=data.get("likes", []),
            comments=data.get("comments", []),
            created_at=data.get("created_at")
        )
        # Convert string IDs to ObjectId if needed
        if isinstance(note.author_id, str):
            note.author_id = ObjectId(note.author_id)
        return note