import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';

const API_URL = "http://127.0.0.1:8000";

const StatusBadge = ({ status }) => {
  const baseStyle = "px-2 py-1 text-xs font-semibold rounded-full";
  const styles = {
    Pending: "bg-yellow-100 text-yellow-800",
    Approved: "bg-green-100 text-green-800",
    Rejected: "bg-red-100 text-red-800",
  };
  return <span className={`${baseStyle} ${styles[status]}`}>{status}</span>;
};

export default function EmployeeDashboard() {
  const { user } = useAuth();
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchExpenses = async () => {
      try {
        const response = await axios.get(`${API_URL}/expenses/my-expenses`);
        setExpenses(response.data);
      } catch (err) {
        setError("Failed to fetch expenses.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchExpenses();
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.username}!</h1>
          <p className="text-muted-foreground">Here is a summary of your recent expenses.</p>
        </div>
        <Link 
          to="/submit" 
          className="px-4 py-2 font-semibold text-white rounded-md bg-primary hover:bg-primary/90"
        >
          Submit New Expense
        </Link>
      </div>

      <div className="p-6 rounded-lg shadow-md bg-card">
        <h2 className="mb-4 text-xl font-semibold">Recent Submissions</h2>
        {loading ? (
          <p>Loading your expenses...</p>
        ) : error ? (
          <p className="text-destructive">{error}</p>
        ) : expenses.length === 0 ? (
          <p className="text-center text-muted-foreground">You haven't submitted any expenses yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="border-b border-border">
                <tr>
                  <th className="p-3">Date</th>
                  <th className="p-3">Description</th>
                  <th className="p-3">Category</th>
                  <th className="p-3 text-right">Amount</th>
                  <th className="p-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody>
                {expenses.slice(0, 5).map((expense) => ( // Show latest 5
                  <tr key={expense._id} className="border-b border-border hover:bg-secondary">
                    <td className="p-3">{format(new Date(expense.expense_date), 'MMM dd, yyyy')}</td>
                    <td className="p-3">{expense.description || '-'}</td>
                    <td className="p-3">{expense.category}</td>
                    <td className="p-3 font-medium text-right">
                      {new Intl.NumberFormat('en-US', { style: 'currency', currency: expense.currency }).format(expense.amount)}
                    </td>
                    <td className="p-3 text-center">
                      <StatusBadge status={expense.status} />
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