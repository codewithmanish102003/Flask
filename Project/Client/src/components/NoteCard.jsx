import React from "react";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import API from "../services/api";

const NoteCard = ({ note, onUpdated }) => {
  const { user } = React.useContext(AuthContext);

  const toggleLike = async () => {
    if (!user) { alert("Please login"); return; }
    await API.post(`/notes/${note.id}/like`);
    onUpdated();
  };

  const deleteNote = async () => {
    if (!user) return;
    try {
      await API.delete(`/notes/${note.id}`);
      onUpdated();
    } catch (e) { alert("delete failed"); }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <h3 className="text-xl font-bold mb-2">
        <Link to={`/note/${note.id}`} className="text-blue-600 hover:text-blue-800">
          {note.title}
        </Link>
      </h3>
      <p className="text-gray-700 mb-4">
        {note.content.slice(0, 150)}
        {note.content.length > 150 && "..."}
      </p>
      <p className="text-sm text-gray-500 mb-2">By: {note.author_username}</p>
      <p className="text-sm text-gray-500 mb-4">
        Likes: {note.likes?.length || 0} Comments: {note.comments?.length || 0}
      </p>
      <div className="flex space-x-2">
        <button 
          onClick={toggleLike}
          className={`px-3 py-1 rounded ${user && note.likes && note.likes.includes(user.id) ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'} text-white`}
        >
          {user && note.likes && note.likes.includes(user.id) ? "Unlike" : "Like"}
        </button>
        {user && user.id === note.author_id && (
          <button 
            onClick={deleteNote}
            className="px-3 py-1 bg-red-500 hover:bg-red-700 text-white rounded"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
};

export default NoteCard;
