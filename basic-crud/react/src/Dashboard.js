import React, { useEffect, useState } from "react";

const API_URL = "http://localhost:5000";

function Dashboard({ user, onLogout }) {
  const [models, setModels] = useState([]);
  const [modelName, setModelName] = useState("");
  const [modelVersion, setModelVersion] = useState("");

  useEffect(() => {
    if (user) fetchModels();
    // eslint-disable-next-line
  }, [user]);

  const fetchModels = async () => {
    const res = await fetch(`${API_URL}/models`, {
      headers: { 'Authorization': user.api_key }
    });
    if (res.ok) {
      const data = await res.json();
      setModels(data);
    }
  };

  const handleAddModel = async (e) => {
    e.preventDefault();
    if (!user) return;
    const res = await fetch(`${API_URL}/models`, {
      method: "POST",
      headers: { "Content-Type": "application/json", 'Authorization': user.api_key },
      body: JSON.stringify({ name: modelName, version: modelVersion })
    });
    if (res.ok) {
      fetchModels();
      setModelName("");
      setModelVersion("");
    }
  };

  const handleDeleteModel = async (id) => {
    if (!user) return;
    await fetch(`${API_URL}/models/${id}`, {
      method: "DELETE",
      headers: { 'Authorization': user.api_key }
    });
    fetchModels();
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Dashboard</h2>
      <div className="mb-2">Welcome, <span className="font-semibold">{user.email}</span></div>
      <button onClick={onLogout} className="bg-red-500 text-white py-2 px-4 rounded mb-4">Logout</button>
      <form onSubmit={handleAddModel} className="flex space-x-2 mb-4">
        <input type="text" placeholder="Model Name" value={modelName} onChange={e => setModelName(e.target.value)} className="px-2 py-1 border rounded" required />
        <input type="text" placeholder="Version" value={modelVersion} onChange={e => setModelVersion(e.target.value)} className="px-2 py-1 border rounded" required />
        <button className="bg-green-500 text-white px-3 rounded">Add</button>
      </form>
      <ul className="space-y-2">
        {models.map(m => (
          <li key={m.id} className="flex justify-between items-center p-2 border rounded">
            <span>{m.name} ({m.version})</span>
            <button onClick={() => handleDeleteModel(m.id)} className="text-red-600">Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Dashboard;
