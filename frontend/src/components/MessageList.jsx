export default function MessageList({
  messages,
  setSelectedSources,
}) {
  /* =====================================================
     EMPTY CHAT
     ===================================================== */

  if (!messages || messages.length === 0) {
    return (
      <div className="messages">

        <div className="empty-chat">

          <div className="empty-chat-icon">
            ✦
          </div>

          <h2>
            Ask your email intelligence
          </h2>

          <p>
            Search across the Enron email
            knowledge base using natural language.
          </p>

        </div>

      </div>
    );
  }

  /* =====================================================
     MESSAGE LIST
     ===================================================== */

  return (
    <div className="messages">

      {messages.map(
        (message, index) => {

          /* ==============================================
             USER MESSAGE
             ============================================== */

          if (
            message.type === "user"
          ) {
            return (
              <div
                key={`user-${index}`}
                className="user-message fade-in"
              >

                <div className="user-bubble">
                  {message.text}
                </div>

              </div>
            );
          }

          /* ==============================================
             LOADING MESSAGE
             ============================================== */

          if (
            message.type === "loading"
          ) {
            return (
              <div
                key={`loading-${index}`}
                className="assistant-card fade-in"
              >

                <div className="assistant-answer">

                  <div className="assistant-top">

                    <div className="ai-badge">
                      AI
                    </div>

                    <span className="confidence-badge">
                      Analyzing
                    </span>

                  </div>

                  <div className="assistant-response">

                    Searching the email
                    knowledge base

                    <span className="loading-dots">

                      <span></span>

                      <span></span>

                      <span></span>

                    </span>

                  </div>

                </div>

              </div>
            );
          }

          /* ==============================================
             ASSISTANT MESSAGE
             ============================================== */

          if (
            message.type ===
              "assistant" &&
            message.data
          ) {
            const data =
              message.data;

            const sources =
              data.sources || [];

            const confidence =
              data.confidence;

            return (
              <div
                key={`assistant-${index}`}
                className="assistant-card fade-in"
              >

                {/* ======================================
                    ANSWER
                    ====================================== */}

                <div className="assistant-answer">

                  <div className="assistant-top">

                    <div className="ai-badge">
                      AI
                    </div>

                    {confidence !==
                      undefined &&
                      confidence !==
                        null && (
                        <span className="confidence-badge">

                          Confidence{" "}

                          {typeof confidence ===
                          "number"
                            ? `${Math.round(
                                confidence
                              )}%`
                            : confidence}

                        </span>
                      )}

                  </div>

                  <div className="assistant-response">

                    {data.answer ||
                      "No answer was generated."}

                  </div>

                </div>

                {/* ======================================
                    SOURCES
                    ====================================== */}

                {sources.length >
                  0 && (
                  <>

                    <div
                      style={{
                        padding:
                          "0 21px 12px",
                        color:
                          "#6f7689",
                        fontSize:
                          "10px",
                        fontWeight:
                          700,
                        textTransform:
                          "uppercase",
                        letterSpacing:
                          "0.8px",
                      }}
                    >

                      {sources.length}{" "}
                      Source
                      {sources.length !==
                      1
                        ? "s"
                        : ""}{" "}
                      Used

                    </div>

                    <div className="email-list">

                      {sources.map(
                        (
                          email,
                          sourceIndex
                        ) => (
                          <div
                            key={
                              email._id ||
                              email.message_id ||
                              `source-${sourceIndex}`
                            }
                            className="email-card"
                            onClick={() =>
                              setSelectedSources(
                                email
                              )
                            }
                          >

                            <div className="email-card-header">

                              <span className="mail-dot" />

                              <h4>
                                {email.subject ||
                                  "No Subject"}
                              </h4>

                            </div>

                            <p>
                              {(
                                email.clean_body ||
                                email.body ||
                                "No email content available."
                              )
                                .replace(
                                  /\n/g,
                                  " "
                                )
                                .replace(
                                  /\s+/g,
                                  " "
                                )
                                .trim()}
                            </p>

                            <span className="open-mail">
                              Open source
                            </span>

                          </div>
                        )
                      )}

                    </div>

                  </>
                )}

                {/* ======================================
                    NO SOURCES
                    ====================================== */}

                {sources.length ===
                  0 && (
                  <div
                    style={{
                      padding:
                        "0 21px 20px",
                      color:
                        "#6f7689",
                      fontSize:
                        "11px",
                    }}
                  >

                    No source emails were
                    returned for this answer.

                  </div>
                )}

              </div>
            );
          }

          return null;
        }
      )}

    </div>
  );
}