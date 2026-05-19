import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { api, getAuthHeaders } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import {
  IconBriefcase,
  IconCalendar,
  IconWorld,
  IconCoin,
  IconMapPin,
  IconPlus,
  IconSparkles,
  IconCalculator,
} from "@tabler/icons-react";

function SkeletonBlock({ width = "100%", height = "20px" }) {
  return <div className="skeleton" style={{ width, height }} />;
}

function StatCard({ icon: Icon, label, value, color, loading }) {
  return (
    <div className="card flex items-center gap-4">
      <div
        className="w-10 h-10 rounded-lg flex items-center justify-center"
        style={{ backgroundColor: `${color}15` }}
      >
        <Icon size={20} style={{ color }} stroke={1.5} />
      </div>
      <div>
        {loading ? (
          <>
            <SkeletonBlock width="60px" height="14px" />
            <SkeletonBlock width="40px" height="10px" />
          </>
        ) : (
          <>
            <p className="text-sm text-[var(--color-text-secondary)]">
              {label}
            </p>
            <p className="text-xl font-semibold text-[var(--color-text-primary)]">
              {value}
            </p>
          </>
        )}
      </div>
    </div>
  );
}

function getStatusBadge(status) {
  const statusMap = {
    planning: { label: "Planning", className: "badge-planning" },
    confirmed: { label: "Confirmed", className: "badge-confirmed" },
    completed: { label: "Completed", className: "badge-completed" },
    active: { label: "Active", className: "badge-active" },
  };
  const { label, className } = statusMap[status?.toLowerCase()] || {
    label: status || "Unknown",
    className: "badge-completed",
  };
  return <span className={`badge ${className}`}>{label}</span>;
}

function getDestinationColor(destination) {
  const colors = [
    "#2563EB",
    "#7C3AED",
    "#DB2777",
    "#DC2626",
    "#059669",
    "#0891B2",
  ];
  if (!destination) return colors[0];
  let hash = 0;
  for (let i = 0; i < destination.length; i++) {
    hash = destination.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

function TripCard({ trip }) {
  const color = getDestinationColor(trip.destination);
  return (
    <div className="card p-0 overflow-hidden flex-shrink-0 w-72">
      <div
        className="h-12 flex items-center justify-center"
        style={{ backgroundColor: color }}
      >
        <p className="text-sm font-medium text-white">
          {trip.destination || "Unknown"}
        </p>
      </div>
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-medium text-[var(--color-text-primary)]">
            {trip.origin} → {trip.destination}
          </h3>
          {getStatusBadge(trip.status)}
        </div>
        <p className="text-xs text-[var(--color-text-muted)]">
          {trip.start_date} — {trip.end_date}
        </p>
        {trip.budget && (
          <p className="text-xs text-[var(--color-text-secondary)] mt-1">
            Budget: {trip.budget}
          </p>
        )}
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { profile, isAuthenticated, authHeaders } = useAuth();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isAuthenticated) {
      fetchTrips();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated]);

  const fetchTrips = async () => {
    try {
      const response = await api.get("/api/v1/trips", {
        headers: getAuthHeaders(),
      });
      setTrips(response.data);
    } catch (error) {
      console.error("Failed to fetch trips:", error);
    } finally {
      setLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good morning";
    if (hour < 18) return "Good afternoon";
    return "Good evening";
  };

  const getUsername = () => {
    if (profile?.full_name) return profile.full_name.split(" ")[0];
    if (profile?.email) return profile.email.split("@")[0];
    return null;
  };

  // Calculate stats
  const totalTrips = trips.length;
  const today = new Date().toISOString().split("T")[0];
  const upcomingTrips = trips.filter((t) => t.start_date >= today).length;
  const uniqueCountries = new Set(
    trips.map((t) => t.destination).filter(Boolean),
  ).size;
  const totalBudget = trips.reduce(
    (sum, t) => sum + (Number(t.budget) || 0),
    0,
  );

  const sortedTrips = [...trips].sort((a, b) => {
    if (!a.start_date) return 1;
    if (!b.start_date) return -1;
    return new Date(a.start_date) - new Date(b.start_date);
  });

  const username = getUsername();

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-[var(--color-text-primary)]">
          {getGreeting()}
          {username ? `, ${username}` : ""} 👋
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-1">
          Here's your travel overview
        </p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          icon={IconBriefcase}
          label="Total Trips"
          value={totalTrips}
          color="#2563EB"
          loading={loading}
        />
        <StatCard
          icon={IconCalendar}
          label="Upcoming"
          value={upcomingTrips}
          color="#10B981"
          loading={loading}
        />
        <StatCard
          icon={IconWorld}
          label="Destinations"
          value={uniqueCountries}
          color="#7C3AED"
          loading={loading}
        />
        <StatCard
          icon={IconCoin}
          label="Budget Spent"
          value={
            totalBudget > 0 ? `Rs ${totalBudget.toLocaleString()}` : "Rs 0"
          }
          color="#F59E0B"
          loading={loading}
        />
      </div>

      {/* Upcoming Trips */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-medium text-[var(--color-text-primary)]">
            Upcoming trips
          </h2>
          <Link
            to="/trips"
            className="text-sm text-[var(--color-primary)] hover:underline"
          >
            View all →
          </Link>
        </div>

        {loading ? (
          <div className="flex gap-4 overflow-hidden">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="card p-0 overflow-hidden flex-shrink-0 w-72"
              >
                <div className="h-12 skeleton" />
                <div className="p-4 space-y-2">
                  <SkeletonBlock width="80%" height="16px" />
                  <SkeletonBlock width="60%" height="12px" />
                </div>
              </div>
            ))}
          </div>
        ) : sortedTrips.length === 0 ? (
          <div className="card text-center py-12">
            <IconMapPin
              size={48}
              stroke={1.5}
              className="mx-auto text-[var(--color-text-muted)] mb-3"
            />
            <h3 className="text-lg font-medium text-[var(--color-text-primary)] mb-1">
              No trips yet
            </h3>
            <p className="text-sm text-[var(--color-text-secondary)] mb-4">
              Start planning your first adventure
            </p>
            <Link to="/trips" className="btn btn-primary inline-flex">
              <IconPlus size={18} />
              Plan a trip
            </Link>
          </div>
        ) : (
          <div className="flex gap-4 overflow-x-auto pb-2 -mx-2 px-2">
            {sortedTrips.slice(0, 5).map((trip) => (
              <TripCard key={trip.id} trip={trip} />
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-3">
        <Link to="/trips" className="btn btn-primary">
          <IconPlus size={18} />
          Plan New Trip
        </Link>
        <Link to="/ai" className="btn btn-secondary">
          <IconSparkles size={18} />
          Generate AI Itinerary
        </Link>
        <Link to="/budget" className="btn btn-secondary">
          <IconCalculator size={18} />
          Estimate Budget
        </Link>
      </div>
    </div>
  );
}
