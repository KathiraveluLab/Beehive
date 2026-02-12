import { Outlet, Link, useLocation, useNavigate } from "react-router-dom";
import {
  SunIcon,
  MoonIcon,
  BellIcon,
  ChatBubbleLeftRightIcon,
  Bars3Icon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import { useTheme } from "../context/ThemeContext";
import { useState, useEffect, useRef } from "react";
import ChatDrawer from "../components/ChatDrawer";
import { apiUrl } from "../utils/api";
import { useAuth } from "../hooks/useAuth";

interface NotificationItem {
  _id: string;
  title: string;
  username?: string;
  timestamp?: string;
  seen: boolean;
}

const AdminLayout = () => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const { user, isAdmin } = useAuth();
  const admin = isAdmin();
  const navigate = useNavigate();

  const adminNavigation = [
    { name: "Dashboard", href: "/admin" },
    { name: "Users", href: "/admin/users" },
    { name: "Analytics", href: "/admin/analytics" },
  ];

  // Notification state
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unseenCount, setUnseenCount] = useState(0);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const adminId = (user as any)?.id || "admin";

  // Pagination state
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const NOTIFICATION_PAGE_SIZE = 5;

  // Sidebar state
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Poll for unseen notifications
  useEffect(() => {
    if (!admin) return;
    const interval = setInterval(fetchUnseenNotifications, 10000);
    fetchUnseenNotifications();
    return () => clearInterval(interval);
  }, [admin]);

  // Fetch unseen notifications (for polling and badge)
  const fetchUnseenNotifications = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(
        apiUrl(
          `/api/admin/notifications?page=1&limit=${NOTIFICATION_PAGE_SIZE}`
        ),
        {
          headers: { Authorization: `Bearer ${token}` },
          credentials: "include",
        }
      );
      if (!res.ok) return;
      const data = await res.json();
      setUnseenCount(data.unseen_count);
    } catch (error) {
      console.error("Error fetching unseen notifications:", error);
    }
  };

  // Fetch and mark notifications as seen when dropdown opens
  const fetchAndMarkNotifications = async () => {
    try {
      const token = localStorage.getItem("access_token");


      // Fetch without marking seen
      const res = await fetch(
        apiUrl(
          `/api/admin/notifications?page=1&limit=${NOTIFICATION_PAGE_SIZE}`
        ),
        {
          headers: { Authorization: `Bearer ${token}` },
          credentials: "include",
        }
      );
      if (!res.ok) return;

      const data = await res.json();

      setNotifications(data.notifications);
      setPage(1);
      setHasMore(data.notifications.length === NOTIFICATION_PAGE_SIZE);

      // Get only unseen IDs
      const unseenIds: string[] = data.notifications
        .filter((n: NotificationItem) => !n.seen)
        .map((n: NotificationItem) => n._id);

      // Mark only these as seen
      if (unseenIds.length > 0) {
        await fetch(apiUrl("/api/admin/notifications/mark_seen"), {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          credentials: "include",
          body: JSON.stringify({ ids: unseenIds }),
        });

        // Decrease badge count
        setUnseenCount((prev) => Math.max(prev - unseenIds.length, 0));
      }
    } catch (error) {
      // console.error("Error fetching/marking notifications:", error);
    }
  };

  // Load more notifications
  const loadMoreNotifications = async () => {
    try {
      const nextPage = page + 1;
      const token = localStorage.getItem("access_token");


      const res = await fetch(
        apiUrl(
          `/api/admin/notifications?page=${nextPage}&limit=${NOTIFICATION_PAGE_SIZE}`
        ),
        {
          headers: { Authorization: `Bearer ${token}` },
          credentials: "include",
        }
      );
      if (!res.ok) return;
      const data = await res.json();

      if (data.notifications.length === 0) {
        setHasMore(false);
        return;
      }

      setNotifications((prev) => [...prev, ...data.notifications]);
      setPage(nextPage);

      if (data.notifications.length < NOTIFICATION_PAGE_SIZE) setHasMore(false);
    } catch (error) {
      // console.error("Error loading more notifications:", error);
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
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false);
      }
    }
    if (dropdownOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    } else {
      document.removeEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [dropdownOpen]);

  // Close sidebar on Escape key
  useEffect(() => {
    if (!sidebarOpen) return;
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") setSidebarOpen(false);
    };
    window.addEventListener("keydown", handleEsc);
    return () => window.removeEventListener("keydown", handleEsc);
  }, [sidebarOpen]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              {/* Hamburger for mobile */}
              {admin && (
                <button
                  className="sm:hidden p-2 mr-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
                  onClick={() => setSidebarOpen(true)}
                  aria-label="Open sidebar menu"
                >
                  <Bars3Icon className=" h-4 w-4 sm:h-7 sm:w-7 text-gray-700 dark:text-gray-200" />
                </button>
              )}
              <div className="flex-shrink-0 flex items-center">
                <Link
                  to="/admin"
                  className="sm:text-2xl text-lg font-bold text-black dark:text-white"
                >
                  <img
                    src="/favicon.png"
                    alt="Beehive Logo"
                    className="sm:h-8 sm:w-8 inline-block sm:mr-2 mr-1 h-6 w-6"
                  />
                  Beehive{" "}
                  <span className="text-yellow-500 align-super sm:text-sm text-xs">
                    Admin
                  </span>
                </Link>
              </div>
              {/* Top nav links hidden on mobile */}
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {admin && (
                  <>
                    {adminNavigation.map((item) => (
                      <Link
                        key={item.name}
                        to={item.href}
                        className={`${
                          location.pathname === item.href
                            ? "border-yellow-400"
                            : "border-transparent hover:border-gray-300"
                        } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200`}
                      >
                        {item.name}
                      </Link>
                    ))}
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center sm:space-x-4 space-x-1">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
              >
                {theme === "dark" ? (
                  <SunIcon className="sm:h-5 sm:w-5 h-4 w-4" />
                ) : (
                  <MoonIcon className="h-5 w-5" />
                )}
              </button>
              {admin && (
                <div className="relative" ref={dropdownRef}>
                  <button
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 relative"
                    aria-label="Notifications"
                    onClick={handleBellClick}
                  >
                    <BellIcon className="h-4 w-4 sm:h-6 sm:w-6 text-gray-700 dark:text-gray-200" />
                    {unseenCount > 0 && (
                      <span className="absolute top-0 right-0 bg-red-600 text-white rounded-full text-xs px-1.5 py-0.5 font-bold">
                        {unseenCount}
                      </span>
                    )}
                  </button>

                  {dropdownOpen && (
                    <div className="absolute right-0 mt-2 w-48 sm:w-80 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50">
                      <div className="p-4 max-h-80 overflow-y-auto notification-scroll">
                        <h3 className="text-sm font-semibold mb-2 text-gray-700 dark:text-gray-200">
                          Notifications
                        </h3>

                        {notifications.length === 0 ? (
                          <div className="text-gray-500 text-sm">
                            No notifications
                          </div>
                        ) : (
                          <ul>
                            {notifications.map((notif, idx) => (
                              <li
                                key={notif._id || idx}
                                className={`mb-2 last:mb-0 text-sm rounded-lg p-2 ${
                                  notif.seen
                                    ? "bg-transparent"
                                    : "bg-yellow-100 dark:bg-yellow-900"
                                }`}
                              >
                                <span className="font-medium">
                                  Image uploaded by {notif.username || "a user"}
                                </span>
                                : {notif.title}
                                <div className="text-xs text-gray-500">
                                  {notif.timestamp
                                    ? new Date(notif.timestamp).toLocaleString()
                                    : ""}
                                </div>
                              </li>
                            ))}
                          </ul>
                        )}

                        {/* LOAD MORE BUTTON */}
                        {hasMore && (
                          <button
                            onClick={loadMoreNotifications}
                            className="w-full mt-3 py-1.5 text-sm font-medium text-center rounded-lg bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"
                          >
                            Load More
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
              {admin && (
                <>
                  <button
                    className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
                    onClick={() => setChatOpen(true)}
                    aria-label="Open Chat"
                  >
                    <ChatBubbleLeftRightIcon className="h-4 w-4 sm:h-6 sm:w-6 text-gray-700 dark:text-gray-200" />
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
              {user ? (
                <button
                  onClick={() => {
                    localStorage.removeItem("access_token");
                    navigate("/landing");
                  }}
                  className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 px-4 rounded-lg"
                >
                  Logout
                </button>
              ) : (
                <button
                  onClick={() => navigate("/sign-in")}
                  className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 px-4 rounded-lg"
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Sidebar Drawer for mobile */}
      {admin && sidebarOpen && (
        <>
          {/* Overlay */}
          <div
            className="fixed inset-0 z-40 bg-black/40 transition-opacity"
            onClick={() => setSidebarOpen(false)}
          ></div>
          {/* Sidebar */}
          <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 shadow-2xl flex flex-col transition-transform duration-300 transform translate-x-0">
            <div className="flex items-center justify-between px-4 py-4 border-b border-gray-200 dark:border-gray-700">
              <span className="text-xl font-bold text-black dark:text-white">
                Menu
              </span>
              <button
                className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => setSidebarOpen(false)}
                aria-label="Close sidebar menu"
              >
                <XMarkIcon className="h-7 w-7 text-gray-700 dark:text-gray-200" />
              </button>
            </div>
            <nav className="flex-1 px-4 py-4 space-y-2">
              {adminNavigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`block px-4 py-2 rounded-lg text-base font-medium transition-colors duration-200
                    ${
                      location.pathname === item.href
                        ? "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300"
                        : "text-gray-800 dark:text-gray-100 hover:bg-yellow-50 dark:hover:bg-gray-700"
                    }`}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        </>
      )}

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
};

export default AdminLayout;
