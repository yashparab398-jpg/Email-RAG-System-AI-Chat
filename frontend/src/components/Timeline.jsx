import { useEffect, useMemo, useState } from "react";
import api from "../services/api";

export default function Timeline() {
  const [timeline, setTimeline] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  /* =====================================================
     LOAD TIMELINE
     ===================================================== */

  useEffect(() => {
    let mounted = true;

    async function loadTimeline() {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(
          "/insights/timeline"
        );

        if (!mounted) {
          return;
        }

        const data = response.data || {};

        /*
         * Backend currently returns:
         *
         * {
         *   timeline: {
         *     "2000-01": 123,
         *     "2000-02": 456
         *   }
         * }
         */

        if (
          data.timeline &&
          typeof data.timeline === "object" &&
          !Array.isArray(data.timeline)
        ) {
          setTimeline(data.timeline);
        } else {
          setTimeline({});
        }
      } catch (err) {
        console.error(
          "[TIMELINE] Failed to load:",
          err
        );

        if (mounted) {
          setError(
            "Timeline data is currently unavailable."
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadTimeline();

    return () => {
      mounted = false;
    };
  }, []);

  /* =====================================================
     MONTH FORMAT
     ===================================================== */

  const formatMonth = (value) => {
    if (!value) {
      return "UNKNOWN";
    }

    const parts = String(value).split("-");

    if (parts.length !== 2) {
      return String(value).toUpperCase();
    }

    const year = parts[0];
    const month = Number(parts[1]);

    if (!month || month < 1 || month > 12) {
      return String(value).toUpperCase();
    }

    const date = new Date(
      Number(year),
      month - 1,
      1
    );

    return date
      .toLocaleDateString("en-IN", {
        month: "short",
        year: "numeric",
      })
      .toUpperCase();
  };

  /* =====================================================
     PREPARE MONTHLY DATA
     ===================================================== */

  const monthlyData = useMemo(() => {
    return Object.entries(timeline)
      .map(([month, count]) => ({
        month,
        label: formatMonth(month),
        count: Number(count || 0),
      }))
      .sort((a, b) =>
        a.month.localeCompare(b.month)
      );
  }, [timeline]);

  /* =====================================================
     FILTER
     ===================================================== */

  const filteredData = useMemo(() => {
    const query = search
      .trim()
      .toLowerCase();

    if (!query) {
      return monthlyData;
    }

    return monthlyData.filter((item) => {
      return (
        item.month
          .toLowerCase()
          .includes(query) ||
        item.label
          .toLowerCase()
          .includes(query)
      );
    });
  }, [monthlyData, search]);

  /* =====================================================
     STATISTICS
     ===================================================== */

  const totalEmails = useMemo(() => {
    return monthlyData.reduce(
      (total, item) =>
        total + item.count,
      0
    );
  }, [monthlyData]);

  const peakMonth = useMemo(() => {
    if (monthlyData.length === 0) {
      return null;
    }

    return monthlyData.reduce(
      (highest, current) =>
        current.count > highest.count
          ? current
          : highest
    );
  }, [monthlyData]);

  const averageEmails = useMemo(() => {
    if (monthlyData.length === 0) {
      return 0;
    }

    return Math.round(
      totalEmails /
        monthlyData.length
    );
  }, [
    totalEmails,
    monthlyData.length,
  ]);

  const maxCount = useMemo(() => {
    if (monthlyData.length === 0) {
      return 0;
    }

    return Math.max(
      ...monthlyData.map(
        (item) => item.count
      )
    );
  }, [monthlyData]);

  /* =====================================================
     LOADING
     ===================================================== */

  if (loading) {
    return (
      <section className="analytics-page timeline-page">

        <div className="analytics-header">

          <div>

            <span className="analytics-eyebrow">
              COMMUNICATION HISTORY
            </span>

            <h1>
              Timeline Analysis
            </h1>

            <p>
              Explore historical email activity
              across the dataset.
            </p>

          </div>

          <div className="analytics-live-status">
            LOADING DATA
          </div>

        </div>

        <div className="timeline-loading">

          <div className="pixel-loader">

            <span></span>
            <span></span>
            <span></span>

          </div>

          <h2>
            BUILDING TIMELINE
          </h2>

          <p>
            Loading historical communication
            activity...
          </p>

        </div>

      </section>
    );
  }

  /* =====================================================
     ERROR
     ===================================================== */

  if (error) {
    return (
      <section className="analytics-page timeline-page">

        <div className="analytics-header">

          <div>

            <span className="analytics-eyebrow">
              COMMUNICATION HISTORY
            </span>

            <h1>
              Timeline Analysis
            </h1>

            <p>
              Explore historical email activity
              across the dataset.
            </p>

          </div>

          <div className="analytics-live-status">
            OFFLINE
          </div>

        </div>

        <div className="timeline-error">

          <div className="timeline-error-icon">
            !
          </div>

          <h2>
            TIMELINE DATA UNAVAILABLE
          </h2>

          <p>
            {error}
          </p>

        </div>

      </section>
    );
  }

  /* =====================================================
     RENDER
     ===================================================== */

  return (
    <section className="analytics-page timeline-page">

      {/* =================================================
          HEADER
          ================================================= */}

      <div className="analytics-header">

        <div>

          <span className="analytics-eyebrow">
            COMMUNICATION HISTORY
          </span>

          <h1>
            Timeline Analysis
          </h1>

          <p>
            Explore historical email activity
            across the dataset.
          </p>

        </div>

        <div className="analytics-live-status">

          <span className="dashboard-status-dot"></span>

          TIMELINE ONLINE

        </div>

      </div>


      {/* =================================================
          SUMMARY
          ================================================= */}

      <div className="timeline-summary">

        <div className="timeline-summary-card">

          <span>
            TOTAL EMAILS
          </span>

          <strong>
            {totalEmails.toLocaleString(
              "en-IN"
            )}
          </strong>

          <small>
            Indexed communications
          </small>

        </div>


        <div className="timeline-summary-card">

          <span>
            ACTIVE MONTHS
          </span>

          <strong>
            {monthlyData.length.toLocaleString(
              "en-IN"
            )}
          </strong>

          <small>
            Months with recorded activity
          </small>

        </div>


        <div className="timeline-summary-card">

          <span>
            PEAK PERIOD
          </span>

          <strong className="timeline-view-label">

            {peakMonth
              ? peakMonth.label
              : "—"}

          </strong>

          <small>

            {peakMonth
              ? `${peakMonth.count.toLocaleString(
                  "en-IN"
                )} emails`
              : "No data"}

          </small>

        </div>

      </div>


      {/* =================================================
          TOOLBAR
          ================================================= */}

      <div className="timeline-toolbar">

        <div>

          <span className="dashboard-panel-eyebrow">
            EMAIL ACTIVITY
          </span>

          <h2>
            MONTHLY COMMUNICATION TIMELINE
          </h2>

        </div>

        <div className="timeline-search">

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
            placeholder="Search month..."
          />

        </div>

      </div>


      {/* =================================================
          VISUALIZATION
          ================================================= */}

      <div className="timeline-panel">

        {filteredData.length === 0 ? (

          <div className="timeline-empty">

            <div className="timeline-empty-icon">
              —
            </div>

            <h2>
              NO TIMELINE DATA
            </h2>

            <p>
              No monthly email activity
              matches the current search.
            </p>

          </div>

        ) : (

          <div className="timeline-chart">

            {/* CHART HEADER */}

            <div className="timeline-chart-header">

              <div>

                <span>
                  EMAIL VOLUME
                </span>

                <strong>
                  MONTHLY ACTIVITY
                </strong>

              </div>

              <div className="timeline-average">

                AVG / MONTH

                <strong>
                  {averageEmails.toLocaleString(
                    "en-IN"
                  )}
                </strong>

              </div>

            </div>


            {/* BAR CHART */}

            <div className="timeline-bars">

              {filteredData.map(
                (item) => {

                  const percentage =
                    maxCount > 0
                      ? (
                          item.count /
                          maxCount
                        ) * 100
                      : 0;

                  return (
                    <div
                      className="timeline-bar-column"
                      key={item.month}
                      title={`${item.label}: ${item.count.toLocaleString(
                        "en-IN"
                      )} emails`}
                    >

                      {/* VALUE */}

                      <span className="timeline-bar-value">

                        {item.count.toLocaleString(
                          "en-IN"
                        )}

                      </span>


                      {/* BAR */}

                      <div className="timeline-bar-track">

                        <div
                          className="timeline-bar"
                          style={{
                            height:
                              `${Math.max(
                                percentage,
                                2
                              )}%`,
                          }}
                        />

                      </div>


                      {/* LABEL */}

                      <span className="timeline-bar-label">

                        {item.label}

                      </span>

                    </div>
                  );
                }
              )}

            </div>

          </div>

        )}

      </div>


      {/* =================================================
          DATA TABLE
          ================================================= */}

      {filteredData.length > 0 && (

        <div className="timeline-data-panel">

          <div className="timeline-data-header">

            <span>
              PERIOD
            </span>

            <span>
              EMAILS
            </span>

            <span>
              ACTIVITY
            </span>

          </div>


          <div className="timeline-data-list">

            {filteredData.map(
              (item) => {

                const percentage =
                  maxCount > 0
                    ? (
                        item.count /
                        maxCount
                      ) * 100
                    : 0;

                return (
                  <div
                    className="timeline-data-row"
                    key={`row-${item.month}`}
                  >

                    <strong>
                      {item.label}
                    </strong>

                    <span>
                      {item.count.toLocaleString(
                        "en-IN"
                      )}
                    </span>

                    <div className="timeline-mini-bar">

                      <span
                        style={{
                          width:
                            `${percentage}%`,
                        }}
                      />

                    </div>

                  </div>
                );
              }
            )}

          </div>

        </div>

      )}


      {/* =================================================
          FOOTNOTE
          ================================================= */}

      {monthlyData.length > 0 && (

        <div className="dashboard-footnote">

          <span>
            ■
          </span>

          Timeline activity is calculated from
          the monthly email counts returned by
          the indexed dataset.

        </div>

      )}

    </section>
  );
}