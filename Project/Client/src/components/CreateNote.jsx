import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import API from "../services/api";

const CreateNote = () => {
  const [form, setForm] = useState({ title: "", content: "" });
  const { user } = useAuth();
  const nav = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    try {
      const res = await API.post("/notes/", form);
      nav(`/note/${res.data.id}`);
    } catch (e) {
      alert("Create failed");
    }
  };

  return (
    <form onSubmit={submit} className="max-w-2xl mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Create Note</h2>
      <div className="mb-4">
        <input 
          placeholder="Title" 
          value={form.title} 
          onChange={e=>setForm({...form, title: e.target.value})}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div className="mb-4">
        <textarea 
          placeholder="Content" 
          value={form.content} 
          onChange={e=>setForm({...form, content: e.target.value})}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows="6"
        />
      </div>
      <button 
        type="submit" 
        className="w-full bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      >
        Create
      </button>
    </form>
  );
};

export default CreateNote;
