import { useEffect, useMemo, useState } from "react";
import api from "../services/api";

export default function RiskAnalysis({
  setSelectedSource,
}) {
  const [emails, setEmails] = useState([]);
  const [count, setCount] = useState(0);

  const [search, setSearch] = useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  /* =====================================================
     LOAD RISK DATA
     ===================================================== */

  useEffect(() => {
    async function loadRiskData() {
      try {
        setLoading(true);
        setError("");

        const response =
          await api.get(
            "/insights/high-risk"
          );

        const data = response.data || {};

        setEmails(
          Array.isArray(data.emails)
            ? data.emails
            : []
        );

        setCount(
          Number(data.count || 0)
        );
      } catch (err) {
        console.error(
          "[RISK] Failed to load:",
          err
        );

        setError(
          "Risk intelligence is currently unavailable."
        );
      } finally {
        setLoading(false);
      }
    }

    loadRiskData();
  }, []);

  /* =====================================================
     FILTER
     ===================================================== */

  const filteredEmails = useMemo(() => {
    const query =
      search.trim().toLowerCase();

    if (!query) {
      return emails;
    }

    return emails.filter((email) => {
      const searchableText = [
        email.subject,
        email.from,
        email.message_id,
        email.matched_keyword,
        email.date,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return searchableText.includes(
        query
      );
    });
  }, [emails, search]);

  /* =====================================================
     DATE FORMAT
     ===================================================== */

  const formatDate = (date) => {
    if (!date) {
      return "Unknown date";
    }

    try {
      const parsed =
        new Date(date);

      if (
        Number.isNaN(
          parsed.getTime()
        )
      ) {
        return date;
      }

      return parsed.toLocaleDateString(
        "en-IN",
        {
          day: "2-digit",
          month: "short",
          year: "numeric",
        }
      );
    } catch {
      return date;
    }
  };

  /* =====================================================
     RISK LEVEL
     ===================================================== */

  const getRiskLevel = (keyword) => {
    const highRisk = [
      "fraud",
      "subpoena",
      "investigation",
      "sec",
      "lawsuit",
    ];

    if (
      highRisk.includes(
        String(keyword)
          .toLowerCase()
      )
    ) {
      return "HIGH";
    }

    return "ELEVATED";
  };

  /* =====================================================
     OPEN SOURCE
     ===================================================== */

  const openSource = async (email) => {
    if (!setSelectedSource) {
      return;
    }

    try {
      /*
       * The high-risk endpoint intentionally
       * returns a lightweight email object.
       *
       * Fetch the complete email before opening
       * the SourcePanel.
       */

      if (email.message_id) {
        const response =
          await api.get(
            `/emails/message/${encodeURIComponent(
              email.message_id
            )}`
          );

        if (response.data) {
          setSelectedSource(
            response.data
          );

          return;
        }
      }
    } catch (err) {
      console.error(
        "[RISK] Failed to load source:",
        err
      );
    }

    /*
     * Fallback to the data we already have.
     */

    setSelectedSource(email);
  };

  return (
    <section className="analytics-page risk-page">

      {/* =================================================
          HEADER
          ================================================= */}

      <div className="analytics-header">

        <div>

          <span className="analytics-eyebrow risk-eyebrow">
            RISK INTELLIGENCE
          </span>

          <h1>
            Risk Analysis
          </h1>

          <p>
            Identify emails containing legal,
            compliance, investigation and other
            potentially high-risk indicators.
          </p>

        </div>

        <div className="risk-live-status">
          <span className="risk-status-dot"></span>

          Monitoring Dataset
        </div>

      </div>

      {/* =================================================
          STAT CARDS
          ================================================= */}

      <div className="analytics-stats">

        <div className="analytics-stat-card risk-stat">

          <span className="analytics-stat-label">
            FLAGGED EMAILS
          </span>

          <strong>
            {loading
              ? "—"
              : count.toLocaleString()}
          </strong>

          <small>
            Potentially relevant messages
          </small>

        </div>

        <div className="analytics-stat-card">

          <span className="analytics-stat-label">
            KEYWORD RULES
          </span>

          <strong>
            8
          </strong>

          <small>
            Risk indicators monitored
          </small>

        </div>

        <div className="analytics-stat-card">

          <span className="analytics-stat-label">
            CURRENT STATUS
          </span>

          <strong className="risk-active">
            ACTIVE
          </strong>

          <small>
            Rule-based risk detection
          </small>

        </div>

      </div>

      {/* =================================================
          TOOLBAR
          ================================================= */}

      <div className="analytics-toolbar">

        <div>

          <h2>
            Flagged Communications
          </h2>

          <p>
            Review messages matching known
            risk indicators.
          </p>

        </div>

        <div className="entity-search">

          <span>
            ⌕
          </span>

          <input
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
            placeholder="Search flagged emails..."
          />

        </div>

      </div>

      {/* =================================================
          RISK TABLE
          ================================================= */}

      <div className="risk-panel">

        {/* TABLE HEADER */}

        <div className="risk-table-header">

          <span>
            MESSAGE
          </span>

          <span>
            SENDER
          </span>

          <span>
            INDICATOR
          </span>

          <span>
            DATE
          </span>

          <span>
            LEVEL
          </span>

        </div>

        {/* LOADING */}

        {loading && (
          <div className="analytics-empty">

            <div className="analytics-loader">

              <span></span>
              <span></span>
              <span></span>

            </div>

            <h3>
              Scanning risk indicators
            </h3>

            <p>
              Loading flagged communications
              from the email intelligence system.
            </p>

          </div>
        )}

        {/* ERROR */}

        {!loading &&
          error && (
            <div className="analytics-empty">

              <div className="analytics-empty-icon risk-error-icon">
                !
              </div>

              <h3>
                Risk data unavailable
              </h3>

              <p>
                {error}
              </p>

            </div>
          )}

        {/* EMPTY */}

        {!loading &&
          !error &&
          filteredEmails.length ===
            0 && (
            <div className="analytics-empty">

              <div className="analytics-empty-icon">
                ✓
              </div>

              <h3>
                No flagged emails found
              </h3>

              <p>
                No messages match the current
                search criteria.
              </p>

            </div>
          )}

        {/* EMAIL ROWS */}

        {!loading &&
          !error &&
          filteredEmails.length >
            0 && (
            <div className="risk-email-list">

              {filteredEmails.map(
                (
                  email,
                  index
                ) => {

                  const level =
                    getRiskLevel(
                      email.matched_keyword
                    );

                  return (
                    <button
                      type="button"
                      className="risk-row"
                      key={
                        email.message_id ||
                        `${email.subject}-${index}`
                      }
                      onClick={() =>
                        openSource(
                          email
                        )
                      }
                    >

                      {/* MESSAGE */}

                      <div className="risk-message">

                        <div className="risk-message-icon">
                          !
                        </div>

                        <div className="risk-message-content">

                          <strong>
                            {email.subject ||
                              "No Subject"}
                          </strong>

                          <span>
                            {email.message_id ||
                              "Message ID unavailable"}
                          </span>

                        </div>

                      </div>

                      {/* SENDER */}

                      <div className="risk-sender">

                        {email.from ||
                          "Unknown sender"}

                      </div>

                      {/* KEYWORD */}

                      <div className="risk-keyword">

                        <span>
                          {email.matched_keyword ||
                            "Unknown"}
                        </span>

                      </div>

                      {/* DATE */}

                      <div className="risk-date">

                        {formatDate(
                          email.date
                        )}

                      </div>

                      {/* LEVEL */}

                      <div>

                        <span
                          className={
                            level ===
                            "HIGH"
                              ? "risk-level high"
                              : "risk-level elevated"
                          }
                        >
                          {level}
                        </span>

                      </div>

                    </button>
                  );
                }
              )}

            </div>
          )}

      </div>

      {/* =================================================
          FOOTNOTE
          ================================================= */}

      {!loading &&
        !error &&
        emails.length > 0 && (
          <div className="risk-footnote">

            <span>
              ⚠
            </span>

            Risk detection is currently
            keyword-based. A flagged email does
            not necessarily indicate misconduct.

          </div>
        )}

    </section>
  );
}