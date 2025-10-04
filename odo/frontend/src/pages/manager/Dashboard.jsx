import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { useAuth } from '../../context/AuthContext';

const API_URL = "http://127.0.0.1:8000";

// A simple modal component for confirming decisions
const DecisionModal = ({ expense, onConfirm, onCancel, setComment, comment }) => (
  <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div className="w-full max-w-md p-6 rounded-lg shadow-lg bg-card">
      <h2 className="text-xl font-semibold">Confirm Decision</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        You are about to action an expense for <strong>{new Intl.NumberFormat('en-US', { style: 'currency', currency: expense.currency }).format(expense.amount)}</strong>.
      </p>
      <div className="mt-4">
        <label htmlFor="comment" className="block text-sm font-medium">Optional Comment</label>
        <textarea
          id="comment"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          rows="3"
          className="w-full p-2 mt-1 border rounded-md bg-background border-border"
        />
      </div>
      <div className="flex justify-end mt-6 space-x-4">
        <button onClick={onCancel} className="px-4 py-2 text-sm font-medium rounded-md hover:bg-accent">Cancel</button>
        <button onClick={() => onConfirm('Rejected')} className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700">Reject</button>
        <button onClick={() => onConfirm('Approved')} className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700">Approve</button>
      </div>
    </div>
  </div>
);

export default function ManagerDashboard() {
  const { user } = useAuth();
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedExpense, setSelectedExpense] = useState(null);
  const [comment, setComment] = useState('');

  const fetchApprovalQueue = async () => {
    try {
      const response = await axios.get(`${API_URL}/expenses/approvals`);
      setQueue(response.data);
    } catch (err) {
      setError("Failed to fetch approval queue.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovalQueue();
  }, []);

  const handleDecision = async (status) => {
    if (!selectedExpense) return;
    
    try {
      await axios.post(`${API_URL}/expenses/${selectedExpense._id}/decision`, {
        status,
        comment,
      });
      // Refresh queue by removing the actioned item for instant feedback
      setQueue(prev => prev.filter(exp => exp._id !== selectedExpense._id));
    } catch (err) {
      setError("Failed to process decision. Please try again.");
    } finally {
      setSelectedExpense(null);
      setComment('');
    }
  };

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold">Approval Queue</h1>
      <p className="mb-8 text-muted-foreground">Welcome, {user?.username}. Review and action the expenses waiting for your approval.</p>

      <div className="p-6 rounded-lg shadow-md bg-card">
        {loading ? <p>Loading approval queue...</p> : 
         error ? <p className="text-destructive">{error}</p> :
         queue.length === 0 ? <p className="text-center text-muted-foreground">Your approval queue is empty. Great job!</p> : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="border-b border-border">
                <tr>
                  <th className="p-3">Submission Date</th>
                  <th className="p-3">Employee ID</th>
                  <th className="p-3">Description</th>
                  <th className="p-3 text-right">Amount</th>
                  <th className="p-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {queue.map((expense) => (
                  <tr key={expense._id} className="border-b border-border hover:bg-secondary">
                    <td className="p-3">{format(new Date(expense.created_at), 'MMM dd, yyyy')}</td>
                    <td className="p-3 font-mono text-xs">{expense.employee_id}</td>
                    <td className="p-3">{expense.description || '-'}</td>
                    <td className="p-3 font-medium text-right">{new Intl.NumberFormat('en-US', { style: 'currency', currency: expense.currency }).format(expense.amount)}</td>
                    <td className="p-3 text-center">
                      <button onClick={() => setSelectedExpense(expense)} className="px-3 py-1 font-semibold text-white rounded-md bg-primary hover:bg-primary/90">
                        Review
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedExpense && (
        <DecisionModal 
          expense={selectedExpense} 
          comment={comment}
          setComment={setComment}
          onCancel={() => {
            setSelectedExpense(null);
            setComment('');
          }}
          onConfirm={handleDecision}
        />
      )}
    </div>
  );
}