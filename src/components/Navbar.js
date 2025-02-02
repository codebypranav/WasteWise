import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>WasteWise AI</h1>
      </div>
      <div className="nav-links">
        <Link to="/" className={location.pathname === '/' ? 'active' : ''}>
          Dashboard
        </Link>
        <Link to="/analytics" className={location.pathname === '/analytics' ? 'active' : ''}>
          Analytics
        </Link>
        <Link to="/alerts" className={location.pathname === '/alerts' ? 'active' : ''}>
          Alerts
        </Link>
        <Link to="/settings" className={location.pathname === '/settings' ? 'active' : ''}>
          Settings
        </Link>
      </div>
    </nav>
  );
};

export default Navbar; 