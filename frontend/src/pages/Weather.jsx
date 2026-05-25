import { useEffect, useState } from "react";
import { api, getAuthHeaders } from "../lib/api";
import { showToast } from "../components/Toast";
import {
  IconCloud,
  IconDroplet,
  IconWind,
  IconEye,
  IconGauge,
  IconSun,
  IconCloudRain,
  IconSnowflake,
  IconStorm,
  IconInfoCircle,
} from "@tabler/icons-react";

const QUICK_DESTINATIONS = ["Kathmandu", "Pokhara", "Chitwan"];

const ICON_MAP = {
  clear: IconSun,
  sunny: IconSun,
  "partly cloudy": IconCloud,
  cloudy: IconCloud,
  overcast: IconCloud,
  rain: IconCloudRain,
  drizzle: IconCloudRain,
  shower: IconCloudRain,
  snow: IconSnowflake,
  storm: IconStorm,
  thunderstorm: IconStorm,
};

function getWeatherIcon(condition) {
  const key = (condition || "").toLowerCase();
  for (const [k, Icon] of Object.entries(ICON_MAP)) {
    if (key.includes(k)) return Icon;
  }
  return IconCloud;
}

function getWeatherColor(icon) {
  if (icon === IconSun) return "#F59E0B";
  if (icon === IconCloudRain) return "#3B82F6";
  if (icon === IconSnowflake) return "#93C5FD";
  if (icon === IconStorm) return "#6B7280";
  return "#9CA3AF";
}

function formatDay(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", { weekday: "short" });
}

function WeatherSkeleton() {
  return (
    <div className="weather-results">
      <div className="weather-main-skeleton">
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <div>
            <div
              className="skeleton"
              style={{ height: 28, width: 160, marginBottom: 8 }}
            />
            <div
              className="skeleton"
              style={{ height: 14, width: 100, marginBottom: 16 }}
            />
            <div className="skeleton" style={{ height: 64, width: 100 }} />
          </div>
          <div className="skeleton" style={{ width: 64, height: 64 }} />
        </div>
        <div
          className="skeleton"
          style={{ height: 40, width: "100%", marginTop: 20 }}
        />
      </div>
      <div className="forecast-row">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="forecast-card">
            <div
              className="skeleton"
              style={{ height: 14, width: 32, marginBottom: 8 }}
            />
            <div
              className="skeleton"
              style={{ width: 28, height: 28, marginBottom: 8 }}
            />
            <div
              className="skeleton"
              style={{ height: 16, width: 28, marginBottom: 4 }}
            />
            <div className="skeleton" style={{ height: 12, width: 24 }} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Weather() {
  const [destination, setDestination] = useState("Kathmandu");
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchWeather = async (nextDestination) => {
    setLoading(true);
    try {
      const response = await api.get("/api/v1/weather", {
        headers: getAuthHeaders(),
        params: { destination: nextDestination },
      });
      setReport(response.data);
    } catch {
      setReport(null);
      showToast("Failed to fetch weather", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await fetchWeather(destination);
  };

  useEffect(() => {
    fetchWeather(destination);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const WeatherIcon = report ? getWeatherIcon(report.condition) : IconCloud;
  const iconColor = getWeatherColor(WeatherIcon);

  // Parse forecast if available
  const forecast = report?.forecast || [];

  return (
    <div className="page">
      <div className="page-header">
        <h1>Weather</h1>
      </div>

      <form onSubmit={handleSubmit} className="card weather-form">
        <div className="weather-form-row">
          <input
            type="text"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            placeholder="e.g., Kathmandu, Pokhara"
            className="input"
            required
          />
          <button type="submit" disabled={loading} className="btn btn-primary">
            <IconCloud size={18} />
            {loading ? "Loading..." : "Get Weather"}
          </button>
        </div>
      </form>

      {loading ? (
        <WeatherSkeleton />
      ) : report ? (
        <div className="weather-results">
          <div className="weather-main card">
            <div className="weather-main-grid">
              <div className="weather-info">
                <div className="weather-city">{report.city || destination}</div>
                {report.country && (
                  <div className="weather-country">{report.country}</div>
                )}
                <div className="weather-date">
                  {new Date().toLocaleDateString("en-US", {
                    weekday: "long",
                    month: "long",
                    day: "numeric",
                  })}
                </div>
                <div className="weather-temp">
                  {report.temperature ?? "--"}°C
                </div>
                <div className="weather-feels">
                  Feels like {report.feels_like ?? "--"}°C
                </div>
                <div className="weather-condition">
                  {report.condition || "Unknown"}
                </div>
              </div>
              <div className="weather-icon-wrap">
                <WeatherIcon size={64} color={iconColor} />
              </div>
            </div>
            <div className="weather-stats">
              <div className="weather-stat">
                <IconDroplet size={16} />
                <span>Humidity:</span>
                <strong>{report.humidity ?? "--"}%</strong>
              </div>
              <div className="weather-stat">
                <IconWind size={16} />
                <span>Wind:</span>
                <strong>{report.wind_speed ?? "--"} km/h</strong>
              </div>
              <div className="weather-stat">
                <IconEye size={16} />
                <span>Visibility:</span>
                <strong>{report.visibility ?? "--"} km</strong>
              </div>
              <div className="weather-stat">
                <IconGauge size={16} />
                <span>Pressure:</span>
                <strong>{report.pressure ?? "--"} hPa</strong>
              </div>
            </div>
          </div>

          {forecast.length > 0 && (
            <>
              <div className="forecast-title">5-day forecast</div>
              <div className="forecast-row">
                {forecast.slice(0, 5).map((day, i) => {
                  const DayIcon = getWeatherIcon(day.condition);
                  return (
                    <div key={i} className="forecast-card">
                      <div className="forecast-day">{formatDay(day.date)}</div>
                      <DayIcon size={24} color={iconColor} />
                      <div className="forecast-high">{day.high ?? "--"}°</div>
                      <div className="forecast-low">{day.low ?? "--"}°</div>
                    </div>
                  );
                })}
              </div>
            </>
          )}

          {report.high && report.low && (
            <div className="weather-tip">
              <IconInfoCircle size={18} color="var(--color-primary)" />
              <span>
                Pack light layers — temperatures vary between {report.low}°C and{" "}
                {report.high}°C this week.
              </span>
            </div>
          )}
        </div>
      ) : (
        <div className="weather-quick">
          <div className="idle-title">Popular destinations</div>
          <div className="quick-chips">
            {QUICK_DESTINATIONS.map((dest) => (
              <button
                key={dest}
                className="popular-chip"
                onClick={() => {
                  setDestination(dest);
                }}
              >
                {dest}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
