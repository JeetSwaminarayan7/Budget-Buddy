import { useEffect, useRef, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navLinks = [
  { to: "/",             label: "Dashboard",    end: true },
  { to: "/upload",       label: "Upload",       end: false },
  { to: "/budgets",      label: "Budget",       end: false },
  { to: "/transactions", label: "Transactions", end: false },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate         = useNavigate();
  const [open, setOpen]  = useState(false);
  const wrapRef          = useRef(null);

  // Close on click outside
  useEffect(() => {
    function handleClick(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  async function handleLogout() {
    setOpen(false);
    await logout();
    navigate("/login");
  }

  const initials = user?.username
    ? user.username.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase()
    : "??";

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-brand">
          <div className="navbar-logo-mark">B</div>
          <div>
            <div className="navbar-logo-text">Budget Buddy</div>
            <div className="navbar-logo-sub">Smart finance for students</div>
          </div>
        </div>

        <div className="navbar-links">
          {navLinks.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `navbar-link${isActive ? " navbar-link-active" : ""}`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>

        <div className="navbar-actions">
          <div className="navbar-avatar-wrap" ref={wrapRef}>
            <div className="navbar-avatar" onClick={() => setOpen((v) => !v)}>
              {initials}
            </div>
            <div className={`navbar-dropdown${open ? " navbar-dropdown-open" : ""}`}>
              <div className="navbar-dropdown-name">{user?.username}</div>
              <div className="navbar-dropdown-email">{user?.email}</div>
              <div className="navbar-dropdown-divider" />
              <button className="navbar-dropdown-logout" onClick={handleLogout}>
                Sign out
              </button>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
