export default function SourcePanel({ source }) {

  /* =====================================================
     EMPTY STATE
     ===================================================== */

  if (!source) {
    return (
      <aside className="sources-panel">

        <div className="empty-source">

          <div className="viewer-icon">
            ✉
          </div>

          <div className="source-empty-label">
            SOURCE INSPECTION
          </div>

          <h2>
            EMAIL VIEWER
          </h2>

          <p>
            Select a source email from an AI
            response to inspect the complete
            message and metadata.
          </p>

        </div>

      </aside>
    );
  }


  /* =====================================================
     DATE FORMAT
     ===================================================== */

  const formatDate = (date) => {

    if (!date) {
      return "UNKNOWN DATE";
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

      return parsed
        .toLocaleString(
          "en-IN",
          {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
          }
        )
        .toUpperCase();

    } catch {

      return date;

    }

  };


  /* =====================================================
     RECIPIENT FORMAT
     ===================================================== */

  const formatRecipients = (
    value
  ) => {

    if (!value) {
      return "—";
    }

    if (Array.isArray(value)) {
      return value.join(", ");
    }

    return value;

  };


  /* =====================================================
     BODY
     ===================================================== */

  const body =
    source.body ||
    source.clean_body ||
    "No email content available.";


  /* =====================================================
     RENDER
     ===================================================== */

  return (

    <aside className="sources-panel">

      <div className="source-content">


        {/* =================================================
            HEADER
            ================================================= */}

        <div className="source-header">

          <div className="source-header-top">

            <div className="source-tag">
              SOURCE EMAIL
            </div>

            <div className="source-live-indicator">

              <span></span>

              INSPECTING

            </div>

          </div>


          {/* =================================================
              SUBJECT
              ================================================= */}

          <h2>
            {source.subject ||
              "NO SUBJECT"}
          </h2>


          {/* =================================================
              METADATA
              ================================================= */}

          <div className="source-meta">


            {/* FROM */}

            <div className="meta-card">

              <span>
                FROM
              </span>

              <strong>
                {source.from ||
                  "UNKNOWN SENDER"}
              </strong>

            </div>


            {/* TO */}

            <div className="meta-card">

              <span>
                TO
              </span>

              <strong>
                {formatRecipients(
                  source.to
                )}
              </strong>

            </div>


            {/* CC */}

            {source.cc && (

              <div className="meta-card">

                <span>
                  CC
                </span>

                <strong>
                  {formatRecipients(
                    source.cc
                  )}
                </strong>

              </div>

            )}


            {/* DATE */}

            <div className="meta-card">

              <span>
                DATE
              </span>

              <strong>
                {formatDate(
                  source.date
                )}
              </strong>

            </div>


            {/* MESSAGE ID */}

            {source.message_id && (

              <div className="meta-card">

                <span>
                  MESSAGE ID
                </span>

                <strong className="source-message-id">
                  {source.message_id}
                </strong>

              </div>

            )}

          </div>

        </div>


        {/* =================================================
            EMAIL BODY HEADER
            ================================================= */}

        <div className="source-body-header">

          <div>

            <span>
              MESSAGE CONTENT
            </span>

            <strong>
              FULL EMAIL
            </strong>

          </div>

          <span className="source-body-icon">
            ✉
          </span>

        </div>


        {/* =================================================
            EMAIL BODY
            ================================================= */}

        <div className="source-body">

          {body}

        </div>


        {/* =================================================
            SOURCE FOOTER
            ================================================= */}

        <div className="source-footer">

          <span>
            ■
          </span>

          SOURCE RETRIEVED FROM
          INDEXED EMAIL DATASET

        </div>

      </div>

    </aside>

  );

}