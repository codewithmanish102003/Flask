import React from "react";
import { Link, Route, Routes } from "react-router-dom";
import CreateNote from "./components/CreateNote";
import Login from "./components/Login";
import NoteDetail from "./components/NoteDetail";
import NoteList from "./components/NoteList";
import ProtectedRoute from "./components/ProtectedRoute";
import Register from "./components/Register";
import { AuthContext } from "./context/AuthContext";

function App() {
  const { user, logout } = React.useContext(AuthContext);

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8 pb-4 border-b border-gray-200">
        <h1 className="text-3xl font-bold text-blue-600 mb-4">Social Notes</h1>
        <nav className="flex space-x-4">
          <Link to="/" className="text-blue-500 hover:text-blue-700">Notes</Link>
          {user ? (
            <>
              <Link to="/create" className="text-blue-500 hover:text-blue-700">Create</Link>
              <span className="text-gray-600">Welcome, {user.username}</span>
              <button onClick={logout} className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-blue-500 hover:text-blue-700">Login</Link>
              <Link to="/register" className="text-blue-500 hover:text-blue-700">Register</Link>
            </>
          )}
        </nav>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<NoteList />} />
          <Route path="/note/:id" element={<NoteDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/create" element={<ProtectedRoute><CreateNote /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
