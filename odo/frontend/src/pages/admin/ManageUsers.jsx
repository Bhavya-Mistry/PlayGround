import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Users, PlusCircle } from 'lucide-react';

const API_URL = "http://127.0.0.1:8000";

// Modal component for creating/editing users
const UserModal = ({ isOpen, onClose, refreshUsers }) => {
  const [formData, setFormData] = useState({
    full_name: '', email: '', username: '', password: '', role: 'employee'
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await axios.post(`${API_URL}/users/`, formData);
      refreshUsers();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create user.');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-lg p-6 rounded-lg shadow-lg bg-card">
        <h2 className="mb-4 text-xl font-semibold">Add New User</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Form fields */}
          <input name="full_name" placeholder="Full Name" onChange={handleChange} required className="input-style" />
          <input name="email" type="email" placeholder="Email" onChange={handleChange} required className="input-style" />
          <input name="username" placeholder="Username" onChange={handleChange} required className="input-style" />
          <input name="password" type="password" placeholder="Password" onChange={handleChange} required className="input-style" />
          <select name="role" onChange={handleChange} value={formData.role} className="input-style">
            <option value="employee">Employee</option>
            <option value="manager">Manager</option>
            <option value="admin">Admin</option>
          </select>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <div className="flex justify-end space-x-4">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-md hover:bg-accent">Cancel</button>
            <button type="submit" className="px-4 py-2 text-white rounded-md bg-primary hover:bg-primary/90">Create User</button>
          </div>
        </form>
      </div>
      <style jsx>{`
        .input-style { display: block; width: 100%; background-color: var(--background); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.5rem 0.75rem; }
      `}</style>
    </div>
  );
};


export default function ManageUsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_URL}/users/`);
      setUsers(response.data);
    } catch (err) {
      setError("Failed to fetch users.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div>
      <UserModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} refreshUsers={fetchUsers} />
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">User Management</h1>
          <p className="text-muted-foreground">Create, view, and manage all users in your organization.</p>
        </div>
        <button onClick={() => setIsModalOpen(true)} className="flex items-center px-4 py-2 font-semibold text-white rounded-md bg-primary hover:bg-primary/90">
          <PlusCircle className="w-5 h-5 mr-2" />
          Add New User
        </button>
      </div>

      <div className="p-6 rounded-lg shadow-md bg-card">
        {loading ? <p>Loading users...</p> : 
         error ? <p className="text-destructive">{error}</p> : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="border-b border-border">
                <tr>
                  <th className="p-3">Full Name</th>
                  <th className="p-3">Username</th>
                  <th className="p-3">Role</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user._id} className="border-b border-border hover:bg-secondary">
                    <td className="p-3">
                      <div className="font-medium">{user.full_name}</div>
                      <div className="text-xs text-muted-foreground">{user.email}</div>
                    </td>
                    <td className="p-3">{user.username}</td>
                    <td className="p-3 capitalize">{user.role}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 text-xs rounded-full ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="p-3">
                      <button className="text-xs font-semibold text-primary hover:underline">Edit</button>
                      {/* Add deactivate/delete functionality here */}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}