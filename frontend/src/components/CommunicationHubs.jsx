import { useEffect, useMemo, useState } from "react";
import api from "../services/api";

export default function CommunicationHubs() {
  const [hubs, setHubs] = useState([]);
  const [search, setSearch] = useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  /* =====================================================
     LOAD COMMUNICATION HUBS
     ===================================================== */

  useEffect(() => {
    let mounted = true;

    async function loadHubs() {
      try {
        setLoading(true);
        setError("");

        const response =
          await api.get(
            "/insights/hubs"
          );

        if (!mounted) {
          return;
        }

        const data =
          response.data || {};

        const communicationHubs =
          Array.isArray(
            data.communication_hubs
          )
            ? data.communication_hubs
            : [];

        setHubs(
          communicationHubs
        );
      } catch (err) {
        console.error(
          "[HUBS] Failed to load:",
          err
        );

        if (mounted) {
          setError(
            "Communication hub data is currently unavailable."
          );
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadHubs();

    return () => {
      mounted = false;
    };
  }, []);

  /* =====================================================
     FILTER
     ===================================================== */

  const filteredHubs =
    useMemo(() => {
      const query =
        search
          .trim()
          .toLowerCase();

      if (!query) {
        return hubs;
      }

      return hubs.filter(
        ([person]) =>
          String(person)
            .toLowerCase()
            .includes(query)
      );
    }, [
      hubs,
      search,
    ]);

  /* =====================================================
     MAX COUNT
     ===================================================== */

  const maxCount =
    hubs.length > 0
      ? Number(hubs[0][1] || 0)
      : 0;

  /* =====================================================
     LOADING
     ===================================================== */

  if (loading) {
    return (
      <section className="analytics-page hubs-page">

        <div className="analytics-header">

          <div>

            <span className="analytics-eyebrow">
              COMMUNICATION NETWORK
            </span>

            <h1>
              Communication Hubs
            </h1>

            <p>
              Identify the most active
              communication participants.
            </p>

          </div>

          <div className="analytics-live-status">
            LOADING DATA
          </div>

        </div>

        <div className="hubs-loading">

          <div className="pixel-loader">

            <span></span>
            <span></span>
            <span></span>

          </div>

          <h2>
            BUILDING NETWORK
          </h2>

          <p>
            Loading communication activity...
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
      <section className="analytics-page hubs-page">

        <div className="analytics-header">

          <div>

            <span className="analytics-eyebrow">
              COMMUNICATION NETWORK
            </span>

            <h1>
              Communication Hubs
            </h1>

            <p>
              Identify the most active
              communication participants.
            </p>

          </div>

          <div className="analytics-live-status">
            OFFLINE
          </div>

        </div>

        <div className="hubs-error">

          <div className="hubs-error-icon">
            !
          </div>

          <h2>
            NETWORK DATA UNAVAILABLE
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
    <section className="analytics-page hubs-page">

      {/* =================================================
          HEADER
          ================================================= */}

      <div className="analytics-header">

        <div>

          <span className="analytics-eyebrow">
            COMMUNICATION NETWORK
          </span>

          <h1>
            Communication Hubs
          </h1>

          <p>
            Identify the most active
            communication participants.
          </p>

        </div>

        <div className="analytics-live-status">

          <span className="dashboard-status-dot"></span>

          HUBS ONLINE

        </div>

      </div>


      {/* =================================================
          STATISTICS
          ================================================= */}

      <div className="hubs-stats">

        <div className="hubs-stat-card">

          <span>
            DETECTED HUBS
          </span>

          <strong>
            {hubs.length}
          </strong>

          <small>
            Top communication participants
          </small>

        </div>


        <div className="hubs-stat-card">

          <span>
            TOP HUB
          </span>

          <strong className="hubs-stat-person">

            {hubs.length > 0
              ? hubs[0][0]
              : "—"}

          </strong>

          <small>
            Highest communication activity
          </small>

        </div>


        <div className="hubs-stat-card">

          <span>
            TOP ACTIVITY
          </span>

          <strong>
            {maxCount.toLocaleString(
              "en-IN"
            )}
          </strong>

          <small>
            Recorded communications
          </small>

        </div>

      </div>


      {/* =================================================
          TOOLBAR
          ================================================= */}

      <div className="hubs-toolbar">

        <div>

          <span className="dashboard-panel-eyebrow">
            PARTICIPANT ANALYSIS
          </span>

          <h2>
            MOST ACTIVE COMMUNICATION HUBS
          </h2>

        </div>

        <div className="hubs-search">

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
            placeholder="Search people..."
          />

        </div>

      </div>


      {/* =================================================
          HUB LIST
          ================================================= */}

      <div className="hubs-panel">

        {filteredHubs.length === 0 ? (

          <div className="hubs-empty">

            <div className="hubs-empty-icon">
              —
            </div>

            <h2>
              NO HUBS FOUND
            </h2>

            <p>
              No communication participants
              match the current search.
            </p>

          </div>

        ) : (

          <div className="hubs-list">

            {filteredHubs.map(
              ([person, count], index) => {

                const numericCount =
                  Number(count || 0);

                const percentage =
                  maxCount > 0
                    ? (
                        numericCount /
                        maxCount
                      ) * 100
                    : 0;

                return (
                  <div
                    className="hub-row"
                    key={`${person}-${index}`}
                  >

                    {/* RANK */}

                    <div className="hub-rank">
                      {String(
                        index + 1
                      ).padStart(
                        2,
                        "0"
                      )}
                    </div>


                    {/* AVATAR */}

                    <div className="hub-avatar">
                      {String(
                        person || "?"
                      )
                        .charAt(0)
                        .toUpperCase()}
                    </div>


                    {/* PERSON */}

                    <div className="hub-main">

                      <strong>
                        {person ||
                          "Unknown participant"}
                      </strong>

                      <div className="hub-bar">

                        <span
                          style={{
                            width:
                              `${percentage}%`,
                          }}
                        />

                      </div>

                    </div>


                    {/* COUNT */}

                    <div className="hub-count">

                      <strong>
                        {numericCount.toLocaleString(
                          "en-IN"
                        )}
                      </strong>

                      <span>
                        COMMUNICATIONS
                      </span>

                    </div>

                  </div>
                );
              }
            )}

          </div>

        )}

      </div>


      {/* =================================================
          FOOTNOTE
          ================================================= */}

      <div className="dashboard-footnote">

        <span>
          ■
        </span>

        Hub ranking is based on the total
        number of sender and recipient
        appearances in the indexed dataset.

      </div>

    </section>
  );
}