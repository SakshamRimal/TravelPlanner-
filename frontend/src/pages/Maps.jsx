import { useState, useEffect, useRef, useCallback } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { api, getAuthHeaders } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { showToast } from "../components/Toast";
import {
  IconSearch,
  IconMapPin,
  IconMap2,
  IconStar,
  IconMapSearch,
} from "@tabler/icons-react";

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

const QUICK_SEARCHES = [
  "Restaurants",
  "Hotels",
  "ATMs",
  "Hospitals",
  "Temples",
];

const COLORS = [
  "#3B82F6",
  "#10B981",
  "#F59E0B",
  "#EF4444",
  "#8B5CF6",
  "#EC4899",
  "#06B6D4",
  "#84CC16",
  "#F97316",
  "#6366F1",
];

function MapUpdater({ center, zoom = 13 }) {
  const map = useMap();
  const isInitialized = useRef(false);

  useEffect(() => {
    if (map && center && center[0] && center[1]) {
      map.setView(center, zoom, { animate: true });
      isInitialized.current = true;
    }
  }, [center, zoom, map]);

  return null;
}

function MapController({ results }) {
  const map = useMap();

  useEffect(() => {
    if (results && results.length > 0) {
      const validResults = results.filter((r) => r.lat && r.lng);
      if (validResults.length > 0) {
        const bounds = L.latLngBounds(validResults.map((r) => [r.lat, r.lng]));
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
      }
    }
  }, [results, map]);

  return null;
}

function MapsSkeleton() {
  return (
    <div className="results-list">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="result-item">
          <div
            className="skeleton"
            style={{ width: 40, height: 40, borderRadius: "50%" }}
          />
          <div style={{ flex: 1 }}>
            <div
              className="skeleton"
              style={{ height: 14, width: "70%", marginBottom: 6 }}
            />
            <div className="skeleton" style={{ height: 12, width: "50%" }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function Maps() {
  const { isAuthenticated } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [center, setCenter] = useState([27.7172, 85.324]);
  const [zoom, setZoom] = useState(13);
  const [loading, setLoading] = useState(false);
  const [searchedQuery, setSearchedQuery] = useState("");
  const [selectedIdx, setSelectedIdx] = useState(null);
  const [count, setCount] = useState(0);
  const mapKey = useRef(0);

  const NEPAL_LOCATIONS = {
    pokhara: { lat: 28.2096, lng: 83.9856, address: "Pokhara, Nepal" },
    kathmandu: { lat: 27.7172, lng: 85.324, address: "Kathmandu, Nepal" },
    chitwan: { lat: 27.5291, lng: 84.3542, address: "Chitwan, Nepal" },
    lukla: { lat: 27.6887, lng: 86.7314, address: "Lukla, Nepal" },
    nagarkot: { lat: 27.7156, lng: 85.5206, address: "Nagarkot, Nepal" },
    bhaktapur: { lat: 27.6727, lng: 85.4298, address: "Bhaktapur, Nepal" },
  };

  const handleSearch = async (e, searchQuery) => {
    e?.preventDefault();
    if (!searchQuery) return;
    if (!isAuthenticated) {
      showToast("Please sign in first", "error");
      return;
    }
    setLoading(true);
    setSelectedIdx(null);
    try {
      // Check for known Nepal locations
      const key = searchQuery.trim().toLowerCase();
      if (NEPAL_LOCATIONS[key]) {
        const loc = NEPAL_LOCATIONS[key];
        setResults([
          {
            title: key.charAt(0).toUpperCase() + key.slice(1),
            lat: loc.lat,
            lng: loc.lng,
            address: loc.address,
            category: "City",
          },
        ]);
        setCount(1);
        setSearchedQuery(key.charAt(0).toUpperCase() + key.slice(1));
        setCenter([loc.lat, loc.lng]);
        setZoom(13);
        mapKey.current += 1;
        setLoading(false);
        return;
      }
      const response = await api.get("/api/v1/maps/search", {
        headers: getAuthHeaders(),
        params: { q: searchQuery },
      });
      const items = response.data?.results || [];
      // Nepal bounding box: lat 26.347–30.447, lng 80.058–88.201
      const isInNepal = (lat, lng) =>
        lat >= 26.347 && lat <= 30.447 && lng >= 80.058 && lng <= 88.201;
      const filtered = items.filter(
        (i) => i.lat && i.lng && isInNepal(i.lat, i.lng),
      );
      setResults(filtered);
      setCount(filtered.length);
      setSearchedQuery(searchQuery);

      if (filtered.length > 0) {
        setCenter([filtered[0].lat, filtered[0].lng]);
        mapKey.current += 1;
      }
    } catch {
      showToast("Search failed. Please try again.", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleQuickSearch = (q) => {
    setQuery(q);
    handleSearch(null, q);
  };

  const handleResultClick = (item, idx) => {
    setSelectedIdx(idx);
    if (item.lat && item.lng) {
      setCenter([item.lat, item.lng]);
      setZoom(15);
      mapKey.current += 1;
    }
  };

  const filteredResults = results.filter((r) => r.lat && r.lng);

  return (
    <div className="page">
      <div className="page-header">
        <h1>Maps</h1>
      </div>

      <form onSubmit={(e) => handleSearch(e, query)} className="card maps-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search for places..."
          className="search-input"
          required
        />
        <button type="submit" disabled={loading} className="btn btn-primary">
          <IconSearch size={18} />
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      <div className="maps-layout">
        <div className="map-panel">
          {searchedQuery && (
            <div className="map-search-pill">
              Showing results for: <strong>{searchedQuery}</strong>
            </div>
          )}
          <div className="map-container">
            <MapContainer
              key={mapKey.current}
              center={center}
              zoom={zoom}
              scrollWheelZoom
              className="leaflet-map"
              style={{ height: "100%", width: "100%" }}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MapUpdater center={center} zoom={zoom} />
              {filteredResults.length > 0 && (
                <MapController results={filteredResults} />
              )}
              {filteredResults.map((item, idx) => (
                <Marker
                  key={`marker-${idx}`}
                  position={[item.lat, item.lng]}
                  eventHandlers={{
                    click: () => setSelectedIdx(idx),
                  }}
                >
                  <Popup>
                    <div className="map-popup">
                      <strong>{item.title}</strong>
                      <p>{item.address || item.snippet}</p>
                    </div>
                  </Popup>
                </Marker>
              ))}
            </MapContainer>
          </div>
        </div>

        <div className="results-panel">
          {loading ? (
            <MapsSkeleton />
          ) : results.length > 0 ? (
            <>
              <div className="results-header">
                {count} places found
                {searchedQuery && <span> in {searchedQuery}</span>}
                <span className="coords-info">
                  {filteredResults.length} with coordinates
                </span>
              </div>
              <div className="results-list">
                {results.map((item, idx) => {
                  const isSelected = selectedIdx === idx;
                  const color = COLORS[idx % COLORS.length];
                  const initial = item.title?.charAt(0)?.toUpperCase() || "P";
                  const category = item.category || item.type || "";
                  return (
                    <div
                      key={idx}
                      className={`result-item ${isSelected ? "result-item-selected" : ""}`}
                      onClick={() => handleResultClick(item, idx)}
                    >
                      <div
                        className="result-avatar"
                        style={{ backgroundColor: color }}
                      >
                        {initial}
                      </div>
                      <div className="result-info">
                        <div className="result-name">{item.title}</div>
                        <div className="result-category">
                          {category && <span>{category}</span>}
                          {item.distance && <span> · {item.distance}</span>}
                        </div>
                        {item.rating && (
                          <div className="result-rating">
                            {[...Array(5)].map((_, i) => (
                              <IconStar
                                key={i}
                                size={10}
                                fill={
                                  i < Math.round(item.rating)
                                    ? "#F59E0B"
                                    : "none"
                                }
                                color="#F59E0B"
                              />
                            ))}
                            <span>({item.rating})</span>
                          </div>
                        )}
                      </div>
                      <button
                        className="btn-map-pin"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleResultClick(item, idx);
                        }}
                        title="Show on map"
                      >
                        <IconMapPin size={16} />
                      </button>
                    </div>
                  );
                })}
              </div>
            </>
          ) : searchedQuery ? (
            <div className="empty-state">
              <IconMap2 size={40} stroke={1} />
              <h3>No places found</h3>
              <p>Try a different search term.</p>
            </div>
          ) : (
            <div className="idle-results">
              <div className="idle-results-icon">
                <IconMapSearch size={40} stroke={1} />
              </div>
              <div className="idle-results-title">Search for places</div>
              <div className="idle-results-sub">
                Try: restaurants, hotels, temples, cafes
              </div>
              <div className="quick-search-chips">
                {QUICK_SEARCHES.map((q) => (
                  <button
                    key={q}
                    className="popular-chip"
                    onClick={() => handleQuickSearch(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
