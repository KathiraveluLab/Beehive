import { Link } from 'react-router-dom';
import { useUser } from '@clerk/clerk-react';
import { CloudArrowUpIcon, PhotoIcon } from '@heroicons/react/24/outline';

const Home = () => {
  const { user } = useUser();

  return (
    <div className="py-12">
      <div className="max-w-3xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-6">
          Welcome to Beehive, {user?.firstName || 'Guest'}!
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">
          Your personal space to upload, manage, and share your media content.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <Link
            to="/upload"
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-all duration-200 group"
          >
            <div className="flex flex-col items-center p-6">
              <CloudArrowUpIcon className="h-12 w-12 text-yellow-400 mb-4 group-hover:scale-110 transition-transform duration-200" />
              <h3 className="text-xl font-semibold mb-2">Upload Media</h3>
              <p className="text-gray-600 dark:text-gray-400 text-center">
                Share your images and voice notes with descriptions and sentiments
              </p>
            </div>
          </Link>

          <Link
            to="/gallery"
            className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-all duration-200 group"
          >
            <div className="flex flex-col items-center p-6">
              <PhotoIcon className="h-12 w-12 text-yellow-400 mb-4 group-hover:scale-110 transition-transform duration-200" />
              <h3 className="text-xl font-semibold mb-2">View Gallery</h3>
              <p className="text-gray-600 dark:text-gray-400 text-center">
                Browse and manage your uploaded media content
              </p>
            </div>
          </Link>
        </div>

        {user?.publicMetadata?.role === 'admin' && (
          <div className="mt-12">
            <h2 className="text-2xl font-semibold mb-4">Admin Quick Access</h2>
            <div className="flex justify-center space-x-4">
              <Link 
                to="/admin" 
                className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
              >
                Dashboard
              </Link>
              <Link 
                to="/admin/users" 
                className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
              >
                Manage Users
              </Link>
              <Link 
                to="/admin/analytics" 
                className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
              >
                View Analytics
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Home; 