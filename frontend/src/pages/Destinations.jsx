import { useState } from "react";
import { api, getAuthHeaders } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { showToast } from "../components/Toast";
import { IconSearch, IconMap2, IconHeart } from "@tabler/icons-react";

const POPULAR_DESTINATIONS = [
  { name: "Kathmandu", country: "Nepal", emoji: "🏔️" },
  { name: "Pokhara", country: "Nepal", emoji: "🏞️" },
  { name: "Chitwan", country: "Nepal", emoji: "🦏" },
  { name: "Lukla", country: "Nepal", emoji: "✈️" },
  { name: "Nagarkot", country: "Nepal", emoji: "🌅" },
  { name: "Bhaktapur", country: "Nepal", emoji: "🛕" },
];

const COLORS = [
  "#3B82F6",
  "#10B981",
  "#F59E0B",
  "#EF4444",
  "#8B5CF6",
  "#EC4899",
];

function DestinationSkeleton() {
  return (
    <div className="destinations-grid">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div key={i} className="destination-card destination-card-skeleton">
          <div className="destination-band skeleton" />
          <div style={{ padding: 14 }}>
            <div
              className="skeleton"
              style={{ height: 14, width: "70%", marginBottom: 8 }}
            />
            <div
              className="skeleton"
              style={{ height: 12, width: "90%", marginBottom: 8 }}
            />
            <div className="skeleton" style={{ height: 12, width: "50%" }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function Destinations() {
  const { isAuthenticated } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (searchQuery) => {
    if (!searchQuery) return;
    if (!isAuthenticated) {
      showToast("Please sign in first", "error");
      return;
    }
    setLoading(true);
    try {
      const response = await api.get("/api/v1/destinations/search", {
        headers: getAuthHeaders(),
        params: { query: searchQuery },
      });
      setResults(response.data);
    } catch {
      showToast("Search failed. Please try again.", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSearch(query);
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Destinations</h1>
      </div>

      <form onSubmit={handleSubmit} className="card search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for a destination..."
          className="search-input"
          required
        />
        <button type="submit" disabled={loading} className="btn btn-primary">
          <IconSearch size={18} />
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {loading ? (
        <DestinationSkeleton />
      ) : results ? (
        results.length > 0 ? (
          <div className="destinations-grid">
            {results.map((dest, idx) => (
              <div key={idx} className="destination-card">
                <div
                  className="destination-band"
                  style={{ backgroundColor: COLORS[idx % COLORS.length] }}
                >
                  {dest.name}
                </div>
                <div className="destination-body">
                  <p className="destination-desc">
                    {dest.description ||
                      `Discover ${dest.name}, a beautiful destination.`}
                  </p>
                  {dest.tags && dest.tags.length > 0 && (
                    <div className="destination-tags">
                      {dest.tags.slice(0, 3).map((tag, i) => (
                        <span key={i} className="tag-pill">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  <div className="destination-footer">
                    <button className="btn-favorite">
                      <IconHeart size={16} />
                    </button>
                    <a
                      href={dest.url || "#"}
                      className="explore-link"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      Explore →
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            <IconMap2 size={40} stroke={1} />
            <h3>No destinations found for "{query}"</h3>
            <p>Try searching for a country, city, or type of destination.</p>
          </div>
        )
      ) : (
        <div className="idle-section">
          <div className="idle-title">Popular destinations</div>
          <div className="popular-grid">
            {POPULAR_DESTINATIONS.map((dest) => (
              <button
                key={dest.name}
                className="popular-chip"
                onClick={() => {
                  setQuery(dest.name);
                  handleSearch(dest.name);
                }}
              >
                <span className="popular-emoji">{dest.emoji}</span>
                <span className="popular-name">{dest.name}</span>
                <span className="popular-country">{dest.country}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
