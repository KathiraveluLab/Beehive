import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeftIcon } from '@heroicons/react/24/outline';

interface Upload {
  id: number;
  fileName: string;
  uploadDate: string;
  fileSize: string;
  status: 'processed' | 'pending' | 'failed';
  type: string;
}

// Mock data - replace with actual data from backend
const mockUploads: Upload[] = [
  {
    id: 1,
    fileName: 'health_data_2024.csv',
    uploadDate: '2024-02-01T12:00:00Z',
    fileSize: '2.5 MB',
    status: 'processed',
    type: 'CSV'
  },
  {
    id: 2,
    fileName: 'patient_records.xlsx',
    uploadDate: '2024-02-01T11:30:00Z',
    fileSize: '1.8 MB',
    status: 'pending',
    type: 'Excel'
  },
  // Add more mock uploads as needed
];

const UserUploads = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [uploads, setUploads] = useState<Upload[]>(mockUploads);
  const [userName, setUserName] = useState('User');

  useEffect(() => {
    // TODO: Fetch user details and uploads when backend is ready
    // For now using mock data
  }, [userId]);

  const getStatusColor = (status: Upload['status']) => {
    switch (status) {
      case 'processed':
        return 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100';
      case 'failed':
        return 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  return (
    <div className="py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <motion.button
            onClick={() => navigate('/admin/users')}
            className="flex items-center text-gray-600 hover:text-yellow-500 transition-colors duration-200"
            whileHover={{ x: -4 }}
          >
            <ArrowLeftIcon className="h-5 w-5 mr-2" />
            Back to Users
          </motion.button>
          <h1 className="text-3xl font-bold mt-4">
            Uploads by {userName}
          </h1>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    File Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Upload Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {uploads.map((upload) => (
                  <motion.tr
                    key={upload.id}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">
                        {upload.fileName}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {upload.type}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {new Date(upload.uploadDate).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        {upload.fileSize}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(upload.status)}`}>
                        {upload.status}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserUploads; 