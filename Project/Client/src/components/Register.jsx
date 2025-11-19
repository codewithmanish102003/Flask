import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../services/api";

const Register = () => {
  const [form, setForm] = useState({ username: "", password: "" });
  const [msg, setMsg] = useState("");
  const nav = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    try {
      await API.post("/auth/register", form);
      setMsg("Registered. You can login now.");
      nav("/login");
    } catch (error) {
      setMsg(error.response?.data?.msg || "Register failed");
    }
  };

  return (
    <form onSubmit={submit} className="max-w-md mx-auto mt-8 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Register</h2>
      <div className="mb-4">
        <input 
          placeholder="Username" 
          value={form.username} 
          onChange={e => setForm({...form, username: e.target.value})}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <div className="mb-4">
        <input 
          placeholder="Password" 
          type="password" 
          value={form.password} 
          onChange={e => setForm({...form, password: e.target.value})}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
      <button 
        type="submit" 
        className="w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
      >
        Register
      </button>
      {msg && <p className="mt-4 text-center {msg.includes('Registered') ? 'text-green-500' : 'text-red-500'}">{msg}</p>}
    </form>
  );
};

export default Register;
