import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

// Auth & Layout Components
import LoginPage from './pages/auth/Login.jsx';
import SignupPage from './pages/auth/Signup.jsx';
import ProtectedRoute from './components/shared/ProtectedRoute.jsx';
import MainLayout from './components/layout/MainLayout.jsx';

// Page Components
import EmployeeDashboard from './pages/employee/Dashboard.jsx';
import SubmitExpensePage from './pages/employee/SubmitExpense.jsx';
import ExpenseHistoryPage from './pages/employee/ExpenseHistory.jsx';
import ManagerDashboard from './pages/manager/Dashboard.jsx';
import ManageUsersPage from './pages/admin/ManageUsers.jsx'; // <--- IMPORT THE PAGE

/**
 * A component that redirects the user to their default dashboard
 * based on their role after they log in.
 */
const HomeRedirect = () => {
  const { user } = useAuth();
  
  if (user?.role === 'admin') {
    return <Navigate to="/admin/dashboard" />;
  }
  if (user?.role === 'manager') {
    return <Navigate to="/manager/dashboard" />;
  }
  // Default role is employee
  return <Navigate to="/employee/dashboard" />;
};


function App() {
  // Placeholder for the Admin dashboard
  const AdminDashboard = () => <h1 className="text-3xl font-bold">Admin Dashboard</h1>;

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />

      {/* Root path redirects to the appropriate dashboard */}
      <Route path="/" element={<ProtectedRoute><HomeRedirect /></ProtectedRoute>} />

      {/* Employee Routes */}
      <Route path="/employee" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<EmployeeDashboard />} />
        <Route path="submit" element={<SubmitExpensePage />} />
        <Route path="history" element={<ExpenseHistoryPage />} />
      </Route>

      {/* Manager Routes */}
      <Route path="/manager" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<ManagerDashboard />} />
      </Route>
      
      {/* Admin Routes */}
      <Route path="/admin" element={<ProtectedRoute><MainLayout /></ProtectedRoute>}>
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="users" element={<ManageUsersPage />} /> {/* <--- USE THE PAGE */}
      </Route>
    </Routes>
  );
}

export default App;