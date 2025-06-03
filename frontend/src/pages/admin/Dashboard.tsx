import { useState } from 'react';
import {
  UsersIcon,
  PhotoIcon,
  ChartBarIcon,
  MicrophoneIcon,
} from '@heroicons/react/24/outline';

// Mock data - replace with actual data from backend
const mockStats = {
  totalUsers: 150,
  totalImages: 450,
  totalVoiceNotes: 200,
  recentUploads: [
    {
      id: 1,
      title: 'Mountain View',
      user: 'John Doe',
      timestamp: '2024-02-01T12:00:00Z',
      type: 'image',
    },
    {
      id: 2,
      title: 'Beach Sunset',
      user: 'Jane Smith',
      timestamp: '2024-02-01T11:30:00Z',
      type: 'image',
    },
    {
      id: 3,
      title: 'Voice Note #123',
      user: 'Mike Johnson',
      timestamp: '2024-02-01T11:00:00Z',
      type: 'voice',
    },
    // Add more mock data as needed
  ],
};

const StatCard = ({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string;
  value: number;
  icon: React.ElementType;
  color: string;
}) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md transition-colors duration-200">
    <div className="p-6">
      <div className="flex items-center">
        <div className={`p-3 rounded-lg ${color} bg-opacity-10 mr-4`}>
          <Icon className={`h-6 w-6 ${color}`} />
        </div>
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
            {title}
          </p>
          <p className="text-2xl font-semibold mt-1">{value}</p>
        </div>
      </div>
    </div>
  </div>
);

const Dashboard = () => {
  const [stats] = useState(mockStats);

  return (
    <div className="py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Users"
            value={stats.totalUsers}
            icon={UsersIcon}
            color="text-blue-500"
          />
          <StatCard
            title="Total Images"
            value={stats.totalImages}
            icon={PhotoIcon}
            color="text-green-500"
          />
          <StatCard
            title="Voice Notes"
            value={stats.totalVoiceNotes}
            icon={MicrophoneIcon}
            color="text-purple-500"
          />
          <StatCard
            title="Total Media"
            value={stats.totalImages + stats.totalVoiceNotes}
            icon={ChartBarIcon}
            color="text-yellow-400"
          />
        </div>

        {/* Recent Activity */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md transition-colors duration-200">
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Title</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">User</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Type</th>
                    <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recentUploads.map((upload) => (
                    <tr
                      key={upload.id}
                      className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                    >
                      <td className="py-3 px-4">{upload.title}</td>
                      <td className="py-3 px-4">{upload.user}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            upload.type === 'image'
                              ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                              : 'bg-purple-100 text-purple-800 dark:bg-purple-800 dark:text-purple-100'
                          }`}
                        >
                          {upload.type}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        {new Date(upload.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 