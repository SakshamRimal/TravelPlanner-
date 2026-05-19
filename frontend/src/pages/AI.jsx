import { useState } from 'react';
import { api, getAuthHeaders } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { showToast } from '../components/Toast';
import { IconSparkles, IconMapPin, IconCalendar, IconCoin, IconClock, IconStar } from '@tabler/icons-react';

export default function AI() {
  const { isAuthenticated } = useAuth();
  const [form, setForm] = useState({
    origin: 'KTM',
    destination: '',
    budget: '',
    travelers: 1,
    start_date: '',
    end_date: '',
    interests: '',
    transport: '',
    accommodation: '',
    additional_notes: '',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      showToast('Please sign in first', 'error');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        ...form,
        budget: form.budget ? Number(form.budget) : null,
        travelers: Number(form.travelers),
        interests: form.interests ? form.interests.split(',').map((i) => i.trim()) : [],
      };
      const response = await api.post('/api/v1/ai/itinerary', payload, { headers: getAuthHeaders() });
      setResult(response.data);
      showToast('Itinerary generated!', 'success');
    } catch (error) {
      showToast(error.response?.data?.detail || 'Failed to generate itinerary', 'error');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    if (!amount) return 'NPR 0';
    return `NPR ${Math.round(amount).toLocaleString()}`;
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>AI Itinerary</h1>
      </div>

      <form onSubmit={handleSubmit} className="card ai-form">
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">Origin</label>
            <input type="text" value={form.origin} onChange={(e) => setForm({ ...form, origin: e.target.value })} className="input" placeholder="KTM" />
          </div>
          <div className="form-group">
            <label className="form-label">Destination</label>
            <input type="text" value={form.destination} onChange={(e) => setForm({ ...form, destination: e.target.value })} className="input" placeholder="Where to?" required />
          </div>
          <div className="form-group">
            <label className="form-label">Budget (NPR)</label>
            <input type="number" value={form.budget} onChange={(e) => setForm({ ...form, budget: e.target.value })} className="input" placeholder="0" />
          </div>
          <div className="form-group">
            <label className="form-label">Travelers</label>
            <input type="number" min="1" value={form.travelers} onChange={(e) => setForm({ ...form, travelers: e.target.value })} className="input" />
          </div>
          <div className="form-group">
            <label className="form-label">Start Date</label>
            <input type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} className="input" required />
          </div>
          <div className="form-group">
            <label className="form-label">End Date</label>
            <input type="date" value={form.end_date} onChange={(e) => setForm({ ...form, end_date: e.target.value })} className="input" required />
          </div>
          <div className="form-group full-width">
            <label className="form-label">Interests (comma-separated)</label>
            <input type="text" value={form.interests} onChange={(e) => setForm({ ...form, interests: e.target.value })} className="input" placeholder="Adventure, Culture, Food..." />
          </div>
          <div className="form-group">
            <label className="form-label">Transport</label>
            <input type="text" value={form.transport} onChange={(e) => setForm({ ...form, transport: e.target.value })} className="input" placeholder="Flight, Bus..." />
          </div>
          <div className="form-group">
            <label className="form-label">Accommodation</label>
            <input type="text" value={form.accommodation} onChange={(e) => setForm({ ...form, accommodation: e.target.value })} className="input" placeholder="Hotel, Guesthouse..." />
          </div>
          <div className="form-group full-width">
            <label className="form-label">Additional Notes</label>
            <textarea
              value={form.additional_notes}
              onChange={(e) => setForm({ ...form, additional_notes: e.target.value })}
              className="input"
              placeholder="Any specific requirements or preferences..."
              style={{ height: 'auto', minHeight: '80px', padding: '12px' }}
            />
          </div>
        </div>
        <button type="submit" disabled={loading} className="btn btn-primary">
          <IconSparkles size={18} />
          {loading ? 'Generating...' : 'Generate Itinerary'}
        </button>
      </form>

      {result && (
        <div className="itinerary-result">
          {/* Summary */}
          <div className="itinerary-summary card">
            <h2>Your Trip to {form.destination}</h2>
            <p className="summary-text">{result.summary}</p>
            {result.estimated_total && (
              <div className="total-badge">
                <IconCoin size={18} />
                Estimated Total: {formatCurrency(result.estimated_total)}
              </div>
            )}
          </div>

          {/* Days */}
          {result.days && result.days.length > 0 && (
            <div className="itinerary-days">
              <h3>Daily Itinerary</h3>
              {result.days.map((day, idx) => (
                <div key={idx} className="day-card card">
                  <div className="day-header">
                    <span className="day-number">Day {idx + 1}</span>
                    {day.date && <span className="day-date">{day.date}</span>}
                  </div>
                  <div className="day-title">{day.title || 'Daily Schedule'}</div>
                  <div className="activities-list">
                    {day.morning && (
                      <div className="activity-item">
                        <span className="activity-time"><IconClock size={14} />Morning</span>
                        <span className="activity-name">{day.morning}</span>
                      </div>
                    )}
                    {day.late_morning && (
                      <div className="activity-item">
                        <span className="activity-time"><IconClock size={14} />Late Morning</span>
                        <span className="activity-name">{day.late_morning}</span>
                      </div>
                    )}
                    {day.afternoon && (
                      <div className="activity-item">
                        <span className="activity-time"><IconClock size={14} />Afternoon</span>
                        <span className="activity-name">{day.afternoon}</span>
                      </div>
                    )}
                    {day.late_afternoon && (
                      <div className="activity-item">
                        <span className="activity-time"><IconClock size={14} />Late Afternoon</span>
                        <span className="activity-name">{day.late_afternoon}</span>
                      </div>
                    )}
                    {day.evening && (
                      <div className="activity-item">
                        <span className="activity-time"><IconClock size={14} />Evening</span>
                        <span className="activity-name">{day.evening}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Tips */}
          {result.tips && result.tips.length > 0 && (
            <div className="itinerary-tips card">
              <h3>Travel Tips</h3>
              <ul>
                {result.tips.map((tip, idx) => (
                  <li key={idx}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}