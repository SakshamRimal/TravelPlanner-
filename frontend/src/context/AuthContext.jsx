import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api, getAuthHeaders, saveTokens as save, clearTokens as clear, getStoredTokens } from '../lib/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(() => getStoredTokens().access);
  const [refreshToken, setRefreshToken] = useState(() => getStoredTokens().refresh);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);

  const authHeaders = accessToken ? { Authorization: `Bearer ${accessToken}` } : {};

  const saveTokens = useCallback((access, refresh) => {
    setAccessToken(access);
    setRefreshToken(refresh);
    save(access, refresh);
  }, []);

  const logout = useCallback(() => {
    setAccessToken('');
    setRefreshToken('');
    setProfile(null);
    clear();
  }, []);

  const refreshAccessToken = useCallback(async () => {
    if (!refreshToken) return null;
    try {
      const response = await api.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
      saveTokens(response.data.access_token, response.data.refresh_token);
      return response.data.access_token;
    } catch (error) {
      logout();
      return null;
    }
  }, [refreshToken, saveTokens, logout]);

  const fetchProfile = useCallback(async () => {
    if (!accessToken) return null;
    try {
      const response = await api.get('/api/v1/users/me', { headers: authHeaders });
      setProfile(response.data);
      return response.data;
    } catch (error) {
      const newToken = await refreshAccessToken();
      if (newToken) {
        const response = await api.get('/api/v1/users/me', { headers: { Authorization: `Bearer ${newToken}` } });
        setProfile(response.data);
        return response.data;
      }
      return null;
    }
  }, [accessToken, authHeaders, refreshAccessToken]);

  useEffect(() => {
    if (accessToken && !profile) {
      fetchProfile();
    }
  }, [accessToken, profile, fetchProfile]);

  const value = {
    accessToken,
    refreshToken,
    profile,
    loading,
    authHeaders,
    saveTokens,
    logout,
    refreshAccessToken,
    fetchProfile,
    isAuthenticated: !!accessToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}