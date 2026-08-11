import { useLocation, useNavigate } from "react-router-dom";

interface RouteConfig {
  title: string;
  showUpload: boolean;
}

const routeConfig: Record<string, RouteConfig> = {
  "/":             { title: "Dashboard",        showUpload: true  },
  "/upload":       { title: "Upload Statement", showUpload: false },
  "/transactions": { title: "Transactions",     showUpload: false },
  "/budgets":      { title: "Budgets",          showUpload: false },
};

export default function Header() {
  const { pathname } = useLocation();
  const navigate = useNavigate();

  const config = routeConfig[pathname] ?? { title: "Budget Buddy", showUpload: false };

  const now = new Date();
  const dateStr = now.toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <header className="header">
      <div className="header-left">
        <h1 className="page-title">{config.title}</h1>
        <p className="page-subtitle">{dateStr}</p>
      </div>
      <div className="header-right">
        {config.showUpload && (
          <button className="upload-btn" onClick={() => navigate("/upload")}>
            <span>↑</span> Upload Statement
          </button>
        )}
      </div>
    </header>
  );
}
