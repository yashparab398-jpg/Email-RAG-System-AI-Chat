import { useEffect, useMemo, useState } from "react";
import api from "../services/api";

export default function IngestionProgress() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");

  /* =====================================================
     LOAD STATUS
     ===================================================== */

  const loadStatus = async () => {
    try {
      const response = await api.get(
        "/ingestion/status"
      );

      setStatus(
        response.data || {}
      );

      setError("");
    } catch (err) {
      console.error(
        "[INGESTION] Failed to load status:",
        err
      );

      setError(
        "Ingestion service is currently unavailable."
      );
    } finally {
      setLoading(false);
    }
  };

  /* =====================================================
     INITIAL LOAD + POLLING
     ===================================================== */

  useEffect(() => {
    loadStatus();

    const interval =
      setInterval(() => {
        loadStatus();
      }, 2000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  /* =====================================================
     START INGESTION
     ===================================================== */

  const startIngestion = async () => {
    if (starting) {
      return;
    }

    try {
      setStarting(true);
      setError("");

      await api.post(
        "/ingestion/start"
      );

      await loadStatus();
    } catch (err) {
      console.error(
        "[INGESTION] Failed to start:",
        err
      );

      setError(
        "Unable to start email ingestion."
      );
    } finally {
      setStarting(false);
    }
  };

  /* =====================================================
     DATA
     ===================================================== */

  const ingestion =
    status?.ingestion || {};

  const processed =
    Number(
      status?.processed ??
      ingestion?.processed ??
      0
    );

  const failed =
    Number(
      status?.failed ??
      ingestion?.failed ??
      0
    );

  const ingestionStatus =
    String(
      ingestion?.status ||
      "unknown"
    ).toLowerCase();

  /* =====================================================
     STATUS LABEL
     ===================================================== */

  const statusLabel =
    ingestionStatus === "processing"
      ? "PROCESSING"
      : ingestionStatus === "completed"
        ? "COMPLETED"
        : ingestionStatus === "failed"
          ? "FAILED"
          : "READY";

  /* =====================================================
     STATUS CLASS
     ===================================================== */

  const statusClass =
    ingestionStatus === "processing"
      ? "ingestion-processing"
      : ingestionStatus === "completed"
        ? "ingestion-completed"
        : ingestionStatus === "failed"
          ? "ingestion-failed"
          : "ingestion-ready";

  /* =====================================================
     ACTIVITY MESSAGE
     ===================================================== */

  const activityMessage =
    useMemo(() => {
      if (
        ingestionStatus ===
        "processing"
      ) {
        return "Email dataset is currently being processed.";
      }

      if (
        ingestionStatus ===
        "completed"
      ) {
        return "Email ingestion completed successfully.";
      }

      if (
        ingestionStatus ===
        "failed"
      ) {
        return "Email ingestion encountered processing failures.";
      }

      return "System is ready to ingest the email dataset.";
    }, [ingestionStatus]);

  /* =====================================================
     RENDER
     ===================================================== */

  return (
    <section className="analytics-page ingestion-page">

      {/* =================================================
          HEADER
          ================================================= */}

      <div className="analytics-header">

        <div>

          <span className="analytics-eyebrow">
            DATA INGESTION
          </span>

          <h1>
            Ingestion Progress
          </h1>

          <p>
            Monitor email dataset processing
            and indexing activity.
          </p>

        </div>

        <div
          className={`analytics-live-status ${statusClass}`}
        >

          <span className="dashboard-status-dot"></span>

          {statusLabel}

        </div>

      </div>


      {/* =================================================
          MAIN STATUS CARD
          ================================================= */}

      <div className="ingestion-main-card">

        <div className="ingestion-card-header">

          <div>

            <span className="dashboard-panel-eyebrow">
              INGESTION ENGINE
            </span>

            <h2>
              EMAIL DATASET PROCESSING
            </h2>

          </div>

          <div className="ingestion-status-badge">

            {statusLabel}

          </div>

        </div>


        {/* =================================================
            ACTIVITY MESSAGE
            ================================================= */}

        <div className="ingestion-activity">

          <div className="ingestion-activity-icon">
            {ingestionStatus ===
            "processing"
              ? "↻"
              : ingestionStatus ===
                  "completed"
                ? "✓"
                : "■"}
          </div>

          <div>

            <strong>
              {activityMessage}
            </strong>

            <span>
              Status updates refresh automatically.
            </span>

          </div>

        </div>


        {/* =================================================
            LIVE COUNTS
            ================================================= */}

        <div className="ingestion-count-grid">

          <div className="ingestion-count-card">

            <span>
              PROCESSED
            </span>

            <strong>
              {processed.toLocaleString(
                "en-IN"
              )}
            </strong>

            <small>
              Emails indexed
            </small>

          </div>


          <div className="ingestion-count-card">

            <span>
              FAILED
            </span>

            <strong>
              {failed.toLocaleString(
                "en-IN"
              )}
            </strong>

            <small>
              Emails rejected
            </small>

          </div>


          <div className="ingestion-count-card">

            <span>
              CURRENT STATE
            </span>

            <strong className="ingestion-state-value">
              {statusLabel}
            </strong>

            <small>
              Ingestion engine status
            </small>

          </div>

        </div>


        {/* =================================================
            LIVE ACTIVITY BAR
            ================================================= */}

        <div className="ingestion-progress-section">

          <div className="ingestion-progress-header">

            <span>
              PROCESSING ACTIVITY
            </span>

            <strong>

              {ingestionStatus ===
              "processing"
                ? "LIVE"
                : ingestionStatus ===
                    "completed"
                  ? "DONE"
                  : "—"}

            </strong>

          </div>

          <div className="ingestion-progress-track">

            <div
              className={
                ingestionStatus ===
                "processing"
                  ? "ingestion-progress-fill processing"
                  : ingestionStatus ===
                      "completed"
                    ? "ingestion-progress-fill completed"
                    : "ingestion-progress-fill"
              }
            />

          </div>

          <div className="ingestion-progress-note">

            {ingestionStatus ===
            "processing"
              ? "Processing email batches..."
              : ingestionStatus ===
                  "completed"
                ? "All available email batches have been processed."
                : "Waiting for ingestion to start."}

          </div>

        </div>


        {/* =================================================
            ACTION
            ================================================= */}

        <div className="ingestion-actions">

          <button
            type="button"
            className="ingestion-start-button"
            onClick={startIngestion}
            disabled={
              starting ||
              ingestionStatus ===
                "processing"
            }
          >

            <span>
              {starting
                ? "..."
                : ingestionStatus ===
                    "processing"
                  ? "PROCESSING"
                  : "START INGESTION"}
            </span>

          </button>

          <button
            type="button"
            className="ingestion-refresh-button"
            onClick={loadStatus}
          >
            ↻ REFRESH STATUS
          </button>

        </div>

      </div>


      {/* =================================================
          SYSTEM INFORMATION
          ================================================= */}

      <div className="ingestion-info-panel">

        <div>

          <span>
            DATA SOURCE
          </span>

          <strong>
            ENRON EMAIL DATASET
          </strong>

        </div>

        <div>

          <span>
            PROCESSING MODE
          </span>

          <strong>
            BATCH PROCESSING
          </strong>

        </div>

        <div>

          <span>
            STATUS REFRESH
          </span>

          <strong>
            EVERY 2 SECONDS
          </strong>

        </div>

      </div>


      {/* =================================================
          ERROR
          ================================================= */}

      {error && (

        <div className="ingestion-error">

          <span>
            !
          </span>

          {error}

        </div>

      )}


      {/* =================================================
          FOOTNOTE
          ================================================= */}

      <div className="dashboard-footnote">

        <span>
          ■
        </span>

        Ingestion status is retrieved directly
        from the backend processing service.

      </div>

    </section>
  );
}