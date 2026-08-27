import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 120000,
});

export default api;

export const endpoints = {
  // ================================
  // AI QUERY
  // ================================

  query: "/query",

  // ================================
  // EMAILS
  // ================================

  emails: "/emails",
  emailCount: "/emails/count",

  // ================================
  // INSIGHTS
  // ================================

  insights: "/insights",

  summary: "/insights/summary",

  topics: "/insights/topics",

  entities: "/insights/entities",

  timeline: "/insights/timeline",

  hubs: "/insights/hubs",

  risk: "/insights/high-risk",

  // ================================
  // INGESTION
  // ================================

  ingestionStatus: "/ingestion/status",

  ingestionStart: "/ingestion/start",
};