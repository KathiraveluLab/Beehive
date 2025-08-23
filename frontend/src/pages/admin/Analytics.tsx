import { useState } from 'react';
import {
  CalendarIcon,
  ChartBarIcon,
  ChartPieIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from '@heroicons/react/24/outline';

// Mock data - replace with actual data from backend
const mockAnalytics = {
  uploadStats: {
    total: 675,
    increase: 12.5,
    timeframe: 'This month',
    breakdown: {
      images: 450,
      voiceNotes: 225,
    },
  },
  userStats: {
    total: 150,
    increase: 8.3,
    timeframe: 'This month',
    activeUsers: 120,
  },
  sentimentAnalysis: {
    positive: 45,
    neutral: 35,
    negative: 20,
  },
  recentTrends: [
    {
      date: '2024-01',
      uploads: 150,
      users: 45,
    },
    {
      date: '2024-02',
      uploads: 180,
      users: 52,
    },
    {
      date: '2024-03',
      uploads: 210,
      users: 58,
    },
    // Add more trend data as needed
  ],
};

const StatCard = ({
  title,
  value,
  change,
  timeframe,
  icon: Icon,
}: {
  title: string;
  value: number;
  change: number;
  timeframe: string;
  icon: React.ElementType;
}) => (
  <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
          {title}
        </p>
        <p className="text-3xl font-semibold mt-2">{value}</p>
      </div>
      <div className="p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
        <Icon className="h-6 w-6 text-gray-600 dark:text-gray-400" />
      </div>
    </div>
    <div className="mt-4 flex items-center">
      {change > 0 ? (
        <ArrowUpIcon className="h-4 w-4 text-green-500 mr-1" />
      ) : (
        <ArrowDownIcon className="h-4 w-4 text-red-500 mr-1" />
      )}
      <span
        className={`text-sm font-medium ${
          change > 0 ? 'text-green-500' : 'text-red-500'
        }`}
      >
        {Math.abs(change)}%
      </span>
      <span className="text-sm text-gray-600 dark:text-gray-400 ml-2">
        {timeframe}
      </span>
    </div>
  </div>
);

const Analytics = () => {
  const [analytics] = useState(mockAnalytics);

  return (
    <div className="py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold mb-8">Analytics Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Total Uploads"
            value={analytics.uploadStats.total}
            change={analytics.uploadStats.increase}
            timeframe={analytics.uploadStats.timeframe}
            icon={ChartBarIcon}
          />
          <StatCard
            title="Total Users"
            value={analytics.userStats.total}
            change={analytics.userStats.increase}
            timeframe={analytics.userStats.timeframe}
            icon={ChartPieIcon}
          />
          <StatCard
            title="Active Users"
            value={analytics.userStats.activeUsers}
            change={5.2} // Mock change percentage
            timeframe="This week"
            icon={CalendarIcon}
          />
        </div>

        {/* Content Distribution and Sentiment Analysis */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Content Distribution */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
            <h2 className="text-xl font-semibold mb-4">Content Distribution</h2>
            <div className="relative pt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Images</span>
                <span className="text-sm font-medium">
                  {analytics.uploadStats.breakdown.images}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-yellow-400 h-2.5 rounded-full transition-all duration-300 ease-in-out"
                  style={{
                    width: `${
                      (analytics.uploadStats.breakdown.images /
                        analytics.uploadStats.total) *
                      100
                    }%`,
                  }}
                ></div>
              </div>
              <div className="flex items-center justify-between mt-4 mb-2">
                <span className="text-sm font-medium">Voice Notes</span>
                <span className="text-sm font-medium">
                  {analytics.uploadStats.breakdown.voiceNotes}
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-purple-500 h-2.5 rounded-full transition-all duration-300 ease-in-out"
                  style={{
                    width: `${
                      (analytics.uploadStats.breakdown.voiceNotes /
                        analytics.uploadStats.total) *
                      100
                    }%`,
                  }}
                ></div>
              </div>
            </div>
          </div>

          {/* Sentiment Analysis */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
            <h2 className="text-xl font-semibold mb-4">Sentiment Analysis</h2>
            <div className="relative pt-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Positive</span>
                <span className="text-sm font-medium">
                  {analytics.sentimentAnalysis.positive}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-green-500 h-2.5 rounded-full transition-all duration-300 ease-in-out"
                  style={{ width: `${analytics.sentimentAnalysis.positive}%` }}
                ></div>
              </div>
              <div className="flex items-center justify-between mt-4 mb-2">
                <span className="text-sm font-medium">Neutral</span>
                <span className="text-sm font-medium">
                  {analytics.sentimentAnalysis.neutral}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-gray-500 h-2.5 rounded-full transition-all duration-300 ease-in-out"
                  style={{ width: `${analytics.sentimentAnalysis.neutral}%` }}
                ></div>
              </div>
              <div className="flex items-center justify-between mt-4 mb-2">
                <span className="text-sm font-medium">Negative</span>
                <span className="text-sm font-medium">
                  {analytics.sentimentAnalysis.negative}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                <div
                  className="bg-red-500 h-2.5 rounded-full transition-all duration-300 ease-in-out"
                  style={{ width: `${analytics.sentimentAnalysis.negative}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Trends */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
          <h2 className="text-xl font-semibold mb-4">Recent Trends</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Period</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Total Uploads</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Active Users</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Growth</th>
                </tr>
              </thead>
              <tbody>
                {analytics.recentTrends.map((trend, index) => {
                  const prevUploads =
                    index > 0
                      ? analytics.recentTrends[index - 1].uploads
                      : trend.uploads;
                  const growth = ((trend.uploads - prevUploads) / prevUploads) * 100;

                  return (
                    <tr 
                      key={trend.date}
                      className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                    >
                      <td className="py-3 px-4">{trend.date}</td>
                      <td className="py-3 px-4">{trend.uploads}</td>
                      <td className="py-3 px-4">{trend.users}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center">
                          {growth > 0 ? (
                            <ArrowUpIcon className="h-4 w-4 text-green-500 mr-1" />
                          ) : (
                            <ArrowDownIcon className="h-4 w-4 text-red-500 mr-1" />
                          )}
                          <span
                            className={`${
                              growth > 0 ? 'text-green-500' : 'text-red-500'
                            }`}
                          >
                            {Math.abs(growth).toFixed(1)}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics; 