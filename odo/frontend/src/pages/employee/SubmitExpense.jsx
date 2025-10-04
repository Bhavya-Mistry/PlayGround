import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = "http://127.0.0.1:8000";

// These categories should match the Enum on the backend
const expenseCategories = ["Travel", "Food", "Office Supplies", "Other"];

export default function SubmitExpensePage() {
  const [formData, setFormData] = useState({
    amount: '',
    currency: 'USD', // Default currency, can be improved later
    category: expenseCategories[0],
    description: '',
    expense_date: '',
  });
  const [receiptFile, setReceiptFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setReceiptFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    const data = new FormData();
    // Append form fields. The names must match the Pydantic model in FastAPI `Depends()`.
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    
    if (receiptFile) {
      data.append('receipt', receiptFile);
    }

    try {
      await axios.post(`${API_URL}/expenses/`, data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setSuccess(true);
      setTimeout(() => navigate('/'), 2000); // Redirect to dashboard after 2s
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit expense.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="mb-8 text-3xl font-bold">Submit New Expense</h1>
      <div className="max-w-2xl p-8 mx-auto rounded-lg shadow-md bg-card">
        {success ? (
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-green-600">Expense Submitted!</h2>
            <p className="mt-2 text-muted-foreground">Your expense claim has been successfully submitted for approval.</p>
            <p className="mt-4">Redirecting you to the dashboard...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div>
                <label htmlFor="expense_date" className="label-style">Expense Date</label>
                <input type="date" id="expense_date" name="expense_date" value={formData.expense_date} onChange={handleChange} required className="input-style" />
              </div>
              <div>
                <label htmlFor="category" className="label-style">Category</label>
                <select id="category" name="category" value={formData.category} onChange={handleChange} required className="input-style">
                  {expenseCategories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="amount" className="label-style">Amount</label>
                <input type="number" id="amount" name="amount" value={formData.amount} onChange={handleChange} required step="0.01" placeholder="99.99" className="input-style" />
              </div>
              <div>
                <label htmlFor="currency" className="label-style">Currency</label>
                <input type="text" id="currency" name="currency" value={formData.currency} onChange={handleChange} required maxLength="3" placeholder="USD" className="input-style" />
              </div>
            </div>
            <div>
              <label htmlFor="description" className="label-style">Description</label>
              <textarea id="description" name="description" value={formData.description} onChange={handleChange} rows="3" placeholder="e.g., Lunch meeting with a client" className="input-style"></textarea>
            </div>
            <div>
              <label htmlFor="receipt" className="label-style">Receipt</label>
              <input type="file" id="receipt" name="receipt" onChange={handleFileChange} className="block w-full mt-1 text-sm file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20 text-muted-foreground"/>
            </div>
            
            {error && <p className="p-3 text-sm text-center rounded-md bg-destructive text-destructive-foreground">{error}</p>}

            <button type="submit" disabled={loading} className="w-full py-2.5 font-semibold text-white rounded-md bg-primary hover:bg-primary/90 disabled:opacity-50">
              {loading ? 'Submitting...' : 'Submit for Approval'}
            </button>
          </form>
        )}
      </div>
      <style jsx>{`
        .label-style { display: block; font-size: 0.875rem; font-weight: 500; color: var(--foreground); }
        .input-style { display: block; width: 100%; margin-top: 0.25rem; background-color: var(--background); border: 1px solid var(--border); border-radius: var(--radius); padding: 0.5rem 0.75rem; }
        .input-style:focus { outline: 2px solid transparent; outline-offset: 2px; border-color: var(--ring); }
      `}</style>
    </div>
  );
}