import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../services/api";

const NoteDetail = () => {
  const { id } = useParams();
  const [note, setNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchNote = async () => {
      try {
        const response = await api.get(`/notes/${id}`);
        setNote(response.data);
        setLoading(false);
      } catch (err) {
        setError("Failed to fetch note");
        setLoading(false);
      }
    };

    fetchNote();
  }, [id]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!note) return <div>Note not found</div>;

  return (
    <div>
      <h2>{note.title}</h2>
      <p>{note.content}</p>
      <p>Author: {note.author_username}</p>
      <p>Created: {new Date(note.created_at).toLocaleString()}</p>
    </div>
  );
};

export default NoteDetail;