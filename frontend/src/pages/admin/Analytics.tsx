import { useEffect, useState } from "react";
import {
  CalendarIcon,
  ChartBarIcon,
  ChartPieIcon,
  ArrowUpIcon,
  ArrowDownIcon,
} from "@heroicons/react/24/outline";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// Mock data - replace with actual data from backend
// const mockAnalytics = {
//   uploads: {
//     summary: {
//       total: 675,
//       voiceNotes: 225,
//       increase: 12.5,
//       timeframe: "This month",
//       sentimentAnalysis: { positive: 45, neutral: 35, negative: 20 },
//     },
//     trend: [
//       { date: "2024-10-16", uploads: { total: 150, increase: 12.0 } },
//       { date: "2024-10-17", uploads: { total: 180, increase: 20.0 } },
//     ],
//   },
//   users: {
//     summary: {
//       users: { total: 320, increase: 15.0 },
//       activeUsers: { total: 120, increase: 8.3 },
//       timeframe: "This month",
//     },
//     trend: [
//       { date: "2024-10-16", users: { total: 50, increase: 10.0 }, activeUsers: { total: 55, increase: 12.0 } },
//       { date: "2024-10-17", users: { total: 52, increase: 4.0 }, activeUsers: { total: 60, increase: 9.09 } },
//     ],
//   },
// };

const COLORS = ["#10B981", "#6B7280", "#EF4444", "#FBBF24", "#6366F1"];

interface AnalyticsData {
  uploads: {
    summary: {
      total: number;
      voiceNotes: number;
      increase: number;
      timeframe: string;
      sentimentAnalysis: { positive: number; neutral: number; negative: number; custom: number };
    };
    trend: { date: string; uploads: { total: number; increase: number } }[];
  };
  users: {
    summary: {
      users: { total: number; increase: number };
      activeUsers: { total: number; increase: number };
      timeframe: string;
    };
    trend: { date: string; users: { total: number; increase: number }; activeUsers: { total: number; increase: number } }[];
  };
}

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
      {change >= 0 ? (
        <ArrowUpIcon className="h-4 w-4 text-green-500 mr-1" />
      ) : (
        <ArrowDownIcon className="h-4 w-4 text-red-500 mr-1" />
      )}
      <span className={`text-sm font-medium ${change >= 0 ? "text-green-500" : "text-red-500"}`}>
        {Math.abs(change)}%
      </span>
      <span className="text-sm text-gray-600 dark:text-gray-400 ml-2">{timeframe}</span>
    </div>
  </div>
);

const Analytics = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = await window.Clerk.session?.getToken();
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000'}/api/admin/analytics`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        credentials: "include",
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      setAnalytics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch dashboard data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) return (
    <div className="flex justify-center items-center h-32">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400"></div>
    </div>
  );
  if (error) return <p className="text-center mt-10 text-red-500">{error}</p>;
  if (!analytics) return null;

  const uploadSummary = analytics.uploads.summary;
  const userSummary = analytics.users.summary;

  const voiceNoteDistributionData = [
    { name: "Voice Notes", value: uploadSummary.voiceNotes },
    { name: "No Voice Notes", value: uploadSummary.total - uploadSummary.voiceNotes },
  ];

  const sentimentData = [
    { name: "Positive", value: uploadSummary.sentimentAnalysis.positive },
    { name: "Neutral", value: uploadSummary.sentimentAnalysis.neutral },
    { name: "Negative", value: uploadSummary.sentimentAnalysis.negative },
    { name: "Custom", value: uploadSummary.sentimentAnalysis.custom },
  ];

  const uploadTrendMap = new Map(
    analytics.uploads.trend.map(item => [item.date, item.uploads])
  );

  const combinedTrends = analytics.users.trend.map(userTrend => ({
    ...userTrend,
    uploads: uploadTrendMap.get(userTrend.date) || { total: 0, increase: 0 }
  }));

  const isAllZero = (data: { name: string; value: number }[]) =>
    data.every(item => item.value === 0);

  return (
    <div className="py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold mb-8">Analytics Dashboard</h1>

        {/* Stats Grid with updated data paths */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Total Users"
            value={userSummary.users.total}
            change={userSummary.users.increase}
            timeframe={userSummary.timeframe}
            icon={ChartPieIcon}
          />
          <StatCard
            title="Total Uploads"
            value={uploadSummary.total}
            change={uploadSummary.increase}
            timeframe={uploadSummary.timeframe}
            icon={ChartBarIcon}
          />
          <StatCard
            title="Monthly Active Users"
            value={userSummary.activeUsers.total}
            change={userSummary.activeUsers.increase}
            timeframe={userSummary.timeframe}
            icon={CalendarIcon}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Content Distribution */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
            <h2 className="text-xl font-semibold mb-4">Content Distribution</h2>

            {/* Voice Note Distribution */}
            <div className="h-80 flex items-center justify-center">
              {isAllZero(voiceNoteDistributionData) ? (
                <span className="text-gray-400 font-medium">No data available</span>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={voiceNoteDistributionData}
                      dataKey="value"
                      nameKey="name"
                      outerRadius={100}
                      label
                    >
                      {voiceNoteDistributionData.map((_, index) => (
                        <Cell key={index} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>


          {/* Sentiment Analysis */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
            <h2 className="text-xl font-semibold mb-4">Sentiment Analysis</h2>
            <div className="h-80 flex items-center justify-center">
              {isAllZero(sentimentData) ? (
                <span className="text-gray-400 font-medium">No data available</span>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={sentimentData}
                      dataKey="value"
                      nameKey="name"
                      outerRadius={100}
                      label
                    >
                      {sentimentData.map((_, index) => (
                        <Cell key={index} fill={COLORS[index]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>

        {/* Recent Trends */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
          <h2 className="text-xl font-semibold mb-4">Recent Trends (Last Week)</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-gray-200 dark:border-gray-700">
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Period</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Users</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Active Users</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-600 dark:text-gray-400">Uploads</th>
                </tr>
              </thead>
              <tbody>
                {combinedTrends.slice().reverse().map((trendItem) => {
                  const growthIcon = (value: number) => value >= 0 ? (<ArrowUpIcon className="h-4 w-4 text-green-500 inline mr-1" />) : (<ArrowDownIcon className="h-4 w-4 text-red-500 inline mr-1" />);
                  const renderCell = (total: number, increase: number) => (
                    <div className="flex items-center">
                      <span>{total}</span>
                      <span className={`ml-2 flex items-center text-sm font-medium ${increase >= 0 ? 'text-green-500' : 'text-red-500'}`}>{growthIcon(increase)}{Math.abs(increase)}%</span>
                    </div>
                  );
                  return (
                    <tr key={trendItem.date} className="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                      <td className="py-3 px-4">{trendItem.date}</td>
                      <td className="py-3 px-4">{renderCell(trendItem.users.total, trendItem.users.increase)}</td>
                      <td className="py-3 px-4">{renderCell(trendItem.activeUsers.total, trendItem.activeUsers.increase)}</td>
                      <td className="py-3 px-4">{trendItem.uploads ? renderCell(trendItem.uploads.total, trendItem.uploads.increase) : '-'}</td>
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