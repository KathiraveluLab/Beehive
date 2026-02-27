import { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { apiUrl } from '../../utils/api';
import { getToken } from '../../utils/auth';
import {
  PhotoIcon,
  ChartBarIcon,
  MicrophoneIcon,
} from '@heroicons/react/24/outline';

// Types for the dashboard data
interface DashboardStats {
  totalImages: number;
  totalVoiceNotes: number;
  totalMedia: number;
}

interface RecentUpload {
  id: string;
  title: string;
  user: string;
  timestamp: string;
  description: string;
  filename: string;
  audio_filename?: string;
  sentiment?: string;
}

interface DashboardData {
  stats: DashboardStats;
  recentUploads: RecentUpload[];
}

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
        <div className={`p-3 rounded-lg ${color}/10 mr-4`}>
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
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // sorting / filtering state
  const [sortOption, setSortOption] = useState<'date_desc'|'date_asc'|'user_asc'|'user_desc'>('date_desc');
  const [filterUser, setFilterUser] = useState('');
  const [filterFromDate, setFilterFromDate] = useState('');
  const [filterToDate, setFilterToDate] = useState('');

  const location = useLocation();

  useEffect(() => {
    // if user filter provided in query string, pre-populate
    const params = new URLSearchParams(location.search);
    const userParam = params.get('user');
    if (userParam) {
      setFilterUser(userParam);
    }
    fetchDashboardData();
  }, [location.search]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get the JWT token from helper
      const token = getToken();

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(apiUrl('/api/admin/dashboard?limit=10'), {
        method: 'GET',
        headers,
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Error loading dashboard
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  <p>{error}</p>
                </div>
                <div className="mt-4">
                  <button
                    onClick={fetchDashboardData}
                    className="bg-red-100 text-red-800 px-3 py-2 rounded-md text-sm font-medium hover:bg-red-200"
                  >
                    Try again
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <p className="text-gray-500">No data available</p>
          </div>
        </div>
      </div>
    );
  }

  const { stats, recentUploads } = dashboardData;

  // apply filters and sorting to recent uploads
  let displayedUploads = [...recentUploads];

  // filter by user substring
  if (filterUser.trim()) {
    const term = filterUser.trim().toLowerCase();
    displayedUploads = displayedUploads.filter((u) =>
      u.user.toLowerCase().includes(term)
    );
  }

  // filter by date range
  const parseDate = (s: string) => (s ? new Date(s) : null);
  const from = parseDate(filterFromDate);
  const to = parseDate(filterToDate);
  if (from) {
    displayedUploads = displayedUploads.filter(
      (u) => new Date(u.timestamp) >= from
    );
  }
  if (to) {
    // include the entire day of 'to'
    const end = new Date(to);
    end.setHours(23, 59, 59, 999);
    displayedUploads = displayedUploads.filter(
      (u) => new Date(u.timestamp) <= end
    );
  }

  // sort array
  displayedUploads.sort((a, b) => {
    switch (sortOption) {
      case 'date_asc':
        return (
          new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
        );
      case 'date_desc':
        return (
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
      case 'user_asc':
        return a.user.localeCompare(b.user);
      case 'user_desc':
        return b.user.localeCompare(a.user);
      default:
        return 0;
    }
  });

  return (
    <div className="py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold mb-8">Admin Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
            value={stats.totalMedia}
            icon={ChartBarIcon}
            color="text-yellow-400"
          />
        </div>

        {/* Recent Activity */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md transition-colors duration-200">
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>

            {/* filter and sort controls */}
            <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
              <div className="flex flex-wrap items-center gap-2">
                <input
                  type="text"
                  placeholder="Filter by user"
                  value={filterUser}
                  onChange={(e) => setFilterUser(e.target.value)}
                  className="px-3 py-2 border rounded-md text-sm w-40"
                />
                <label className="text-sm">From:</label>
                <input
                  type="date"
                  value={filterFromDate}
                  onChange={(e) => setFilterFromDate(e.target.value)}
                  className="px-3 py-2 border rounded-md text-sm"
                />
                <label className="text-sm">To:</label>
                <input
                  type="date"
                  value={filterToDate}
                  onChange={(e) => setFilterToDate(e.target.value)}
                  className="px-3 py-2 border rounded-md text-sm"
                />
              </div>
              <div className="flex items-center space-x-2">
                <label htmlFor="sort" className="text-sm font-medium">
                  Sort by:
                </label>
                <select
                  id="sort"
                  value={sortOption}
                  onChange={(e) => setSortOption(e.target.value as 'date_desc'|'date_asc'|'user_asc'|'user_desc')}
                  className="px-3 py-2 border rounded-md text-sm"
                >
                  <option value="date_desc">Date (newest)</option>
                  <option value="date_asc">Date (oldest)</option>
                  <option value="user_asc">User (A→Z)</option>
                  <option value="user_desc">User (Z→A)</option>
                </select>
              </div>
            </div>

            {displayedUploads.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No recent activity</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="border-b border-gray-200 dark:border-gray-700">
                      <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Title</th>
                      <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">User</th>
                      {/* <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Type</th> */}
                      <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {displayedUploads.map((upload) => (
                      <tr
                        key={upload.id}
                        className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                      >
                        <td className="py-3 px-4">{upload.title}</td>
                        <td className="py-3 px-4">{upload.user}</td>
                        <td className="py-3 px-4">
                          {new Date(upload.timestamp).toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
