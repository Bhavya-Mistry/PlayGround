import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_URL = "http://127.0.0.1:8000";

export default function SignupPage() {
  const [formData, setFormData] = useState({
    company_name: '',
    company_currency: '',
    full_name: '',
    email: '',
    username: '',
    password: '',
  });
  const [currencies, setCurrencies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch currencies when the component mounts
    const fetchCurrencies = async () => {
      try {
        const response = await axios.get('https://restcountries.com/v3.1/all?fields=currencies');
        const currencySet = new Set();
        response.data.forEach(country => {
          if (country.currencies) {
            Object.keys(country.currencies).forEach(code => currencySet.add(code));
          }
        });
        setCurrencies(Array.from(currencySet).sort());
      } catch (err) {
        console.error("Failed to fetch currencies", err);
        // Fallback in case API fails
        setCurrencies(['USD', 'EUR', 'GBP', 'INR']);
      }
    };
    fetchCurrencies();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await axios.post(`${API_URL}/auth/signup`, formData);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000); // Redirect to login after 2 seconds
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to sign up. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen py-12 bg-secondary">
      <div className="w-full max-w-lg p-8 space-y-6 rounded-lg shadow-lg bg-card text-card-foreground">
        <div className="text-center">
          <h1 className="text-3xl font-bold">Create an Account</h1>
          <p className="text-muted-foreground">Get started with your new expense management system</p>
        </div>
        
        {success ? (
          <div className="p-4 text-center rounded-md bg-accent text-accent-foreground">
            <h3 className="font-semibold">Registration Successful!</h3>
            <p>Redirecting you to the login page...</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {/* Company Info */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium">Company Name</label>
              <input type="text" name="company_name" onChange={handleChange} required className="w-full input-style" />
            </div>
            <div>
              <label className="block text-sm font-medium">Default Currency</label>
              <select name="company_currency" onChange={handleChange} required className="w-full input-style">
                <option value="">Select Currency</option>
                {currencies.map(code => <option key={code} value={code}>{code}</option>)}
              </select>
            </div>
            
            {/* Admin Info */}
            <div>
              <label className="block text-sm font-medium">Full Name</label>
              <input type="text" name="full_name" onChange={handleChange} required className="w-full input-style" />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium">Email Address</label>
              <input type="email" name="email" onChange={handleChange} required className="w-full input-style" />
            </div>
            <div>
              <label className="block text-sm font-medium">Username</label>
              <input type="text" name="username" onChange={handleChange} required className="w-full input-style" />
            </div>
            <div>
              <label className="block text-sm font-medium">Password</label>
              <input type="password" name="password" onChange={handleChange} required className="w-full input-style" />
            </div>

            {error && (
              <div className="p-3 text-sm text-center rounded-md md:col-span-2 bg-destructive text-destructive-foreground">
                {error}
              </div>
            )}

            <div className="md:col-span-2">
              <button type="submit" disabled={loading} className="w-full py-2 font-semibold text-white rounded-md bg-primary hover:bg-primary/90 disabled:opacity-50">
                {loading ? 'Registering...' : 'Create Account'}
              </button>
            </div>
          </form>
        )}

        <p className="text-sm text-center text-muted-foreground">
          Already have an account?{' '}
          <Link to="/login" className="font-medium hover:underline text-primary">
            Sign in
          </Link>
        </p>
      </div>
      <style jsx>{`
        .input-style {
          background-color: var(--background);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 0.5rem 0.75rem;
          margin-top: 0.25rem;
        }
        .input-style:focus {
          outline: 2px solid transparent;
          outline-offset: 2px;
          border-color: var(--ring);
        }
      `}</style>
    </div>
  );
}