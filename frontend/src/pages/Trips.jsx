import { useState, useEffect } from 'react';
import { api, getAuthHeaders } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { showToast } from '../components/Toast';
import {
  IconPlus,
  IconEdit,
  IconTrash,
  IconX,
  IconBriefcase,
  IconCalendar,
  IconUsers,
  IconCoin,
  IconMapPin,
} from '@tabler/icons-react';

const STATUS_MAP = {
  planned: { label: 'Planning', class: 'badge-planning' },
  confirmed: { label: 'Confirmed', class: 'badge-confirmed' },
  completed: { label: 'Completed', class: 'badge-completed' },
  active: { label: 'Active', class: 'badge-active' },
};

function formatDateRange(start, end) {
  if (!start) return '';
  const s = new Date(start);
  const e = end ? new Date(end) : null;
  const fmt = (d) => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  if (!e || s.getTime() === e.getTime()) return fmt(s);
  return `${fmt(s)} – ${fmt(e)}`;
}

function TripModal({ trip, onClose, onSave }) {
  const [form, setForm] = useState({
    origin: trip?.origin || 'KTM',
    destination: trip?.destination || '',
    budget: trip?.budget || '',
    travelers: trip?.travelers || 1,
    start_date: trip?.start_date || '',
    end_date: trip?.end_date || '',
    interests: trip?.interests || '',
    transport: trip?.transport || '',
    accommodation: trip?.accommodation || '',
    status: trip?.status || 'planned',
  });
  const [interests, setInterests] = useState(
    trip?.interests ? trip.interests.split(',').map((i) => i.trim()).filter(Boolean) : []
  );
  const [saving, setSaving] = useState(false);

  const handleInterestKey = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      const val = e.target.value.trim();
      if (val && !interests.includes(val)) {
        setInterests([...interests, val]);
        setForm({ ...form, interests: [...interests, val].join(', ') });
      }
      e.target.value = '';
    }
  };

  const removeInterest = (i) => {
    const updated = interests.filter((_, idx) => idx !== i);
    setInterests(updated);
    setForm({ ...form, interests: updated.join(', ') });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave(form, trip?.id);
      onClose();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{trip ? 'Edit trip' : 'Create new trip'}</h2>
          <button className="modal-close" onClick={onClose}>
            <IconX size={20} />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="modal-body">
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Origin</label>
              <input
                type="text"
                className="input"
                value={form.origin}
                onChange={(e) => setForm({ ...form, origin: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Destination</label>
              <input
                type="text"
                className="input"
                value={form.destination}
                onChange={(e) => setForm({ ...form, destination: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Start Date</label>
              <input
                type="date"
                className="input"
                value={form.start_date}
                onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">End Date</label>
              <input
                type="date"
                className="input"
                value={form.end_date}
                onChange={(e) => setForm({ ...form, end_date: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label className="form-label">Budget</label>
              <input
                type="number"
                className="input"
                value={form.budget}
                onChange={(e) => setForm({ ...form, budget: e.target.value })}
                placeholder="0"
              />
            </div>
            <div className="form-group">
              <label className="form-label">Travelers</label>
              <input
                type="number"
                min="1"
                className="input"
                value={form.travelers}
                onChange={(e) => setForm({ ...form, travelers: e.target.value })}
              />
            </div>
            <div className="form-group full-width">
              <label className="form-label">Interests</label>
              <div className="tag-input-container">
                <input
                  type="text"
                  className="input tag-input"
                  placeholder="Type interest and press Enter"
                  onKeyDown={handleInterestKey}
                />
                {interests.length > 0 && (
                  <div className="tag-list">
                    {interests.map((tag, i) => (
                      <span key={i} className="tag-chip">
                        {tag}
                        <button type="button" onClick={() => removeInterest(i)}>
                          <IconX size={12} />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Transport</label>
              <input
                type="text"
                className="input"
                value={form.transport}
                onChange={(e) => setForm({ ...form, transport: e.target.value })}
                placeholder="Flight, Train..."
              />
            </div>
            <div className="form-group">
              <label className="form-label">Status</label>
              <select
                className="input"
                value={form.status}
                onChange={(e) => setForm({ ...form, status: e.target.value })}
              >
                <option value="planned">Planning</option>
                <option value="confirmed">Confirmed</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-ghost" onClick={onClose}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Saving...' : 'Save Trip'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Trips() {
  const { authHeaders, isAuthenticated } = useAuth();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTrip, setEditingTrip] = useState(null);
  const [deletingId, setDeletingId] = useState(null);

  const fetchTrips = async () => {
    setLoading(true);
    try {
      const response = await api.get('/api/v1/trips', { headers: getAuthHeaders() });
      setTrips(response.data);
    } catch {
      showToast('Failed to load trips', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isAuthenticated) fetchTrips();
  }, [isAuthenticated]);

  const handleSave = async (formData, tripId) => {
    const payload = {
      ...formData,
      budget: formData.budget ? Number(formData.budget) : null,
      travelers: Number(formData.travelers),
    };
    if (tripId) {
      const response = await api.patch(`/api/v1/trips/${tripId}`, payload, { headers: getAuthHeaders() });
      setTrips((prev) => prev.map((t) => (t.id === response.data.id ? response.data : t)));
      showToast('Trip updated', 'success');
    } else {
      const response = await api.post('/api/v1/trips', payload, { headers: getAuthHeaders() });
      setTrips((prev) => [response.data, ...prev]);
      showToast('Trip created successfully!', 'success');
    }
  };

  const handleDelete = async (tripId) => {
    await api.delete(`/api/v1/trips/${tripId}`, { headers: getAuthHeaders() });
    setTrips((prev) => prev.filter((t) => t.id !== tripId));
    setDeletingId(null);
    showToast('Trip deleted', 'error');
  };

  const openEdit = (trip) => {
    setEditingTrip(trip);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingTrip(null);
  };

  const getStatusInfo = (status) => STATUS_MAP[status] || { label: status, class: 'badge-planning' };

  return (
    <div className="page">
      {/* Page Header */}
      <div className="page-header">
        <h1>My Trips</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <IconPlus size={18} />
          New Trip
        </button>
      </div>

      {/* Trip Grid */}
      {loading ? (
        <div className="trips-grid">
          {[1, 2, 3].map((i) => (
            <div key={i} className="trip-card trip-card-skeleton">
              <div className="skeleton" style={{ height: 20, width: '60%', marginBottom: 8 }} />
              <div className="skeleton" style={{ height: 16, width: '40%', marginBottom: 12 }} />
              <div className="skeleton" style={{ height: 14, width: '80%' }} />
            </div>
          ))}
        </div>
      ) : trips.length === 0 ? (
        <div className="empty-state">
          <IconBriefcase size={48} stroke={1} />
          <h3>No trips yet</h3>
          <p>Start planning your first adventure.</p>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <IconPlus size={18} />
            Plan your first trip
          </button>
        </div>
      ) : (
        <div className="trips-grid">
          {trips.map((trip) => {
            const status = getStatusInfo(trip.status);
            return (
              <div key={trip.id} className="trip-card">
                <div className="trip-card-header">
                  <div className="trip-title">
                    {trip.origin} → {trip.destination}
                  </div>
                  <span className={`badge ${status.class}`}>{status.label}</span>
                </div>
                <div className="trip-meta">
                  <span>
                    <IconCalendar size={14} />
                    {formatDateRange(trip.start_date, trip.end_date)}
                  </span>
                  <span>
                    <IconUsers size={14} />
                    {trip.travelers} traveler{trip.travelers !== 1 ? 's' : ''}
                  </span>
                  {trip.budget && (
                    <span>
                      <IconCoin size={14} />
                      Budget: NPR {trip.budget.toLocaleString()}
                    </span>
                  )}
                </div>
                {(trip.interests || trip.transport) && (
                  <div className="trip-tags">
                    {trip.interests &&
                      trip.interests.split(',').map((i, idx) => (
                        <span key={idx} className="trip-tag">
                          <IconMapPin size={12} />
                          {i.trim()}
                        </span>
                      ))}
                    {trip.transport && (
                      <span className="trip-tag">{trip.transport.trim()}</span>
                    )}
                  </div>
                )}
                {deletingId === trip.id ? (
                  <div className="trip-delete-confirm">
                    <span>Delete this trip?</span>
                    <div className="trip-delete-actions">
                      <button
                        className="btn btn-ghost"
                        onClick={() => setDeletingId(null)}
                      >
                        Cancel
                      </button>
                      <button
                        className="btn btn-danger"
                        onClick={() => handleDelete(trip.id)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="trip-card-actions">
                    <button
                      className="btn btn-ghost-icon"
                      onClick={() => openEdit(trip)}
                      title="Edit trip"
                    >
                      <IconEdit size={16} />
                    </button>
                    <button
                      className="btn btn-ghost-icon btn-danger-ghost"
                      onClick={() => setDeletingId(trip.id)}
                      title="Delete trip"
                    >
                      <IconTrash size={16} />
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <TripModal trip={editingTrip} onClose={closeModal} onSave={handleSave} />
      )}
    </div>
  );
}