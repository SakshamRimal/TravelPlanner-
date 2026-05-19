import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, saveTokens } from '../lib/api';
import { useAuth } from '../context/AuthContext';
import { IconPlane, IconEye, IconEyeOff } from '@tabler/icons-react';

export default function Auth() {
  const { saveTokens: saveTokensAuth, fetchProfile, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [activeTab, setActiveTab] = useState('signin');
  const [registerForm, setRegisterForm] = useState({ email: '', full_name: '', password: '', confirmPassword: '' });
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(null);
  const [message, setMessage] = useState(null);

  // Redirect if already authenticated
  if (isAuthenticated) {
    navigate('/');
  }

  const getPasswordStrength = (password) => {
    if (!password) return { score: 0, label: '' };
    let score = 0;
    if (password.length >= 8) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
    const colors = ['', '#EF4444', '#F59E0B', '#EAB308', '#10B981'];
    return { score, label: labels[score], color: colors[score] };
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (registerForm.password !== registerForm.confirmPassword) {
      setMessage({ type: 'error', text: 'Passwords do not match' });
      return;
    }
    setLoading('register');
    setMessage(null);
    try {
      const response = await api.post('/api/v1/auth/register', {
        email: registerForm.email,
        full_name: registerForm.full_name,
        password: registerForm.password,
      });
      saveTokensAuth(response.data.access_token, response.data.refresh_token);
      navigate('/');
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Registration failed' });
    } finally {
      setLoading(null);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading('login');
    setMessage(null);
    try {
      const response = await api.post('/api/v1/auth/login', {
        email: loginForm.email,
        password: loginForm.password,
      });
      saveTokensAuth(response.data.access_token, response.data.refresh_token);
      await fetchProfile();
      navigate('/');
    } catch (error) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'Login failed' });
    } finally {
      setLoading(null);
    }
  };

  const strength = getPasswordStrength(registerForm.password);

  return (
    <div className="flex min-h-screen">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-2/5 bg-[var(--color-primary)] flex-col justify-center items-center p-12 text-white">
        <IconPlane size={48} stroke={1.5} className="mb-4" />
        <h1 className="text-3xl font-bold mb-2">TravelPlanner</h1>
        <p className="text-lg text-blue-200 mb-12">Plan smarter. Travel better.</p>

        <div className="space-y-3">
          {['✦ AI-powered itineraries', '✦ Smart budget tracking', '✦ Real-time recommendations'].map((feature) => (
            <div key={feature} className="px-4 py-2 rounded-full bg-white/15 text-sm">
              {feature}
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-[var(--color-surface)]">
        <div className="w-full max-w-md">
          {/* Form Card */}
          <div className="card p-8">
            {/* Tabs */}
            <div className="flex gap-8 border-b border-[var(--color-border)] mb-6">
              <button
                onClick={() => { setActiveTab('signin'); setMessage(null); }}
                className={`pb-3 text-sm font-medium transition-colors ${
                  activeTab === 'signin'
                    ? 'text-[var(--color-primary)] border-b-2 border-[var(--color-primary)]'
                    : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'
                }`}
              >
                Sign in
              </button>
              <button
                onClick={() => { setActiveTab('register'); setMessage(null); }}
                className={`pb-3 text-sm font-medium transition-colors ${
                  activeTab === 'register'
                    ? 'text-[var(--color-primary)] border-b-2 border-[var(--color-primary)]'
                    : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]'
                }`}
              >
                Register
              </button>
            </div>

            {message && (
              <div className={`message ${message.type === 'success' ? 'message-success' : 'message-error'}`}>
                {message.text}
              </div>
            )}

            {/* Sign In Form */}
            {activeTab === 'signin' && (
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="form-label">Email address</label>
                  <input
                    type="email"
                    value={loginForm.email}
                    onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                    className="input"
                    placeholder="you@example.com"
                    required
                  />
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <label className="form-label mb-0">Password</label>
                    <button type="button" className="text-xs text-[var(--color-primary)] hover:underline">
                      Forgot password?
                    </button>
                  </div>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={loginForm.password}
                      onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                      className="input pr-10"
                      placeholder="Enter your password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
                    >
                      {showPassword ? <IconEyeOff size={18} /> : <IconEye size={18} />}
                    </button>
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={loading === 'login'}
                  className="btn btn-primary w-full h-11"
                >
                  {loading === 'login' ? 'Signing in...' : 'Sign in'}
                </button>
                <p className="text-sm text-center text-[var(--color-text-secondary)]">
                  Don't have an account?{' '}
                  <button type="button" onClick={() => setActiveTab('register')} className="text-[var(--color-primary)] font-medium hover:underline">
                    Register
                  </button>
                </p>
              </form>
            )}

            {/* Register Form */}
            {activeTab === 'register' && (
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <label className="form-label">Full name</label>
                  <input
                    type="text"
                    value={registerForm.full_name}
                    onChange={(e) => setRegisterForm({ ...registerForm, full_name: e.target.value })}
                    className="input"
                    placeholder="John Doe"
                    required
                  />
                </div>
                <div>
                  <label className="form-label">Email address</label>
                  <input
                    type="email"
                    value={registerForm.email}
                    onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                    className="input"
                    placeholder="you@example.com"
                    required
                  />
                </div>
                <div>
                  <label className="form-label">Password</label>
                  <div className="relative">
                    <input
                      type={showPassword ? 'text' : 'password'}
                      value={registerForm.password}
                      onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                      className="input pr-10"
                      placeholder="Create a password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
                    >
                      {showPassword ? <IconEyeOff size={18} /> : <IconEye size={18} />}
                    </button>
                  </div>
                  {/* Password Strength */}
                  {registerForm.password && (
                    <div className="mt-2">
                      <div className="flex gap-1 mb-1">
                        {[1, 2, 3, 4].map((level) => (
                          <div
                            key={level}
                            className="h-1 flex-1 rounded-full transition-colors"
                            style={{ background: strength.score >= level ? strength.color : 'var(--color-border)' }}
                          />
                        ))}
                      </div>
                      <p className="text-xs" style={{ color: strength.color }}>{strength.label}</p>
                    </div>
                  )}
                </div>
                <div>
                  <label className="form-label">Confirm password</label>
                  <div className="relative">
                    <input
                      type={showConfirmPassword ? 'text' : 'password'}
                      value={registerForm.confirmPassword}
                      onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                      className={`input pr-10 ${registerForm.confirmPassword && registerForm.password !== registerForm.confirmPassword ? 'input error' : ''}`}
                      placeholder="Confirm your password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-text-muted)] hover:text-[var(--color-text-secondary)]"
                    >
                      {showConfirmPassword ? <IconEyeOff size={18} /> : <IconEye size={18} />}
                    </button>
                  </div>
                  {registerForm.confirmPassword && registerForm.password !== registerForm.confirmPassword && (
                    <p className="form-error">Passwords do not match</p>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={loading === 'register'}
                  className="btn btn-primary w-full h-11"
                >
                  {loading === 'register' ? 'Creating account...' : 'Create account'}
                </button>
                <p className="text-sm text-center text-[var(--color-text-secondary)]">
                  Already have an account?{' '}
                  <button type="button" onClick={() => setActiveTab('signin')} className="text-[var(--color-primary)] font-medium hover:underline">
                    Sign in
                  </button>
                </p>
              </form>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}