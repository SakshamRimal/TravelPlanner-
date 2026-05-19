import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Auth from './pages/Auth';
import Trips from './pages/Trips';
import Budget from './pages/Budget';
import Destinations from './pages/Destinations';
import Recommendations from './pages/Recommendations';
import AI from './pages/AI';
import Chat from './pages/Chat';
import Weather from './pages/Weather';
import Maps from './pages/Maps';
import { ToastContainer } from './components/Toast';

export default function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="auth" element={<Auth />} />
          <Route path="trips" element={<Trips />} />
          <Route path="budget" element={<Budget />} />
          <Route path="destinations" element={<Destinations />} />
          <Route path="recommendations" element={<Recommendations />} />
          <Route path="ai" element={<AI />} />
          <Route path="chat" element={<Chat />} />
          <Route path="weather" element={<Weather />} />
          <Route path="maps" element={<Maps />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
      <ToastContainer />
    </>
  );
}