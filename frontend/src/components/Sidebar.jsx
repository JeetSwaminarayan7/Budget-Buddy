import { NavLink, useLocation } from "react-router-dom";

const navItems = [
  { icon: "⊞", label: "Dashboard",    to: "/"             },
  { icon: "↕", label: "Transactions", to: "/transactions" },
  { icon: "◎", label: "Budgets",      to: "/budgets"      },
  { icon: "⬆", label: "Upload",       to: "/upload"       },
];

export default function Sidebar() {
  const { pathname } = useLocation();

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-mark">B</div>
        <span className="logo-text">BudgetBuddy</span>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const isActive =
            item.to === "/" ? pathname === "/" : pathname.startsWith(item.to);
          return (
            <NavLink
              key={item.label}
              to={item.to}
              className={`nav-item ${isActive ? "nav-item-active" : ""}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
              {isActive && <span className="nav-indicator" />}
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="user-avatar">JS</div>
        <div className="user-info">
          <span className="user-name">Jeet Swaminarayan</span>
          <span className="user-plan">Pro Plan</span>
        </div>
      </div>
    </aside>
  );
}
