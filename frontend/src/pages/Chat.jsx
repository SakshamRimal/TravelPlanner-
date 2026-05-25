import { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { api } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { useAppState } from "../context/AppStateContext"; // ← ADD
import {
  IconSparkles,
  IconArrowUp,
  IconTrash,
  IconMapPin,
  IconCoin,
  IconBackpack,
  IconPlane,
  IconAlertCircle,
} from "@tabler/icons-react";
const SUGGESTION_CHIPS = [
  { icon: IconMapPin, text: "What should I visit in Pokhara for 5 days?" },
  { icon: IconCoin, text: "Estimate my budget for a trip to Chitwan" },
  { icon: IconBackpack, text: "What should I pack for a trek in Nepal?" },
  { icon: IconPlane, text: "Find me flights from Kathmandu to Pokhara" },
];

function formatTime(date) {
  return new Date(date).toLocaleTimeString("en-US", {
    // ← CHANGE: new Date(date) so strings work too
    hour: "numeric",
    minute: "2-digit",
  });
}

function generateId() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export default function Chat() {
  const { isAuthenticated, authHeaders } = useAuth();
  const { state, setState, updateState } = useAppState();

  // ← CHANGE: read messages & selectedTripId from context instead of local state
  const messages = state.chatMessages ?? [];
  const selectedTripId = state.chatSelectedTrip ?? null;
  const setMessages = (val) =>
    setState((prev) => ({
      ...prev,
      chatMessages:
        typeof val === "function" ? val(prev.chatMessages ?? []) : val,
    }));
  const setSelectedTripId = (val) => updateState({ chatSelectedTrip: val });

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [trips, setTrips] = useState([]);
  const [showClearConfirm, setShowClearConfirm] = useState(false);
  const textareaRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isAuthenticated) {
      fetchTrips();
    }
  }, [isAuthenticated]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const fetchTrips = async () => {
    try {
      const res = await api.get("/api/v1/trips", { headers: authHeaders });
      setTrips(res.data || []);
    } catch {
      // ignore
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const adjustTextareaHeight = () => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 160) + "px";
    }
  };

  const handleInputChange = (e) => {
    setInput(e.target.value);
    adjustTextareaHeight();
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const sendMessage = async (textToSend = input) => {
    if (!textToSend.trim() || isLoading) return;
    if (!isAuthenticated) return;

    const userMessage = {
      id: generateId(),
      role: "user",
      content: textToSend.trim(),
      timestamp: new Date().toISOString(), // ← CHANGE: ISO string survives JSON roundtrip
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
    setIsLoading(true);

    try {
      const response = await api.post(
        "/api/v1/chat",
        { message: textToSend.trim(), trip_id: selectedTripId },
        { headers: authHeaders },
      );
      const aiMessage = {
        id: generateId(),
        role: "ai",
        content: response.data.reply || "No response received.",
        timestamp: new Date().toISOString(), // ← CHANGE
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      const errorMessage = {
        id: generateId(),
        role: "ai",
        content: "Sorry, I couldn't process that. Please try again.",
        isError: true,
        timestamp: new Date().toISOString(), // ← CHANGE
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChipClick = (text) => {
    sendMessage(text);
  };

  const handleClear = () => {
    if (showClearConfirm) {
      setMessages([]);
      setShowClearConfirm(false);
    } else {
      setShowClearConfirm(true);
    }
  };

  const handleClearCancel = () => {
    setShowClearConfirm(false);
  };

  const renderMessageContent = (content, isError) => {
    return (
      <ReactMarkdown
        components={{
          p: ({ children }) => (
            <p style={{ margin: "0 0 8px", lineHeight: 1.6 }}>{children}</p>
          ),
          ul: ({ children }) => (
            <ul style={{ paddingLeft: 16, margin: "4px 0" }}>{children}</ul>
          ),
          ol: ({ children }) => (
            <ol style={{ paddingLeft: 16, margin: "4px 0" }}>{children}</ol>
          ),
          li: ({ children }) => <li style={{ marginBottom: 4 }}>{children}</li>,
          strong: ({ children }) => (
            <strong style={{ fontWeight: 500 }}>{children}</strong>
          ),
          code: ({ children }) => (
            <code
              style={{
                background: "#F3F4F6",
                padding: "1px 5px",
                borderRadius: 4,
                fontFamily: "monospace",
                fontSize: 13,
              }}
            >
              {children}
            </code>
          ),
          h1: ({ children }) => (
            <h1 style={{ fontSize: 18, fontWeight: 600, margin: "8px 0 4px" }}>
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 style={{ fontSize: 16, fontWeight: 600, margin: "6px 0 4px" }}>
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 style={{ fontSize: 14, fontWeight: 600, margin: "4px 0 2px" }}>
              {children}
            </h3>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  const renderMessages = () => {
    if (messages.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-full px-4">
          <div
            style={{
              width: 80,
              height: 80,
              borderRadius: "50%",
              background: "#EFF6FF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              marginBottom: 16,
            }}
          >
            <IconSparkles size={48} color="#2563EB" stroke={1.5} />
          </div>
          <p
            style={{
              fontSize: 20,
              fontWeight: 500,
              color: "#111827",
              marginBottom: 8,
            }}
          >
            How can I help you plan your trip?
          </p>
          <p
            style={{
              fontSize: 14,
              color: "#6B7280",
              maxWidth: 320,
              textAlign: "center",
              lineHeight: 1.5,
              marginBottom: 28,
            }}
          >
            Ask me anything about destinations, itineraries, budgets, packing
            lists, or travel tips.
          </p>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(2, 1fr)",
              gap: 10,
              maxWidth: 460,
            }}
          >
            {SUGGESTION_CHIPS.map((chip, i) => (
              <button
                key={i}
                onClick={() => handleChipClick(chip.text)}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  padding: "12px 16px",
                  background: "white",
                  border: "1px solid #E5E7EB",
                  borderRadius: 10,
                  fontSize: 13,
                  color: "#374151",
                  cursor: "pointer",
                  textAlign: "left",
                  transition: "all 150ms ease",
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = "#F9FAFB";
                  e.currentTarget.style.borderColor = "#2563EB";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = "white";
                  e.currentTarget.style.borderColor = "#E5E7EB";
                }}
              >
                <chip.icon size={16} color="#2563EB" stroke={1.5} />
                {chip.text}
              </button>
            ))}
          </div>
        </div>
      );
    }

    return messages.map((msg, index) => {
      const prevMsg = messages[index - 1];
      const isGroupedWithPrev =
        prevMsg &&
        prevMsg.role === msg.role &&
        new Date(msg.timestamp) - new Date(prevMsg.timestamp) < 60000; // ← CHANGE: parse strings
      const showTimestamp = !isGroupedWithPrev;

      if (msg.role === "user") {
        return (
          <div
            key={msg.id}
            style={{
              display: "flex",
              justifyContent: "flex-end",
              padding: "4px 24px",
              marginBottom: isGroupedWithPrev ? 2 : 4,
            }}
          >
            <div style={{ maxWidth: "70%" }}>
              <div
                style={{
                  background: "#2563EB",
                  color: "white",
                  borderRadius: isGroupedWithPrev
                    ? "18px 4px 4px 18px"
                    : "18px 18px 4px 18px",
                  padding: "10px 16px",
                  fontSize: 14,
                  lineHeight: 1.6,
                  display: "inline-block",
                }}
              >
                {msg.content}
              </div>
              {showTimestamp && (
                <div
                  style={{
                    fontSize: 11,
                    color: "#9CA3AF",
                    marginTop: 3,
                    textAlign: "right",
                  }}
                >
                  {formatTime(msg.timestamp)}
                </div>
              )}
            </div>
          </div>
        );
      }

      return (
        <div
          key={msg.id}
          style={{
            display: "flex",
            alignItems: "flex-start",
            gap: 10,
            padding: "4px 24px",
            marginBottom: isGroupedWithPrev ? 2 : 4,
          }}
        >
          {showTimestamp && (
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: "50%",
                background: "#EFF6FF",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
                marginTop: 2,
              }}
            >
              <IconSparkles size={16} color="#2563EB" stroke={1.5} />
            </div>
          )}
          <div style={{ maxWidth: "70%" }}>
            <div
              style={{
                background: msg.isError ? "#FEF2F2" : "white",
                color: msg.isError ? "#991B1B" : "#111827",
                border: msg.isError ? "1px solid #EF4444" : "1px solid #E5E7EB",
                borderRadius: isGroupedWithPrev
                  ? "4px 18px 18px 4px"
                  : "4px 18px 18px 18px",
                padding: "10px 16px",
                fontSize: 14,
                lineHeight: 1.6,
                display: "inline-block",
              }}
            >
              {msg.isError && (
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    marginBottom: 4,
                  }}
                >
                  <IconAlertCircle size={14} color="#EF4444" stroke={1.5} />
                  <span style={{ fontWeight: 500, fontSize: 13 }}>Error</span>
                </div>
              )}
              {renderMessageContent(msg.content, msg.isError)}
            </div>
            {showTimestamp && (
              <div
                style={{
                  fontSize: 11,
                  color: "#9CA3AF",
                  marginTop: 3,
                  display: "flex",
                  alignItems: "center",
                  gap: 4,
                }}
              >
                {msg.isError ? null : (
                  <span style={{ marginLeft: 42 }}>
                    {formatTime(msg.timestamp)}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      );
    });
  };

  const renderTypingIndicator = () => (
    <div
      style={{
        display: "flex",
        alignItems: "flex-start",
        gap: 10,
        padding: "4px 24px",
        marginBottom: 4,
      }}
    >
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: "50%",
          background: "#EFF6FF",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexShrink: 0,
          marginTop: 2,
        }}
      >
        <IconSparkles size={16} color="#2563EB" stroke={1.5} />
      </div>
      <div
        style={{
          background: "white",
          border: "1px solid #E5E7EB",
          borderRadius: "4px 18px 18px 18px",
          padding: "14px 20px",
          display: "flex",
          gap: 5,
          alignItems: "center",
        }}
      >
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: "#9CA3AF",
              animation: `bounce 1.2s infinite`,
              animationDelay: `${i * 0.15}s`,
            }}
          />
        ))}
      </div>
    </div>
  );

  const selectedTrip = trips.find((t) => t.id === selectedTripId);

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        height: "calc(100vh - 0px)",
        background: "#F9FAFB",
      }}
    >
      <style>{`
        @keyframes bounce {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-6px); }
        }
      `}</style>

      {/* Chat Header Bar */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 24px",
          background: "white",
          borderBottom: "1px solid #E5E7EB",
          flexShrink: 0,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 32,
              height: 32,
              borderRadius: "50%",
              background: "#EFF6FF",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <IconSparkles size={16} color="#2563EB" stroke={1.5} />
          </div>
          <span style={{ fontWeight: 500, fontSize: 15, color: "#111827" }}>
            AI Travel Assistant
          </span>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 5,
              marginLeft: 4,
            }}
          >
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: "#10B981",
              }}
            />
            <span style={{ fontSize: 12, color: "#6B7280" }}>Online</span>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 12, color: "#6B7280" }}>
              Trip context:
            </span>
            <select
              value={selectedTripId || ""}
              onChange={(e) => setSelectedTripId(e.target.value || null)}
              style={{
                background: "white",
                border: "1px solid #E5E7EB",
                borderRadius: 20,
                padding: "4px 12px",
                fontSize: 13,
                color: "#111827",
                cursor: "pointer",
                outline: "none",
              }}
            >
              <option value="">No trip selected</option>
              {trips.map((trip) => (
                <option key={trip.id} value={trip.id}>
                  {trip.destination || "Trip"} ({trip.start_date})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleClear}
            onBlur={handleClearCancel}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "6px 10px",
              background: "transparent",
              border: "none",
              borderRadius: 6,
              fontSize: 12,
              color: "#6B7280",
              cursor: "pointer",
              transition: "all 150ms ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = "#F3F4F6";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = "transparent";
            }}
          >
            <IconTrash size={14} stroke={1.5} />
            {showClearConfirm ? "Confirm?" : "Clear"}
          </button>

          {showClearConfirm && (
            <button
              onClick={handleClearCancel}
              style={{
                padding: "4px 8px",
                background: "transparent",
                border: "none",
                fontSize: 12,
                color: "#9CA3AF",
                cursor: "pointer",
              }}
            >
              Cancel
            </button>
          )}
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "24px 0",
          scrollBehavior: "smooth",
        }}
      >
        {renderMessages()}
        {isLoading && renderTypingIndicator()}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div
        style={{
          flexShrink: 0,
          borderTop: "1px solid #E5E7EB",
          background: "white",
          padding: "16px 24px 20px",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            gap: 10,
            background: "white",
            border: "1px solid #E5E7EB",
            borderRadius: 14,
            padding: "10px 14px",
            transition: "all 150ms ease",
          }}
          onFocus={() => {
            const el = document.querySelector(".chat-input-wrapper");
            if (el) {
              el.style.borderColor = "#2563EB";
              el.style.boxShadow = "0 0 0 3px rgba(37,99,235,0.08)";
            }
          }}
          onBlur={(e) => {
            const el = e.currentTarget;
            if (!el.contains(e.relatedTarget)) {
              el.style.borderColor = "#E5E7EB";
              el.style.boxShadow = "none";
            }
          }}
          className="chat-input-wrapper"
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask about destinations, itineraries, budgets..."
            rows={1}
            disabled={!isAuthenticated}
            style={{
              flex: 1,
              border: "none",
              outline: "none",
              resize: "none",
              fontSize: 14,
              color: "#111827",
              background: "transparent",
              fontFamily: "inherit",
              lineHeight: 1.6,
              minHeight: 24,
              maxHeight: 160,
              overflowY: "auto",
              padding: 0,
            }}
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || isLoading || !isAuthenticated}
            style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              background: !input.trim() || isLoading ? "#93C5FD" : "#2563EB",
              border: "none",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              cursor:
                !input.trim() || isLoading || !isAuthenticated
                  ? "not-allowed"
                  : "pointer",
              flexShrink: 0,
              transition: "all 150ms ease",
            }}
            onMouseEnter={(e) => {
              if (input.trim() && !isLoading && isAuthenticated) {
                e.currentTarget.style.background = "#1D4ED8";
              }
            }}
            onMouseLeave={(e) => {
              if (input.trim() && !isLoading && isAuthenticated) {
                e.currentTarget.style.background = "#2563EB";
              }
            }}
            onMouseDown={(e) => {
              if (input.trim() && !isLoading && isAuthenticated) {
                e.currentTarget.style.transform = "scale(0.95)";
              }
            }}
            onMouseUp={(e) => {
              e.currentTarget.style.transform = "scale(1)";
            }}
          >
            {isLoading ? (
              <div
                style={{
                  width: 16,
                  height: 16,
                  border: "2px solid white",
                  borderTopColor: "transparent",
                  borderRadius: "50%",
                  animation: "spin 0.8s linear infinite",
                }}
              />
            ) : (
              <IconArrowUp size={18} color="white" stroke={2} />
            )}
          </button>
        </div>

        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>

        <p
          style={{
            fontSize: 11,
            color: "#9CA3AF",
            textAlign: "center",
            marginTop: 8,
          }}
        >
          TravelPlanner AI can make mistakes. Verify important travel info.
        </p>
      </div>
    </div>
  );
}
