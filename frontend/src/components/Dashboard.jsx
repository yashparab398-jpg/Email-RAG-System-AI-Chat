import { useEffect, useState } from "react";
import api from "../services/api";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [topics, setTopics] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  /* =====================================================
     LOAD DASHBOARD DATA
     ===================================================== */

  useEffect(() => {
    let mounted = true;

    async function loadData() {
      try {
        setLoading(true);
        setError("");

        const [
          summaryResponse,
          topicsResponse,
        ] = await Promise.all([
          api.get("/insights/summary"),
          api.get("/insights/topics"),
        ]);

        if (!mounted) {
          return;
        }

        setSummary(
          summaryResponse.data || null
        );

        setTopics(
          topicsResponse.data || null
        );
      } catch (err) {
        console.error(
          "[DASHBOARD] Failed to load:",
          err
        );

        if (mounted) {
          setError(
            "Dashboard data is currently unavailable."
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadData();

    return () => {
      mounted = false;
    };
  }, []);

  /* =====================================================
     FORMAT NUMBER
     ===================================================== */

  const formatNumber = (value) => {
    const number = Number(value || 0);

    return number.toLocaleString("en-IN");
  };

  /* =====================================================
     LOADING
     ===================================================== */

  if (loading) {
    return (
      <section className="analytics-page dashboard-page">

        <div className="analytics-header">

          <div>
            <span className="analytics-eyebrow">
              DATASET INTELLIGENCE
            </span>

            <h1>
              Email Dashboard
            </h1>

            <p>
              Overview of the Enron email
              intelligence dataset.
            </p>
          </div>

          <div className="analytics-live-status">
            LOADING DATA
          </div>

        </div>

        <div className="dashboard-loading">

          <div className="pixel-loader">
            <span></span>
            <span></span>
            <span></span>
          </div>

          <h2>
            ANALYZING DATASET
          </h2>

          <p>
            Loading email intelligence statistics...
          </p>

        </div>

      </section>
    );
  }

  /* =====================================================
     ERROR
     ===================================================== */

  if (error || !summary || !topics) {
    return (
      <section className="analytics-page dashboard-page">

        <div className="analytics-header">

          <div>
            <span className="analytics-eyebrow">
              DATASET INTELLIGENCE
            </span>

            <h1>
              Email Dashboard
            </h1>

            <p>
              Overview of the Enron email
              intelligence dataset.
            </p>
          </div>

          <div className="analytics-live-status">
            OFFLINE
          </div>

        </div>

        <div className="dashboard-error">

          <div className="dashboard-error-icon">
            !
          </div>

          <h2>
            DATA UNAVAILABLE
          </h2>

          <p>
            {error ||
              "Dashboard information could not be loaded."}
          </p>

        </div>

      </section>
    );
  }

  const totalEmails =
    summary.total_emails || 0;

  const topSenders =
    Array.isArray(summary.top_senders)
      ? summary.top_senders
      : [];

  const topicEntries =
    topics &&
    typeof topics === "object"
      ? Object.entries(topics)
      : [];

  const topTopic =
    topicEntries.length > 0
      ? topicEntries.reduce(
          (highest, current) =>
            Number(current[1]) >
            Number(highest[1])
              ? current
              : highest
        )
      : null;

  /* =====================================================
     RENDER
     ===================================================== */

  return (
    <section className="analytics-page dashboard-page">

      {/* =================================================
          HEADER
          ================================================= */}

      <div className="analytics-header">

        <div>

          <span className="analytics-eyebrow">
            DATASET INTELLIGENCE
          </span>

          <h1>
            Email Dashboard
          </h1>

          <p>
            Overview of the Enron email
            intelligence dataset.
          </p>

        </div>

        <div className="analytics-live-status">
          <span className="dashboard-status-dot"></span>
          DATASET ONLINE
        </div>

      </div>


      {/* =================================================
          STATISTICS
          ================================================= */}

      <div className="dashboard-stat-grid">

        <div className="dashboard-stat-card">

          <span className="dashboard-stat-icon">
            ✉
          </span>

          <div>

            <span className="dashboard-stat-label">
              TOTAL EMAILS
            </span>

            <strong>
              {formatNumber(totalEmails)}
            </strong>

            <small>
              Messages indexed
            </small>

          </div>

        </div>


        <div className="dashboard-stat-card">

          <span className="dashboard-stat-icon">
            ◉
          </span>

          <div>

            <span className="dashboard-stat-label">
              TOP SENDERS
            </span>

            <strong>
              {formatNumber(
                topSenders.length
              )}
            </strong>

            <small>
              Leading communicators
            </small>

          </div>

        </div>


        <div className="dashboard-stat-card">

          <span className="dashboard-stat-icon">
            ◆
          </span>

          <div>

            <span className="dashboard-stat-label">
              TOPIC GROUPS
            </span>

            <strong>
              {formatNumber(
                topicEntries.length
              )}
            </strong>

            <small>
              Detected categories
            </small>

          </div>

        </div>


        <div className="dashboard-stat-card">

          <span className="dashboard-stat-icon">
            ★
          </span>

          <div>

            <span className="dashboard-stat-label">
              LEADING TOPIC
            </span>

            <strong className="dashboard-topic-value">
              {topTopic
                ? topTopic[0]
                : "—"}
            </strong>

            <small>
              Highest frequency topic
            </small>

          </div>

        </div>

      </div>


      {/* =================================================
          CONTENT GRID
          ================================================= */}

      <div className="dashboard-content-grid">


        {/* =================================================
            TOP SENDERS
            ================================================= */}

        <div className="dashboard-panel">

          <div className="dashboard-panel-header">

            <div>

              <span className="dashboard-panel-eyebrow">
                COMMUNICATION
              </span>

              <h2>
                TOP SENDERS
              </h2>

            </div>

            <span className="dashboard-panel-count">
              {topSenders.length}
            </span>

          </div>


          <div className="dashboard-list">

            {topSenders.length === 0 ? (

              <div className="dashboard-empty">
                No sender information available.
              </div>

            ) : (

              topSenders.map(
                ([sender, count], index) => (
                  <div
                    className="dashboard-list-row"
                    key={`${sender}-${index}`}
                  >

                    <div className="dashboard-rank">
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </div>

                    <div className="dashboard-row-main">

                      <strong>
                        {sender ||
                          "Unknown sender"}
                      </strong>

                      <div className="dashboard-bar">

                        <span
                          style={{
                            width: `${
                              Math.min(
                                100,
                                topSenders[0]?.[1]
                                  ? (Number(count) /
                                      Number(
                                        topSenders[0][1]
                                      )) *
                                    100
                                  : 0
                              )
                            }%`,
                          }}
                        />

                      </div>

                    </div>

                    <strong className="dashboard-row-count">
                      {formatNumber(count)}
                    </strong>

                  </div>
                )
              )

            )}

          </div>

        </div>


        {/* =================================================
            TOPICS
            ================================================= */}

        <div className="dashboard-panel">

          <div className="dashboard-panel-header">

            <div>

              <span className="dashboard-panel-eyebrow">
                CLASSIFICATION
              </span>

              <h2>
                TOPICS
              </h2>

            </div>

            <span className="dashboard-panel-count">
              {topicEntries.length}
            </span>

          </div>


          <div className="dashboard-list">

            {topicEntries.length === 0 ? (

              <div className="dashboard-empty">
                No topic information available.
              </div>

            ) : (

              topicEntries.map(
                ([topic, count], index) => (
                  <div
                    className="dashboard-list-row"
                    key={`${topic}-${index}`}
                  >

                    <div className="dashboard-rank">
                      {String(
                        index + 1
                      ).padStart(2, "0")}
                    </div>

                    <div className="dashboard-row-main">

                      <strong>
                        {topic}
                      </strong>

                      <div className="dashboard-bar">

                        <span
                          style={{
                            width: `${
                              topicEntries[0]?.[1]
                                ? Math.min(
                                    100,
                                    (Number(count) /
                                      Number(
                                        topicEntries[0][1]
                                      )) *
                                      100
                                  )
                                : 0
                            }%`,
                          }}
                        />

                      </div>

                    </div>

                    <strong className="dashboard-row-count">
                      {formatNumber(count)}
                    </strong>

                  </div>
                )
              )

            )}

          </div>

        </div>

      </div>


      {/* =================================================
          SYSTEM FOOTNOTE
          ================================================= */}

      <div className="dashboard-footnote">

        <span>
          ■
        </span>

        Dataset statistics are loaded directly
        from the email intelligence backend.

      </div>

    </section>
  );
}