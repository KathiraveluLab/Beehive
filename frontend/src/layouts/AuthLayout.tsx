import { Outlet, Link } from 'react-router-dom';
import { SignedIn, RedirectToSignIn } from '@clerk/clerk-react';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';
import { useTheme } from '../context/ThemeContext';

const AuthLayout = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <SignedIn>
        <RedirectToSignIn />
      </SignedIn>
      
      <div className="flex min-h-screen">
        {/* Left side - Branding */}
        <div className="hidden lg:flex lg:w-1/2 bg-yellow-400 items-center justify-center">
          <div className="text-center">
            <Link to="/" className="text-4xl font-bold text-black hover:text-gray-900 transition-colors duration-200">
              Beehive
            </Link>
            <p className="mt-4 text-lg text-black">
              Upload, Share, and Manage Your Media
            </p>
          </div>
        </div>

        {/* Right side - Auth Form */}
        <div className="w-full lg:w-1/2">
          <div className="flex justify-end p-4">
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
          </div>
          
          <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">
            <div className="w-full max-w-md">
              <Outlet />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AuthLayout; 