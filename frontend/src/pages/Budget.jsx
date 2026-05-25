import { useState } from "react";
import { api, getAuthHeaders } from "../lib/api";
import { useAuth } from "../context/AuthContext";
import { useAppState } from "../context/AppStateContext";
import { showToast } from "../components/Toast";
import {
  IconCalculator,
  IconUser,
  IconCalendar,
  IconUsers,
  IconPlane,
  IconBuilding,
  IconCoins,
  IconToolsKitchen2,
  IconRoute,
  IconPackage,
  IconAlertCircle,
} from "@tabler/icons-react";

const CATEGORIES = [
  { key: "flights", label: "Flights", icon: IconPlane },
  { key: "accommodation", label: "Accommodation", icon: IconBuilding },
  { key: "food", label: "Food", icon: IconToolsKitchen2 },
  { key: "activities", label: "Activities", icon: IconRoute },
  { key: "other", label: "Other", icon: IconPackage },
];

// ─── Skeleton ────────────────────────────────────────────────────────────────

function BudgetSkeleton() {
  return (
    <div className="budget-results">
      <div className="budget-summary-skeleton">
        <div
          className="skeleton"
          style={{ height: 16, width: 120, marginBottom: 16 }}
        />
        <div
          className="skeleton"
          style={{ height: 40, width: 180, marginBottom: 12 }}
        />
        <div
          className="skeleton"
          style={{ height: 16, width: 100, marginBottom: 24 }}
        />
        <div
          style={{ borderTop: "1px solid var(--color-border)", paddingTop: 20 }}
        >
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: 12,
              }}
            >
              <div className="skeleton" style={{ height: 14, width: 80 }} />
              <div className="skeleton" style={{ height: 14, width: 60 }} />
            </div>
          ))}
        </div>
      </div>
      <div className="budget-breakdown-skeleton">
        <div
          className="skeleton"
          style={{ height: 18, width: 120, marginBottom: 20 }}
        />
        {CATEGORIES.map((cat) => (
          <div key={cat.key} style={{ marginBottom: 20 }}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                marginBottom: 8,
              }}
            >
              <div className="skeleton" style={{ height: 14, width: 100 }} />
              <div className="skeleton" style={{ height: 14, width: 60 }} />
            </div>
            <div
              className="skeleton"
              style={{ height: 6, width: "100%", borderRadius: 4 }}
            />
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatCurrency(amount) {
  if (!amount) return "NPR 0";
  return `NPR ${Number(amount).toLocaleString()}`;
}

// ─── Component ───────────────────────────────────────────────────────────────

export default function Budget() {
  const { isAuthenticated, accessToken } = useAuth();

  // ✅ Read persisted state from context instead of local useState
  const { state, updateState } = useAppState();
  const form = state.budgetForm ?? {
    destination: "Pokhara",
    days: 3,
    travelers: 1,
  };
  const result = state.budgetResult ?? null;
  const currency = "NPR";

  // Local-only: loading spinner doesn't need to survive navigation
  const [loading, setLoading] = useState(false);

  // Thin setters that write back to context (and therefore localStorage)
  const setForm = (val) => updateState({ budgetForm: val });
  const setResult = (val) => updateState({ budgetResult: val });

  // ─── Submit ───────────────────────────────────────────────────────────────

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      showToast("Please sign in first", "error");
      return;
    }
    setLoading(true);
    try {
      const response = await api.get("/api/v1/budget/estimate", {
        headers: getAuthHeaders(accessToken),
        params: {
          destination: form.destination,
          days: Number(form.days),
          travelers: Number(form.travelers),
        },
      });
      setResult(response.data);
    } catch {
      showToast("Could not estimate budget. Please try again.", "error");
    } finally {
      setLoading(false);
    }
  };

  // ─── Derived values ───────────────────────────────────────────────────────

  const total = result?.total_estimate ?? result?.total ?? 0;
  const perPerson =
    form.travelers > 0 ? Math.round(total / form.travelers) : total;
  const perDay = form.days > 0 ? Math.round(total / form.days) : total;

  const getCategoryAmount = (key) => result?.breakdown?.[key] ?? 0;

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Budget Estimator</h1>
          <p>Estimate costs for your trip.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="budget-form card">
        <div className="budget-form-row">
          <div className="form-group">
            <label className="form-label">Destination</label>
            <input
              type="text"
              value={form.destination}
              onChange={(e) =>
                setForm({ ...form, destination: e.target.value })
              }
              className="input"
              placeholder="e.g. Paris, Tokyo"
              required
            />
          </div>
          <div className="form-group form-group-sm">
            <label className="form-label">Days</label>
            <input
              type="number"
              min="1"
              value={form.days}
              onChange={(e) => setForm({ ...form, days: e.target.value })}
              className="input"
            />
          </div>
          <div className="form-group form-group-sm">
            <label className="form-label">Travelers</label>
            <input
              type="number"
              min="1"
              value={form.travelers}
              onChange={(e) => setForm({ ...form, travelers: e.target.value })}
              className="input"
            />
          </div>
          <button type="submit" disabled={loading} className="btn btn-primary">
            <IconCalculator size={18} />
            {loading ? "Estimating..." : "Estimate"}
          </button>
        </div>
      </form>

      {loading ? (
        <BudgetSkeleton />
      ) : result ? (
        <div className="budget-results">
          <div className="budget-summary card">
            <div className="budget-total-label">Estimated Total</div>
            <div className="budget-total">
              {formatCurrency(total, currency)}
            </div>
            {result.converted_usd && currency === "USD" && (
              <div className="budget-usd">
                ≈ NPR {result.total.toLocaleString()}
              </div>
            )}
            {result.converted_npr && currency === "NPR" && (
              <div className="budget-usd">≈ ${result.converted_npr} USD</div>
            )}
            <div className="budget-divider" />
            <div className="budget-stat-row">
              <span>
                <IconUser size={16} /> Per person
              </span>
              <strong>{formatCurrency(perPerson, currency)}</strong>
            </div>
            <div className="budget-stat-row">
              <span>
                <IconCalendar size={16} /> Per day
              </span>
              <strong>{formatCurrency(perDay, currency)}</strong>
            </div>
            <div className="budget-stat-row">
              <span>
                <IconUsers size={16} />
                {form.travelers} traveler
                {Number(form.travelers) !== 1 ? "s" : ""}
              </span>
              <strong>{form.days} days</strong>
            </div>
          </div>

          <div className="budget-breakdown card">
            <div className="budget-breakdown-title">Cost breakdown</div>
            {CATEGORIES.map((cat) => {
              const amount = getCategoryAmount(cat.key);
              const pct = total > 0 ? (amount / total) * 100 : 0;
              return (
                <div key={cat.key} className="breakdown-row">
                  <div className="breakdown-header">
                    <span className="breakdown-label">
                      <cat.icon size={16} />
                      {cat.label}
                    </span>
                    <span className="breakdown-amount">
                      {formatCurrency(amount, currency)}
                    </span>
                  </div>
                  <div className="breakdown-bar-bg">
                    <div
                      className="breakdown-bar-fill"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <IconCalculator size={48} stroke={1} />
          <h3>Estimate your travel budget</h3>
          <p>Enter destination, days, and travelers to get a cost estimate.</p>
        </div>
      )}

      {result?.error && (
        <div className="error-card">
          <IconAlertCircle size={20} />
          <span>{result.error}</span>
        </div>
      )}
    </div>
  );
}
