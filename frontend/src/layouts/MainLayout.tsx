import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { SignedIn, SignedOut, UserButton, useUser } from '@clerk/clerk-react';
import { SunIcon, MoonIcon, ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';
import { useTheme } from '../context/ThemeContext';
import { useState } from 'react';
import ChatDrawer from '../components/ChatDrawer';

const MainLayout = () => {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const { user } = useUser();
  const navigate = useNavigate();
  const [chatOpen, setChatOpen] = useState(false);
  const userId = user?.id || '';

  const navigation = [
    { name: 'Home', href: '/dashboard' },
    { name: 'Gallery', href: '/gallery' },
    { name: 'Upload', href: '/upload' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link to="/" className="text-2xl font-bold text-black">
                  <img src="/favicon.png" alt="Beehive Logo" className="h-8 w-8 inline-block mr-2" />
                  Beehive
                </Link>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`${
                      location.pathname === item.href
                        ? 'border-yellow-400'
                        : 'border-transparent hover:border-gray-300'
                    } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200`}
                  >
                    {item.name}
                  </Link>
                ))}
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
              {user && (
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
                      userId={userId}
                      userRole="user"
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

export default MainLayout; 