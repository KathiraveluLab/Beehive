import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { SignedIn, SignedOut, UserButton, useUser } from '@clerk/clerk-react';
import { SunIcon, MoonIcon, BellIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { useTheme } from '../context/ThemeContext';
import { useState, useEffect, useRef } from 'react';
import ChatDrawer from '../components/ChatDrawer';

const AdminLayout = () => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const { user } = useUser();

  const navigate = useNavigate();

  const isAdmin = user?.unsafeMetadata?.role === 'admin';

  const adminNavigation = [
    { name: 'Dashboard', href: '/admin' },
    { name: 'Users', href: '/admin/users' },
    { name: 'Analytics', href: '/admin/analytics' },
  ];

  // Notification state
  const [notifications, setNotifications] = useState<any[]>([]);
  const [unseenCount, setUnseenCount] = useState(0);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const adminId = user?.id || 'admin';

  // Poll for unseen notifications
  useEffect(() => {
    if (!isAdmin) return;
    const interval = setInterval(fetchUnseenNotifications, 10000);
    fetchUnseenNotifications();
    return () => clearInterval(interval);
  }, [isAdmin]);

  // Fetch unseen notifications (for polling and badge)
  const fetchUnseenNotifications = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/admin/notifications', {
        method: 'GET',
        credentials: 'include',
      });
      if (!response.ok) return;
      const data = await response.json();
      if (data.notifications && data.notifications.length > 0) {
        setUnseenCount(data.notifications.length);
      } else {
        setUnseenCount(0);
      }
    } catch (e) {
      // Ignore notification errors
    }
  };

  // Fetch and mark notifications as seen when dropdown opens
  const fetchAndMarkNotifications = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/admin/notifications?mark_seen=true', {
        method: 'GET',
        credentials: 'include',
      });
      if (!response.ok) return;
      const data = await response.json();
      if (data.notifications) {
        setNotifications(data.notifications);
        setUnseenCount(0);
      }
    } catch (e) {
      // Ignore notification errors
    }
  };

  // Open dropdown and mark notifications as seen
  const handleBellClick = () => {
    setDropdownOpen((open) => {
      const willOpen = !open;
      if (willOpen) {
        fetchAndMarkNotifications();
      }
      return willOpen;
    });
  };

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    }
    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [dropdownOpen]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link to="/" className="text-2xl font-bold text-black">
                <img src="/favicon.png" alt="Beehive Logo" className="h-8 w-8 inline-block mr-2" />
                  Beehive <span className="text-yellow-500 align-super text-sm">Admin</span>
                </Link>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {isAdmin && (
                  <>
                    {adminNavigation.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`${
                          location.pathname === item.href
                            ? 'border-yellow-400 text-black'
                            : 'border-transparent hover:border-gray-300 text-black'
                        } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200`}
                      >
                        {item.name}
                      </Link>
                    ))}
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
              >
                {theme === 'dark' ? (
                  <SunIcon className="h-5 w-5" />
                ) : (
                  <MoonIcon className="h-5 w-5" />
                )}
              </button>
              {isAdmin && (
                <div className="relative" ref={dropdownRef}>
                  <button
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 relative"
                    onClick={handleBellClick}
                    aria-label="Notifications"
                  >
                    <BellIcon className="h-6 w-6 text-gray-700 dark:text-gray-200" />
                    {unseenCount > 0 && (
                      <span className="absolute top-0 right-0 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-bold leading-none text-white bg-red-600 rounded-full">
                        {unseenCount}
                      </span>
                    )}
                  </button>
                  {dropdownOpen && (
                    <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
                      <div className="p-4 max-h-80 overflow-y-auto">
                        <h3 className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-200">Notifications</h3>
                        {notifications.length === 0 ? (
                          <div className="text-gray-500 text-sm">No new notifications</div>
                        ) : (
                          <ul>
                            {notifications.map((notif, idx) => (
                              <li key={notif._id || idx} className="mb-2 last:mb-0 text-sm text-gray-800 dark:text-gray-100">
                                <span className="font-medium">Image uploaded by {notif.username || 'a user'}</span>: {notif.title}
                                <div className="text-xs text-gray-500">{notif.timestamp ? new Date(notif.timestamp).toLocaleString() : ''}</div>
                              </li>
                            ))}
                          </ul>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
              {isAdmin && (
                <>
                  <button
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
                    onClick={() => setChatOpen(true)}
                    aria-label="Open Chat"
                  >
                    <ChatBubbleLeftRightIcon className="h-6 w-6 text-gray-700 dark:text-gray-200" />
                  </button>
                  {chatOpen && (
                    <ChatDrawer
                      userId={adminId}
                      userRole="admin"
                      onClose={() => setChatOpen(false)}
                    />
                  )}
                </>
              )}
              <SignedIn>
                <UserButton afterSignOutUrl="/sign-in" />
              </SignedIn>
              <SignedOut>
                <button
                  onClick={() => navigate('/sign-in')}
                  className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
                >
                  Sign In
                </button>
              </SignedOut>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <SignedIn>
          <Outlet />
        </SignedIn>
        <SignedOut>
          <div className="text-center py-12">
            <h2 className="text-2xl font-bold mb-4">Please Sign In</h2>
            <p className="mb-4 text-gray-600 dark:text-gray-400">You need to be signed in to access this content.</p>
            <button
              onClick={() => navigate('/sign-in')}
              className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Sign In
            </button>
          </div>
        </SignedOut>
      </main>
    </div>
  );
};

export default AdminLayout; 