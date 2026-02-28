/**
 * api/client.js
 * -------------
 * All HTTP calls to the FastAPI backend in one place.
 * Never write fetch() calls directly in components.
 *
 * If the API base URL changes (e.g., staging vs production),
 * update it here — not in 10 different components.
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Send a chat message to the backend agent.
 * @param {string} sessionId - Unique session identifier
 * @param {string} message - User's query
 * @returns {Promise<ChatResponse>}
 */
export async function sendMessage(sessionId, message) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Clear conversation history for a session.
 * Called when user starts a new chat.
 */
export async function clearSession(sessionId) {
  await fetch(`${BASE_URL}/session/${sessionId}`, {
    method: "DELETE",
  });
}

/**
 * Check backend health.
 * @returns {Promise<HealthResponse>}
 */
export async function checkHealth() {
  const response = await fetch(`${BASE_URL}/health`);
  return response.json();
}
