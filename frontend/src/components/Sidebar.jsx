export default function Sidebar({
  activeView = "chat",
  setActiveView,
}) {
  const navigate = (view) => {
    if (typeof setActiveView === "function") {
      setActiveView(view);
    }
  };

  const recentSearch = (text) => {
    navigate("chat");

    window.dispatchEvent(
      new CustomEvent("email-intelligence-search", {
        detail: text,
      })
    );
  };

  const isActive = (view) =>
    activeView === view;

  return (
    <aside className="sidebar">

      {/* PROFILE */}
      <div className="sidebar-profile">

        <div className="profile-avatar">
          <span className="mail-icon">
            ✉
          </span>
        </div>

        <div className="profile-info">
          <h2>
            EMAIL
            <br />
            INTELLIGENCE
          </h2>

          <p>
            YASH PARAB PRODUCT
          </p>
        </div>

      </div>


      {/* NEW ANALYSIS */}
      <button
        type="button"
        className="compose-button"
        onClick={() => navigate("chat")}
      >
        <span className="button-icon">
          +
        </span>

        NEW ANALYSIS
      </button>


      {/* WORKSPACE */}
      <div className="sidebar-section">

        <h3>
          WORKSPACE
        </h3>

        <ul className="sidebar-menu">

          <li
            className={`sidebar-item ${
              isActive("chat")
                ? "sidebar-active"
                : ""
            }`}
            onClick={() => navigate("chat")}
          >
            <span className="sidebar-icon icon-search">
              🔎
            </span>

            <span className="sidebar-label">
              AI EMAIL SEARCH
            </span>
          </li>


          <li
            className={`sidebar-item ${
              isActive("dashboard")
                ? "sidebar-active"
                : ""
            }`}
            onClick={() =>
              navigate("dashboard")
            }
          >
            <span className="sidebar-icon icon-dashboard">
              ▦
            </span>

            <span className="sidebar-label">
              DASHBOARD
            </span>
          </li>

        </ul>

      </div>


      {/* INTELLIGENCE MODULES */}
      <div className="sidebar-section">

        <h3>
          INTELLIGENCE MODULES
        </h3>

        <ul className="sidebar-menu">

          {/* ENTITY EXTRACTION */}
          <li
            className={`sidebar-item ${
              isActive("entities")
                ? "sidebar-active"
                : ""
            }`}
            onClick={() =>
              navigate("entities")
            }
          >
            <span className="sidebar-icon icon-entity">
              ◆
            </span>

            <span className="sidebar-label">
              ENTITY EXTRACTION
            </span>
          </li>


          {/* TIMELINE ANALYSIS */}
          <li
            className={`sidebar-item ${
              isActive("timeline")
                ? "sidebar-active"
                : ""
            }`}
            onClick={() =>
              navigate("timeline")
            }
          >
            <span className="sidebar-icon icon-timeline">
              ◷
            </span>

            <span className="sidebar-label">
              TIMELINE ANALYSIS
            </span>
          </li>


          {/* RISK DETECTION */}
          <li
            className={`sidebar-item ${
              isActive("risk")
                ? "sidebar-active"
                : ""
            }`}
            onClick={() =>
              navigate("risk")
            }
          >
            <span className="sidebar-icon icon-risk">
              !
            </span>

            <span className="sidebar-label">
              RISK DETECTION
            </span>
          </li>


          {/* COMMUNICATION HUBS */}
          <li
            className={`sidebar-item ${
              isActive("hubs")
                ? "sidebar-active"
                : ""
            }`}
            onClick={() =>
              navigate("hubs")
            }
          >
            <span className="sidebar-icon icon-hubs">
              ◎
            </span>

            <span className="sidebar-label">
              COMMUNICATION HUBS
            </span>
          </li>


          {/* INGESTION PROGRESS */}
          <li
            className={`sidebar-item ${
              isActive("ingestion")
                ? "sidebar-active"
                : ""
            }`}
            onClick={() =>
              navigate("ingestion")
            }
          >
            <span className="sidebar-icon icon-ingestion">
              ⇩
            </span>

            <span className="sidebar-label">
              INGESTION PROGRESS
            </span>
          </li>

        </ul>

      </div>


      {/* RECENT SEARCHES */}
      <div className="sidebar-section recent-section">

        <h3>
          RECENT SEARCHES
        </h3>

        <ul className="sidebar-menu">

          {/* KENNETH LAY */}
          <li
            className="sidebar-item recent-item"
            onClick={() =>
              recentSearch(
                "Kenneth Lay communications"
              )
            }
          >
            <span className="sidebar-icon recent-icon">
              ▸
            </span>

            <span className="sidebar-label">
              KENNETH LAY
            </span>
          </li>


          {/* TRADING ACTIVITY */}
          <li
            className="sidebar-item recent-item"
            onClick={() =>
              recentSearch(
                "Trading Activity"
              )
            }
          >
            <span className="sidebar-icon recent-icon">
              ▸
            </span>

            <span className="sidebar-label">
              TRADING ACTIVITY
            </span>
          </li>


          {/* LEGAL RISK */}
          <li
            className="sidebar-item recent-item"
            onClick={() =>
              recentSearch(
                "Legal Risk"
              )
            }
          >
            <span className="sidebar-icon recent-icon">
              ▸
            </span>

            <span className="sidebar-label">
              LEGAL RISK
            </span>
          </li>


          {/* COMMUNICATION NETWORK */}
          <li
            className="sidebar-item recent-item"
            onClick={() =>
              recentSearch(
                "Communication Network"
              )
            }
          >
            <span className="sidebar-icon recent-icon">
              ▸
            </span>

            <span className="sidebar-label">
              COMMUNICATION NETWORK
            </span>
          </li>

        </ul>

      </div>


      {/* FOOTER */}
      <div className="sidebar-footer">

        <span className="footer-status-dot"></span>

        SYSTEM ONLINE

      </div>

    </aside>
  );
}