import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useClerk } from '@clerk/clerk-react';
import { motion } from 'framer-motion';
import { ArrowLeftIcon, XMarkIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

interface Upload {
  id: string;
  filename: string;
  title: string;
  description: string;
  created_at: string;
  audio_filename?: string;
  sentiment?: string;
}

const UserUploads = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const clerk = useClerk();
  const [uploads, setUploads] = useState<Upload[]>([]);
  const [userName, setUserName] = useState('User');
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [currentAudio, setCurrentAudio] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    const fetchUploads = async () => {
      try {
        setLoading(true);
        
        // Get the authentication token from Clerk
        const token = await clerk.session?.getToken();
        
        const response = await fetch(`http://127.0.0.1:5000/api/admin/user_uploads/${userId}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          credentials: 'include',
          mode: 'cors'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(data);
        if (data.error) {
          throw new Error(data.error);
        }
        
        const sortedImages: Upload[] = data.images.sort((a: Upload, b: Upload) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        setUploads(sortedImages);
      } catch (error) {
        console.error('Error fetching uploads:', error);
        toast.error('Failed to fetch uploads');
      } finally {
        setLoading(false);
      }
    };
    fetchUploads();
  }, [userId]);

  const handleFileClick = (filename: string) => {
    setSelectedFile(filename);
    setIsModalOpen(true);
  };

  const handleAudioClick = (audioFilename: string) => {
    if (currentAudio === audioFilename) {
      // If clicking the same audio, stop it
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      setCurrentAudio(null);
    } else {
      // If clicking a different audio, stop current and play new
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      setCurrentAudio(audioFilename);
    }
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
  };

  const isPDF = (filename: string) => {
    return filename.toLowerCase().endsWith('.pdf');
  };

  const renderFilePreview = () => {
    if (!selectedFile) return null;

    const fileUrl = `http://127.0.0.1:5000/static/uploads/${selectedFile}`;

    if (isPDF(selectedFile)) {
      return (
        <iframe
          src={fileUrl}
          className="w-full h-[80vh]"
          title="PDF Preview"
        />
      );
    }

    return (
      <img
        src={fileUrl}
        alt="Uploaded file"
        className="max-w-full h-auto mx-auto"
      />
    );
  };

  const handleDownload = (filename: string, type: 'file' | 'audio') => {
    const url = `http://127.0.0.1:5000/static/uploads/${filename}`;
    window.open(url, '_blank');
    toast.success(`${type === 'file' ? 'File' : 'Audio'} opened in new window!`);
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
            {loading ? (
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400"></div>
              </div>
            ) : (
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-yellow-200 dark:bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black dark:text-gray-400 uppercase tracking-wider">
                      Title
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black dark:text-gray-400 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black dark:text-gray-400 uppercase tracking-wider">
                      Upload Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black dark:text-gray-400 uppercase tracking-wider">
                      Sentiment
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black dark:text-gray-400 uppercase tracking-wider">
                      Audio
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-black dark:text-gray-400 uppercase tracking-wider">
                      Actions
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
                        <button
                          onClick={() => handleFileClick(upload.filename)}
                          className="text-sm font-medium text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                        >
                          {upload.title}
                        </button>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {upload.description}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {new Date(upload.created_at).toLocaleString()}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {upload.sentiment || 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {upload.audio_filename ? (
                          <div className="flex flex-col space-y-2">
                            <button
                              onClick={() => handleAudioClick(upload.audio_filename!)}
                              className={`inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium transition-colors duration-200 ${
                                currentAudio === upload.audio_filename 
                                  ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-100 dark:hover:bg-red-800' 
                                  : 'bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-100 dark:hover:bg-blue-800'
                              }`}
                            >
                              {currentAudio === upload.audio_filename ? 'Hide Player' : 'Show Player'}
                            </button>
                            {currentAudio === upload.audio_filename && (
                              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-3 border border-gray-200 dark:border-gray-700">
                                <audio
                                  ref={audioRef}
                                  controls
                                  className="w-full [&::-webkit-media-controls-panel]:bg-gray-100 dark:[&::-webkit-media-controls-panel]:bg-gray-800 [&::-webkit-media-controls-current-time-display]:text-gray-700 dark:[&::-webkit-media-controls-current-time-display]:text-gray-300 [&::-webkit-media-controls-time-remaining-display]:text-gray-700 dark:[&::-webkit-media-controls-time-remaining-display]:text-gray-300 [&::-webkit-media-controls-timeline]:bg-gray-300 dark:[&::-webkit-media-controls-timeline]:bg-gray-600 [&::-webkit-media-controls-volume-slider]:bg-gray-300 dark:[&::-webkit-media-controls-volume-slider]:bg-gray-600"
                                  src={`http://127.0.0.1:5000/static/uploads/${upload.audio_filename}`}
                                  onEnded={() => setCurrentAudio(null)}
                                >
                                  Your browser does not support the audio element.
                                </audio>
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            N/A
                          </div>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => handleDownload(upload.filename, 'file')}
                            className="inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium bg-yellow-100 text-yellow-700 hover:bg-yellow-200 dark:bg-yellow-900 dark:text-yellow-100 dark:hover:bg-yellow-800 transition-colors duration-200"
                            title="Download File"
                          >
                            <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                            File
                          </button>
                          {upload.audio_filename && (
                            <button
                              onClick={() => handleDownload(upload.audio_filename!, 'audio')}
                              className="inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-100 dark:hover:bg-blue-800 transition-colors duration-200"
                              title="Download Audio"
                            >
                              <ArrowDownTrayIcon className="h-4 w-4 mr-1" />
                              Audio
                            </button>
                          )}
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {/* File Preview Modal */}
      {isModalOpen && selectedFile && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 dark:bg-gray-900 opacity-75"></div>
            </div>

            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

            <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="absolute top-0 right-0 pt-4 pr-4">
                <button
                  onClick={closeModal}
                  className="bg-white dark:bg-gray-800 rounded-md text-gray-400 hover:text-gray-500 focus:outline-none"
                >
                  <span className="sr-only">Close</span>
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
              <div className="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="mt-3 text-center sm:mt-0 sm:text-left">
                  <div className="mt-2">
                    {renderFilePreview()}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserUploads; 