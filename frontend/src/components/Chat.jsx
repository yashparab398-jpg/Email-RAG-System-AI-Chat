import {
  useEffect,
  useRef,
  useState,
} from "react";

import Sidebar from "./Sidebar";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import SourcePanel from "./SourcePanel";
import SuggestedQuestions from "./SuggestedQuestions";

import Dashboard from "./Dashboard";
import Entities from "./Entities";
import Timeline from "./Timeline";
import RiskAnalysis from "./RiskAnalysis";
import CommunicationHubs from "./CommunicationHubs";
import IngestionProgress from "./IngestionProgress";

import "../styles/chat.css";


/* =========================================================
   WEBSOCKET URL
   ========================================================= */

const WS_URL = "ws://127.0.0.1:8000/chat";


/* =========================================================
   SESSION ID
   ========================================================= */

function createSessionId() {

  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {

    return crypto.randomUUID();

  }

  return `session-${Date.now()}-${Math.random()
    .toString(36)
    .slice(2)}`;
}


/* =========================================================
   CHAT
   ========================================================= */

export default function Chat() {


  /* =====================================================
     NAVIGATION
     ===================================================== */

  const [activeView, setActiveView] =
    useState("chat");


  /* =====================================================
     CHAT STATE
     ===================================================== */

  const [messages, setMessages] =
    useState([]);

  const [input, setInput] =
    useState("");

  const [selectedSource, setSelectedSource] =
    useState(null);

  const [isLoading, setIsLoading] =
    useState(false);

  const [isConnected, setIsConnected] =
    useState(false);


  /* =====================================================
     WEBSOCKET
     ===================================================== */

  const socketRef =
    useRef(null);

  const reconnectTimerRef =
    useRef(null);

  const sessionIdRef =
    useRef(createSessionId());


  /* =====================================================
     PENDING SOURCES
     ===================================================== */

  const pendingSourcesRef =
    useRef([]);


  /* =====================================================
     AUTO SCROLL
     ===================================================== */

  const messagesEndRef =
    useRef(null);


  /* =====================================================
     CONNECT WEBSOCKET
     ===================================================== */

  const connectWebSocket = () => {

    /* -----------------------------------------------------
       Don't create duplicate connections.
       ----------------------------------------------------- */

    if (
      socketRef.current &&
      (
        socketRef.current.readyState ===
          WebSocket.OPEN ||
        socketRef.current.readyState ===
          WebSocket.CONNECTING
      )
    ) {

      return;

    }


    console.log(
      "[WS] Connecting..."
    );


    const socket =
      new WebSocket(
        WS_URL
      );


    socketRef.current =
      socket;


    /* =====================================================
       OPEN
       ===================================================== */

    socket.onopen = () => {

      console.log(
        "[WS] Connected."
      );

      setIsConnected(true);

    };


    /* =====================================================
       MESSAGE
       ===================================================== */

    socket.onmessage = (
      event
    ) => {

      try {

        const data =
          JSON.parse(
            event.data
          );


        console.log(
          "[WS] Event:",
          data
        );


        /* ================================================
           RETRIEVAL STARTED
           ================================================ */

        if (
          data.type ===
          "retrieval_started"
        ) {

          pendingSourcesRef.current =
            [];

          setIsLoading(true);

          return;

        }


        /* ================================================
           SOURCE FOUND
           ================================================ */

        if (
          data.type ===
          "source_found"
        ) {

          if (
            data.email
          ) {

            pendingSourcesRef.current.push(
              data.email
            );

          }

          return;

        }


        /* ================================================
           ASSISTANT RESPONSE
           ================================================ */

        if (
          data.type ===
          "assistant_token"
        ) {

          const finalSources =
            Array.isArray(
              data.sources
            )
              ? data.sources
              : pendingSourcesRef.current;


          /* ----------------------------------------------
             Remove loading message before adding answer
             ---------------------------------------------- */

          setMessages(
            (previous) =>
              previous.filter(
                (message) =>
                  message.type !==
                  "loading"
              )
          );


          /* ----------------------------------------------
             Add assistant response
             ---------------------------------------------- */

          setMessages(
            (previous) => [

              ...previous,

              {
                type:
                  "assistant",

                data: {

                  answer:
                    data.answer ||
                    data.content ||
                    "No answer was generated.",

                  confidence:
                    data.confidence ??
                    0,

                  sources:
                    finalSources,

                },

              },

            ]
          );


          setIsLoading(false);

          return;

        }


        /* ================================================
           ASSISTANT DONE
           ================================================ */

        if (
          data.type ===
          "assistant_done"
        ) {

          setIsLoading(false);

          pendingSourcesRef.current =
            [];

          return;

        }


        /* ================================================
           ERROR
           ================================================ */

        if (
          data.type ===
          "error"
        ) {

          console.error(
            "[WS] Server error:",
            data.message
          );


          /* ----------------------------------------------
             Remove loading state
             ---------------------------------------------- */

          setMessages(
            (previous) =>
              previous.filter(
                (message) =>
                  message.type !==
                  "loading"
              )
          );


          /* ----------------------------------------------
             Add error message
             ---------------------------------------------- */

          setMessages(
            (previous) => [

              ...previous,

              {
                type:
                  "assistant",

                data: {

                  answer:
                    data.message ||
                    "The AI system could not process the request.",

                  confidence:
                    0,

                  sources:
                    [],

                },

              },

            ]
          );


          setIsLoading(false);

          return;

        }


      } catch (error) {

        console.error(
          "[WS] Invalid server message:",
          error
        );

      }

    };


    /* =====================================================
       CLOSE
       ===================================================== */

    socket.onclose = () => {

      console.log(
        "[WS] Connection closed."
      );


      setIsConnected(false);


      if (
        socketRef.current ===
        socket
      ) {

        socketRef.current =
          null;

      }


      /*
       * Automatically attempt to reconnect.
       *
       * This allows the UI to recover if
       * FastAPI is restarted.
       */

      if (
        reconnectTimerRef.current
      ) {

        return;

      }


      reconnectTimerRef.current =
        setTimeout(
          () => {

            reconnectTimerRef.current =
              null;

            connectWebSocket();

          },
          2000
        );

    };


    /* =====================================================
       ERROR
       ===================================================== */

    socket.onerror = (
      error
    ) => {

      console.error(
        "[WS] WebSocket error:",
        error
      );

    };

  };


  /* =====================================================
     INITIAL WEBSOCKET CONNECTION
     ===================================================== */

  useEffect(() => {

    connectWebSocket();


    return () => {

      if (
        reconnectTimerRef.current
      ) {

        clearTimeout(
          reconnectTimerRef.current
        );

        reconnectTimerRef.current =
          null;

      }


      if (
        socketRef.current
      ) {

        socketRef.current.close();

        socketRef.current =
          null;

      }

    };

  }, []);


  /* =====================================================
     AUTO SCROLL
     ===================================================== */

  useEffect(() => {

    if (
      activeView !==
      "chat"
    ) {

      return;

    }


    messagesEndRef.current?.scrollIntoView({
      behavior:
        "smooth",
    });

  }, [
    messages,
    activeView,
  ]);


  /* =====================================================
     RECENT SEARCH EVENT
     ===================================================== */

  useEffect(() => {

    const handleRecentSearch =
      (event) => {

        const search =
          event.detail;


        if (!search) {

          return;

        }


        setActiveView(
          "chat"
        );


        setInput(
          search
        );


        setSelectedSource(
          null
        );

      };


    window.addEventListener(
      "email-intelligence-search",
      handleRecentSearch
    );


    return () => {

      window.removeEventListener(
        "email-intelligence-search",
        handleRecentSearch
      );

    };

  }, []);


  /* =====================================================
     SEND MESSAGE
     ===================================================== */

  const sendMessage = () => {

    const question =
      input.trim();


    if (!question) {

      return;

    }


    if (isLoading) {

      return;

    }


    /* =====================================================
       CHECK CONNECTION
       ===================================================== */

    const socket =
      socketRef.current;


    if (
      !socket ||
      socket.readyState !==
        WebSocket.OPEN
    ) {

      console.warn(
        "[WS] Cannot send. WebSocket is not connected."
      );


      setMessages(
        (previous) => [

          ...previous,

          {
            type:
              "assistant",

            data: {

              answer:
                "The real-time AI connection is not available. Reconnecting...",

              confidence:
                0,

              sources:
                [],

            },

          },

        ]
      );


      return;

    }


    /* =====================================================
       ADD USER MESSAGE
       ===================================================== */

    setMessages(
      (previous) => [

        ...previous,

        {
          type:
            "user",

          text:
            question,
        },

      ]
    );


    /* =====================================================
       CLEAR INPUT
       ===================================================== */

    setInput("");


    /* =====================================================
       CLEAR SOURCE
       ===================================================== */

    setSelectedSource(
      null
    );


    /* =====================================================
       LOADING
       ===================================================== */

    setIsLoading(
      true
    );


    setMessages(
      (previous) => [

        ...previous,

        {
          type:
            "loading",
        },

      ]
    );


    /* =====================================================
       CLEAR PENDING SOURCES
       ===================================================== */

    pendingSourcesRef.current =
      [];


    /* =====================================================
       SEND WEBSOCKET MESSAGE
       ===================================================== */

    try {

      socket.send(
        JSON.stringify({

          type:
            "user_message",

          session_id:
            sessionIdRef.current,

          message:
            question,

          top_k:
            5,

        })
      );


      console.log(
        "[WS] Question sent:",
        question
      );


    } catch (error) {

      console.error(
        "[WS] Failed to send:",
        error
      );


      setMessages(
        (previous) =>
          previous.filter(
            (message) =>
              message.type !==
              "loading"
          )
      );


      setMessages(
        (previous) => [

          ...previous,

          {
            type:
              "assistant",

            data: {

              answer:
                "Unable to send the question to the AI system.",

              confidence:
                0,

              sources:
                [],

            },

          },

        ]
      );


      setIsLoading(
        false
      );

    }

  };


  /* =====================================================
     NAVIGATION
     ===================================================== */

  const handleViewChange =
    (view) => {

      setActiveView(
        view
      );

      setSelectedSource(
        null
      );

    };


  /* =====================================================
     HEADER TITLE
     ===================================================== */

  const getHeaderTitle =
    () => {

      switch (
        activeView
      ) {

        case "dashboard":
          return "Email Intelligence Dashboard";

        case "entities":
          return "Entity Intelligence";

        case "timeline":
          return "Timeline Analysis";

        case "risk":
          return "Risk Analysis";

        case "hubs":
          return "Communication Hubs";

        case "ingestion":
          return "Ingestion Progress";

        case "chat":
        default:
          return "AI Email Intelligence";

      }

    };


  /* =====================================================
     HEADER SUBTITLE
     ===================================================== */

  const getHeaderSubtitle =
    () => {

      switch (
        activeView
      ) {

        case "dashboard":
          return "Email Analytics";

        case "entities":
          return "People and communication entities";

        case "timeline":
          return "Historical email activity";

        case "risk":
          return "Risk and compliance intelligence";

        case "hubs":
          return "Communication network intelligence";

        case "ingestion":
          return "Dataset processing and indexing";

        case "chat":
        default:
          return "Email Knowledge Assistant";

      }

    };


  /* =====================================================
     CONNECTION STATUS
     ===================================================== */

  const connectionLabel =
    isLoading
      ? "AI Processing..."
      : isConnected
        ? "AI System Online"
        : "Connecting to AI...";


  /* =====================================================
     RENDER
     ===================================================== */

  return (

    <div className="chat-layout">


      {/* =================================================
          AMBIENT BACKGROUND
          ================================================= */}

      <div className="orb orb-1"></div>

      <div className="orb orb-2"></div>


      {/* =================================================
          SIDEBAR
          ================================================= */}

      <Sidebar
        activeView={
          activeView
        }

        setActiveView={
          handleViewChange
        }
      />


      {/* =================================================
          MAIN CONTENT
          ================================================= */}

      <main className="chat-container">


        {/* =================================================
            WINDOW CONTROLS
            ================================================= */}

        <div className="window-controls">

          <span className="red"></span>

          <span className="yellow"></span>

          <span className="green"></span>

        </div>


        {/* =================================================
            HEADER
            ================================================= */}

        <header className="chat-header">

          <div>

            <h1>
              {getHeaderTitle()}
            </h1>

            <p>
              {getHeaderSubtitle()}
            </p>

          </div>


          <div className="header-status">

            {connectionLabel}

          </div>

        </header>


        {/* =================================================
            CHAT VIEW
            ================================================= */}

        {activeView === "chat" && (

          <div className="view-container active-view">


            <div className="search-banner">

              <SuggestedQuestions
                setInput={
                  setInput
                }
              />

            </div>


            <MessageList
              messages={
                messages
              }

              setSelectedSources={
                setSelectedSource
              }

            />


            <div
              ref={
                messagesEndRef
              }
            />


            <MessageInput
              input={
                input
              }

              setInput={
                setInput
              }

              sendMessage={
                sendMessage
              }

              isLoading={
                isLoading
              }

              isConnected={
                isConnected
              }

            />

          </div>

        )}


        {/* =================================================
            DASHBOARD

            IMPORTANT:
            Only mount Dashboard when selected.
            This prevents unnecessary API requests.
            ================================================= */}

        {activeView === "dashboard" && (

          <div className="analytics-content analytics-view-visible">

            <Dashboard />

          </div>

        )}


        {/* =================================================
            ENTITIES

            Only mounted when selected.
            ================================================= */}

        {activeView === "entities" && (

          <div className="analytics-content analytics-view-visible">

            <Entities />

          </div>

        )}


        {/* =================================================
            TIMELINE

            Only mounted when selected.
            ================================================= */}

        {activeView === "timeline" && (

          <div className="analytics-content analytics-view-visible">

            <Timeline />

          </div>

        )}


        {/* =================================================
            RISK

            Only mounted when selected.
            ================================================= */}

        {activeView === "risk" && (

          <div className="analytics-content analytics-view-visible">

            <RiskAnalysis
              setSelectedSource={
                setSelectedSource
              }
            />

          </div>

        )}


        {/* =================================================
            COMMUNICATION HUBS

            Only mounted when selected.
            ================================================= */}

        {activeView === "hubs" && (

          <div className="analytics-content analytics-view-visible">

            <CommunicationHubs />

          </div>

        )}


        {/* =================================================
            INGESTION

            Only mounted when selected.

            This is especially important because
            IngestionProgress polls the backend every
            2 seconds.
            ================================================= */}

        {activeView === "ingestion" && (

          <div className="analytics-content analytics-view-visible">

            <IngestionProgress />

          </div>

        )}


      </main>


      {/* =================================================
          SOURCE PANEL
          ================================================= */}

      <SourcePanel
        source={
          selectedSource
        }
      />


    </div>

  );

}