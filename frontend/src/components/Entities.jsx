import { useEffect, useMemo, useState } from "react";
import api, { endpoints } from "../services/api";

export default function Entities() {
  const [entities, setEntities] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function loadEntities() {
      try {
        setLoading(true);
        setError("");

        console.log(
          "[ENTITIES] Requesting:",
          endpoints.entities
        );

        const response = await api.get(
          endpoints.entities
        );

        console.log(
          "[ENTITIES] Response:",
          response.data
        );

        if (!mounted) {
          return;
        }

        const data = response.data;

        /*
         * Backend is expected to return:
         *
         * {
         *   top_entities: [...]
         * }
         */

        const topEntities =
          Array.isArray(data?.top_entities)
            ? data.top_entities
            : [];

        setEntities(topEntities);

      } catch (err) {
        console.error(
          "[ENTITIES] Failed to load:",
          err
        );

        console.error(
          "[ENTITIES] Response:",
          err.response?.data
        );

        if (mounted) {
          setError(
            "Entity data is currently unavailable."
          );
        }

      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    loadEntities();

    return () => {
      mounted = false;
    };
  }, []);

  /* =====================================================
     SEARCH
     ===================================================== */

  const filteredEntities = useMemo(() => {
    const query =
      search.trim().toLowerCase();

    if (!query) {
      return entities;
    }

    return entities.filter(
      ([entity]) =>
        String(entity)
          .toLowerCase()
          .includes(query)
    );
  }, [entities, search]);

  /* =====================================================
     STATISTICS
     ===================================================== */

  const totalMentions =
    entities.reduce(
      (total, [, count]) =>
        total + Number(count || 0),
      0
    );

  const highestCount =
    entities.length > 0
      ? Math.max(
          ...entities.map(
            ([, count]) =>
              Number(count || 0)
          )
        )
      : 0;

  /* =====================================================
     RENDER
     ===================================================== */

  return (
    <section className="analytics-page">

      {/* =================================================
          HEADER
          ================================================= */}

      <div className="analytics-header">

        <div>

          <span className="analytics-eyebrow">
            ENTITY INTELLIGENCE
          </span>

          <h1>
            Email Entities
          </h1>

          <p>
            Discover the people and email addresses
            appearing most frequently across the
            Enron knowledge base.
          </p>

        </div>

        <div className="analytics-status">

          <span className="status-dot"></span>

          {loading
            ? "Loading Dataset"
            : error
              ? "Offline"
              : "Live Dataset"}

        </div>

      </div>


      {/* =================================================
          STAT CARDS
          ================================================= */}

      <div className="analytics-stats">

        <div className="analytics-stat-card">

          <span className="analytics-stat-label">
            ENTITIES FOUND
          </span>

          <strong>
            {loading
              ? "—"
              : entities.length}
          </strong>

          <small>
            Unique email entities
          </small>

        </div>


        <div className="analytics-stat-card">

          <span className="analytics-stat-label">
            TOTAL MENTIONS
          </span>

          <strong>
            {loading
              ? "—"
              : totalMentions.toLocaleString()}
          </strong>

          <small>
            Entity occurrences
          </small>

        </div>


        <div className="analytics-stat-card">

          <span className="analytics-stat-label">
            TOP ACTIVITY
          </span>

          <strong>
            {loading
              ? "—"
              : highestCount.toLocaleString()}
          </strong>

          <small>
            Mentions by top entity
          </small>

        </div>

      </div>


      {/* =================================================
          SEARCH TOOLBAR
          ================================================= */}

      <div className="analytics-toolbar">

        <div>

          <h2>
            Most Active Entities
          </h2>

          <p>
            Ranked by frequency across email content.
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
            placeholder="Search entities..."
          />

        </div>

      </div>


      {/* =================================================
          CONTENT
          ================================================= */}

      <div className="entity-panel">

        {/* LOADING */}

        {loading && (

          <div className="analytics-empty">

            <div className="analytics-loader">

              <span></span>
              <span></span>
              <span></span>

            </div>

            <h3>
              Analyzing entities
            </h3>

            <p>
              Loading entity intelligence
              from the email knowledge base.
            </p>

          </div>

        )}


        {/* ERROR */}

        {!loading && error && (

          <div className="analytics-empty">

            <div className="analytics-empty-icon">
              !
            </div>

            <h3>
              Data unavailable
            </h3>

            <p>
              {error}
            </p>

          </div>

        )}


        {/* NO RESULTS */}

        {!loading &&
          !error &&
          filteredEntities.length === 0 && (

            <div className="analytics-empty">

              <div className="analytics-empty-icon">
                ⌕
              </div>

              <h3>
                No entities found
              </h3>

              <p>
                Try a different search term.
              </p>

            </div>

          )}


        {/* ENTITY LIST */}

        {!loading &&
          !error &&
          filteredEntities.length > 0 && (

            <div className="entity-list">

              {filteredEntities.map(
                ([entity, count], index) => {

                  const numericCount =
                    Number(count || 0);

                  const percentage =
                    highestCount > 0
                      ? Math.max(
                          5,
                          (numericCount /
                            highestCount) *
                            100
                        )
                      : 0;

                  return (

                    <div
                      className="entity-row"
                      key={`${entity}-${index}`}
                    >

                      <div className="entity-rank">
                        {String(
                          index + 1
                        ).padStart(2, "0")}
                      </div>


                      <div className="entity-avatar">

                        {String(entity)
                          .charAt(0)
                          .toUpperCase()}

                      </div>


                      <div className="entity-main">

                        <div className="entity-name">
                          {entity}
                        </div>

                        <div className="entity-bar">

                          <div
                            className="entity-bar-fill"
                            style={{
                              width:
                                `${percentage}%`,
                            }}
                          />

                        </div>

                      </div>


                      <div className="entity-count">

                        <strong>
                          {numericCount.toLocaleString()}
                        </strong>

                        <span>
                          mentions
                        </span>

                      </div>

                    </div>

                  );
                }
              )}

            </div>

          )}

      </div>

    </section>
  );
}