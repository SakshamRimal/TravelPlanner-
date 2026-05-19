import { Outlet, NavLink, useLocation } from 'react-router-dom';
import {
  IconLayoutDashboard,
  IconBriefcase,
  IconSparkles,
  IconCoin,
  IconMessage,
  IconMapPin,
  IconStar,
  IconCloud,
  IconMap,
  IconLogout,
  IconUser,
} from '@tabler/icons-react';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { to: '/', label: 'Dashboard', icon: IconLayoutDashboard, exact: true },
  { to: '/trips', label: 'My Trips', icon: IconBriefcase },
  { to: '/ai', label: 'AI Itinerary', icon: IconSparkles },
  { to: '/budget', label: 'Budget', icon: IconCoin },
  { to: '/chat', label: 'Chat', icon: IconMessage },
  { to: '/destinations', label: 'Destinations', icon: IconMapPin },
  { to: '/recommendations', label: 'Recommendations', icon: IconStar },
  { to: '/weather', label: 'Weather', icon: IconCloud },
  { to: '/maps', label: 'Maps', icon: IconMap },
];

const profileNavItem = { to: '/auth', label: 'Profile', icon: IconUser };

export default function Layout() {
  const { logout, profile } = useAuth();
  const location = useLocation();

  const getInitials = (name) => {
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="w-60 min-h-screen flex flex-col bg-white border-r border-[var(--color-border)]">
        {/* Logo Area */}
        <div className="px-4 pt-6 pb-4">
          <div className="flex items-center gap-2.5">
            <div className="w-2.5 h-2.5 rounded-full bg-[var(--color-primary)]" />
            <div>
              <p className="text-base font-semibold text-[var(--color-primary)]">TravelPlanner</p>
              <p className="text-xs text-[var(--color-text-muted)]">AI-powered trips</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex flex-col gap-1 px-3 flex-1 mt-2">
          {navItems.map((item) => {
            const isActive = item.exact
              ? location.pathname === item.to
              : location.pathname.startsWith(item.to);

            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 h-10 px-3 rounded-lg text-sm transition-all duration-150 ${
                  isActive
                    ? 'bg-[var(--color-primary-light)] text-[var(--color-primary)] font-medium'
                    : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)]'
                }`}
              >
                <item.icon size={18} stroke={1.5} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>

        {/* Profile & Logout at bottom */}
        <div className="px-3 pb-6 mt-auto">
          <NavLink
            to={profileNavItem.to}
            className={({ isActive }) =>
              `flex items-center gap-3 h-10 px-3 rounded-lg text-sm transition-all duration-150 mb-3 ${
                isActive
                  ? 'bg-[var(--color-primary-light)] text-[var(--color-primary)] font-medium'
                  : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface)]'
              }`
            }
          >
            <profileNavItem.icon size={18} stroke={1.5} />
            {profileNavItem.label}
          </NavLink>

          {profile && (
            <div className="flex items-center gap-3 p-3 rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)]">
              <div className="w-8 h-8 rounded-full bg-[var(--color-primary)] flex items-center justify-center text-white text-xs font-medium">
                {getInitials(profile.full_name || profile.email)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-[var(--color-text-primary)] truncate">
                  {profile.full_name || 'User'}
                </p>
                <p className="text-xs text-[var(--color-text-muted)] truncate">{profile.email}</p>
              </div>
              <button
                onClick={logout}
                className="p-1.5 rounded-lg text-[var(--color-text-muted)] hover:bg-[var(--color-border)] hover:text-[var(--color-error)] transition-colors"
                title="Sign out"
              >
                <IconLogout size={16} stroke={1.5} />
              </button>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 main-content overflow-auto">
        <div className="page-container">
          <Outlet />
        </div>
      </main>
    </div>
  );
}