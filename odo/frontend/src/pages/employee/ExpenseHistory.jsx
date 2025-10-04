import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';

const API_URL = "http://127.0.0.1:8000";

// This is the same reusable component from the Dashboard
const StatusBadge = ({ status }) => {
  const baseStyle = "px-2 py-1 text-xs font-semibold rounded-full";
  const styles = {
    Pending: "bg-yellow-100 text-yellow-800",
    Approved: "bg-green-100 text-green-800",
    Rejected: "bg-red-100 text-red-800",
  };
  return <span className={`${baseStyle} ${styles[status]}`}>{status}</span>;
};

export default function ExpenseHistoryPage() {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchExpenses = async () => {
      try {
        const response = await axios.get(`${API_URL}/expenses/my-expenses`);
        setExpenses(response.data);
      } catch (err) {
        setError("Failed to fetch expense history.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchExpenses();
  }, []);

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold">My Expense History</h1>

      <div className="p-6 rounded-lg shadow-md bg-card">
        <h2 className="mb-4 text-xl font-semibold">All Submissions</h2>
        {/* We could add filter controls here in the future */}
        
        {loading ? (
          <p>Loading your history...</p>
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
                {expenses.map((expense) => (
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