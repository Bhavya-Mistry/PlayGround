import React, { useState, useEffect } from 'react';
import { Outlet, NavLink, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LayoutDashboard, PlusCircle, History, LogOut, CircleUserRound, Users, ShieldCheck } from 'lucide-react';

// Reusable NavLink component for styling
const SidebarLink = ({ to, icon: Icon, children }) => (
  <NavLink
    to={to}
    end={to === '/'} // Use 'end' for the root dashboard link
    className={({ isActive }) =>
      `flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
        isActive
          ? 'bg-primary text-primary-foreground'
          : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
      }`
    }
  >
    <Icon className="w-5 h-5 mr-3" />
    {children}
  </NavLink>
);

// --- Link configurations for different roles ---
const employeeLinks = [
  { to: '/employee/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/employee/submit', icon: PlusCircle, label: 'Submit Expense' },
  { to: '/employee/history', icon: History, label: 'My History' },
];

const managerLinks = [
  { to: '/manager/dashboard', icon: ShieldCheck, label: 'Approval Queue' },
  ...employeeLinks, // Managers can also perform employee actions
];

const adminLinks = [
  { to: '/admin/dashboard', icon: LayoutDashboard, label: 'Admin Dashboard' },
  { to: '/admin/users', icon: Users, label: 'Manage Users'},
  ...managerLinks, // Admins can do everything
];


export default function MainLayout() {
  const { user, logout } = useAuth();
  const [navLinks, setNavLinks] = useState([]);

  useEffect(() => {
    // Set the navigation links based on the user's role
    switch (user?.role) {
      case 'admin':
        setNavLinks(adminLinks);
        break;
      case 'manager':
        setNavLinks(managerLinks);
        break;
      case 'employee':
        setNavLinks(employeeLinks);
        break;
      default:
        setNavLinks([]);
    }
  }, [user]);

  return (
    <div className="flex h-screen bg-secondary">
      {/* Sidebar */}
      <aside className="flex flex-col w-64 p-4 bg-card text-card-foreground border-r border-border">
        <div className="mb-8 text-center">
          <Link to="/" className="text-2xl font-bold text-foreground">
            ExpenSys
          </Link>
        </div>
        
        <nav className="flex-grow space-y-2">
          {navLinks.map((link) => (
            <SidebarLink key={link.to} to={link.to} icon={link.icon}>
              {link.label}
            </SidebarLink>
          ))}
        </nav>

        {/* User Info & Logout */}
        <div className="pt-4 mt-auto border-t border-border">
          <div className="flex items-center p-2 mb-4 rounded-md bg-secondary">
             <CircleUserRound className="w-8 h-8 mr-3 text-muted-foreground"/>
            <div>
              <p className="text-sm font-semibold text-foreground">{user?.username}</p>
              <p className="text-xs capitalize text-muted-foreground">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="flex items-center w-full px-4 py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-destructive hover:text-destructive-foreground"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}