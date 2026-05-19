import { useState } from 'react';
import { api, getAuthHeaders } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { showToast } from '../components/Toast';
import { IconPlane, IconBedFilled, IconRoute, IconMapPin, IconStar, IconCompass, IconClock, IconUsers } from '@tabler/icons-react';

const TABS = [
  { key: 'flights', label: 'Flights', icon: IconPlane },
  { key: 'hotels', label: 'Hotels', icon: IconBedFilled },
  { key: 'activities', label: 'Activities', icon: IconCompass },
];

const formatPrice = (price) => {
  if (!price && price !== 0) return 'Price on request';
  return `NPR ${price.toLocaleString()}`;
};

function FlightCard({ flight }) {
  const isDirect = flight.stops === 0;
  const isLoading = flight.stops === undefined || flight.stops === -1;

  return (
    <div className="rec-card">
      <div className="rec-card-header">
        <div className="rec-airline">
          <div className="airline-logo">
            {flight.carrier?.charAt(0) || 'F'}
          </div>
          <span>{flight.carrier || 'Airline'}</span>
        </div>
        {!isLoading && (
          <div className="rec-price">{formatPrice(flight.price)}</div>
        )}
      </div>
      <div className="rec-route">
        <span className="route-origin">{flight.departure_airport || '---'}</span>
        <div className="route-arrow">
          <IconPlane size={14} />
        </div>
        <span className="route-dest">{flight.arrival_airport || '---'}</span>
      </div>
      <div className="rec-meta">
        {flight.duration && <span className="rec-duration"><IconClock size={12} /> {flight.duration}</span>}
        {!isLoading && (
          isDirect ? (
            <span className="rec-badge rec-badge-green">Direct</span>
          ) : (
            <span className="rec-badge rec-badge-amber">{flight.stops} stop{flight.stops > 1 ? 's' : ''}</span>
          )
        )}
        {flight.flight_number && <span className="rec-flight-num">{flight.flight_number}</span>}
      </div>
      <div className="rec-times">
        <span>Dep: {flight.departure_time || '--:--'}</span>
        <span>Arr: {flight.arrival_time || '--:--'}</span>
      </div>
      {flight.note && (
        <div className="rec-note">{flight.note}</div>
      )}
      <button className="btn btn-secondary rec-book-btn">View Details</button>
    </div>
  );
}

function HotelCard({ hotel }) {
  const stars = Array.from({ length: Math.round(hotel.rating || 3) }, (_, i) => (
    <IconStar key={i} size={12} fill="#F59E0B" color="#F59E0B" />
  ));

  return (
    <div className="rec-card">
      <div className="rec-card-header">
        <div className="rec-hotel-name">{hotel.name || 'Hotel'}</div>
      </div>
      <div className="rec-stars-row">
        <div className="rec-stars">{stars}</div>
        {hotel.reviews && <span className="rec-review-count">({hotel.reviews} reviews)</span>}
      </div>
      <div className="rec-location">
        <IconMapPin size={14} />
        {hotel.address || hotel.location || 'Location'}
      </div>
      {hotel.amenities && hotel.amenities.length > 0 && (
        <div className="rec-amenities">
          {hotel.amenities.slice(0, 4).map((amenity, i) => (
            <span key={i} className="rec-amenity-tag">{amenity}</span>
          ))}
        </div>
      )}
      <div className="rec-price-row">
        <div className="rec-price">{formatPrice(hotel.price_per_night)}</div>
        <span className="rec-price-unit">/ night</span>
      </div>
      <button className="btn btn-secondary rec-book-btn">View Hotel</button>
    </div>
  );
}

function ActivityCard({ activity }) {
  return (
    <div className="rec-card">
      <div className="rec-activity-header">
        <div className="rec-activity-name">{activity.name || 'Activity'}</div>
        {activity.type && (
          <span className="rec-badge">{activity.type}</span>
        )}
      </div>
      <p className="rec-desc">
        {activity.description || 'Experience this amazing activity.'}
      </p>
      <div className="rec-activity-meta">
        {activity.duration && (
          <span className="rec-activity-duration"><IconClock size={12} /> {activity.duration}</span>
        )}
        {activity.rating && (
          <span className="rec-activity-rating">
            <IconStar size={12} fill="#F59E0B" color="#F59E0B" /> {activity.rating}
            {activity.reviews && <span className="rec-review-inline"> ({activity.reviews})</span>}
          </span>
        )}
      </div>
      <div className="rec-activity-cost">
        <span className="rec-price">{formatPrice(activity.estimated_cost)}</span>
      </div>
      <button className="btn btn-secondary rec-book-btn">Add to Trip</button>
    </div>
  );
}

function EmptyTabMessage({ tab, message }) {
  return (
    <div className="empty-tab-message">
      <IconCompass size={32} stroke={1} />
      <p>{message || `No ${tab} available for this destination.`}</p>
    </div>
  );
}

function RecommendationsSkeleton() {
  return (
    <div className="recommendations-tabs">
      <div className="rec-grid">
        {[1, 2, 3].map((i) => (
          <div key={i} className="rec-card rec-card-skeleton">
            <div className="skeleton" style={{ height: 20, width: '60%', marginBottom: 12 }} />
            <div className="skeleton" style={{ height: 16, width: '80%', marginBottom: 8 }} />
            <div className="skeleton" style={{ height: 16, width: '40%', marginBottom: 16 }} />
            <div className="skeleton" style={{ height: 40, width: '100%', marginTop: 12 }} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function Recommendations() {
  const { isAuthenticated } = useAuth();
  const [form, setForm] = useState({
    destination: 'Pokhara',
    origin: 'Kathmandu',
    budget: '',
    travel_date: '',
    travelers: 1,
  });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('flights');
  const [searchedDestination, setSearchedDestination] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      showToast('Please sign in first', 'error');
      return;
    }
    setLoading(true);
    setResults(null);
    try {
      const response = await api.get(`/api/v1/recommendations/${form.destination}`, {
        headers: getAuthHeaders(),
        params: {
          origin: form.origin,
          budget: form.budget ? Number(form.budget) : undefined,
        },
      });
      setResults(response.data);
      setSearchedDestination(form.destination);
    } catch (err) {
      showToast('Failed to fetch recommendations', 'error');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getTabData = (tab) => {
    if (!results) return [];
    if (tab === 'flights') return results.flights || [];
    if (tab === 'hotels') return results.hotels || [];
    if (tab === 'activities') return results.activities || [];
    return [];
  };

  const renderCard = (item, idx) => {
    if (activeTab === 'flights') return <FlightCard key={idx} flight={item} />;
    if (activeTab === 'hotels') return <HotelCard key={idx} hotel={item} />;
    return <ActivityCard key={idx} activity={item} />;
  };

  const tabData = getTabData(activeTab);

  return (
    <div className="page">
      <div className="page-header">
        <h1>Recommendations</h1>
        <p className="page-subtitle">Find flights, hotels, and activities for your next adventure</p>
      </div>

      <form onSubmit={handleSubmit} className="card rec-form">
        <div className="rec-form-row">
          <div className="form-group" style={{ flex: 2 }}>
            <label className="form-label">Destination</label>
            <input
              type="text"
              value={form.destination}
              onChange={(e) => setForm({ ...form, destination: e.target.value })}
              className="input"
              placeholder="e.g., Pokhara, Kathmandu, Chitwan"
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Origin</label>
            <input
              type="text"
              value={form.origin}
              onChange={(e) => setForm({ ...form, origin: e.target.value })}
              className="input"
              placeholder="e.g., Kathmandu"
            />
          </div>
        </div>
        <div className="rec-form-row" style={{ marginTop: 12 }}>
          <div className="form-group">
            <label className="form-label">Budget (NPR)</label>
            <input
              type="number"
              value={form.budget}
              onChange={(e) => setForm({ ...form, budget: e.target.value })}
              className="input"
              placeholder="Optional"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Travel Date</label>
            <input
              type="date"
              value={form.travel_date}
              onChange={(e) => setForm({ ...form, travel_date: e.target.value })}
              className="input"
            />
          </div>
          <div className="form-group">
            <label className="form-label">Travelers</label>
            <input
              type="number"
              min="1"
              value={form.travelers}
              onChange={(e) => setForm({ ...form, travelers: e.target.value })}
              className="input"
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="btn btn-primary rec-submit-btn"
        >
          <IconCompass size={18} />
          {loading ? 'Searching...' : 'Get Recommendations'}
        </button>
      </form>

      {loading ? (
        <RecommendationsSkeleton />
      ) : results ? (
        <div className="recommendations-results">
          <div className="results-summary">
            <h2>Recommendations for {searchedDestination}</h2>
            <div className="results-stats">
              <span><IconPlane size={14} /> {tabData.length} {activeTab}</span>
            </div>
          </div>
          <div className="recommendations-tabs">
            <div className="tabs-header">
              {TABS.map((tab) => {
                const tabCount = getTabData(tab.key).length;
                return (
                  <button
                    key={tab.key}
                    className={`tab-btn ${activeTab === tab.key ? 'active' : ''}`}
                    onClick={() => setActiveTab(tab.key)}
                  >
                    <tab.icon size={16} />
                    {tab.label}
                    {tabCount > 0 && <span className="tab-count">{tabCount}</span>}
                  </button>
                );
              })}
            </div>
            <div className="rec-grid">
              {tabData.length > 0 ? (
                tabData.map(renderCard)
              ) : (
                <EmptyTabMessage tab={activeTab} />
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="empty-state">
          <IconCompass size={48} stroke={1} />
          <h3>Find flights, hotels, and activities</h3>
          <p>Enter your destination above to get personalized recommendations.</p>
          <div className="popular-destinations">
            <span>Popular:</span>
            {['Pokhara', 'Kathmandu', 'Chitwan', 'Lukla'].map((dest) => (
              <button
                key={dest}
                className="popular-chip"
                onClick={() => setForm({ ...form, destination: dest })}
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