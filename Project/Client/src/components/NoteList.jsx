import { useEffect, useState } from "react";
import API from "../services/api";
import NoteCard from "./NoteCard";

const NoteList = () => {
  const [notes, setNotes] = useState([]);

  const fetchNotes = async () => {
    const res = await API.get("/notes/");
    setNotes(res.data);
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  return (
    <div>
      <h2>Notes</h2>
      {notes.map(n => <NoteCard key={n.id} note={n} onUpdated={fetchNotes} />)}
    </div>
  );
};

export default NoteList;
