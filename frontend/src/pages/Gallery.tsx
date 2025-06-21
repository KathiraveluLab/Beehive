import { useState, useEffect, useRef } from 'react';
import { useUser } from '@clerk/clerk-react';
import {
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  SpeakerWaveIcon,
  XMarkIcon,
  Squares2X2Icon,
  ListBulletIcon,
  AdjustmentsHorizontalIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';

interface Upload {
  id: string;
  filename: string;
  title: string;
  description: string;
  created_at: string;
  audio_filename?: string;
  sentiment?: string;
}

interface EditModalProps {
  image: Upload;
  onClose: () => void;
  onSave: (id: string, title: string, description: string, sentiment: string) => void;
}

const EditModal = ({ image, onClose, onSave }: EditModalProps) => {
  const [title, setTitle] = useState(image.title);
  const [description, setDescription] = useState(image.description);
  const [sentiment, setSentiment] = useState(image.sentiment || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(image.id, title, description, sentiment);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-lg w-full transition-colors duration-200">
        <form onSubmit={handleSubmit} className="p-6">
          <h2 className="text-2xl font-bold mb-4">Edit Image</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block mb-2 font-medium">Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent dark:bg-gray-700 dark:text-white transition-colors duration-200"
                required
              />
            </div>

            <div>
              <label className="block mb-2 font-medium">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent dark:bg-gray-700 dark:text-white transition-colors duration-200 min-h-[100px]"
              />
            </div>

            <div>
              <label className="block mb-2 font-medium">Sentiment</label>
              <select
                value={sentiment}
                onChange={(e) => setSentiment(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent dark:bg-gray-700 dark:text-white transition-colors duration-200"
              >
                <option value="">Select Sentiment</option>
                <option value="positive">Positive</option>
                <option value="negative">Negative</option>
                <option value="neutral">Neutral</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-4 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const Gallery = () => {
  const { user } = useUser();
  const [images, setImages] = useState<Upload[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingImage, setEditingImage] = useState<Upload | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentAudio, setCurrentAudio] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'rolling'>('grid');
  const [gridSize, setGridSize] = useState<'small' | 'medium' | 'large'>('medium');
  const [showLayoutOptions, setShowLayoutOptions] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [currentRollingIndex, setCurrentRollingIndex] = useState(0);
  const rollingContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchUploads = async () => {
      if (!user?.id) return;
      
      try {
        setLoading(true);
        const response = await fetch(`http://127.0.0.1:5000/api/user/user_uploads/${user.id}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          mode: 'cors'
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }
        
        setImages(data.images);
        console.log(data.images);
      } catch (error) {
        console.error('Error fetching uploads:', error);
          toast.error('Failed to fetch uploads');
      } finally {
        setLoading(false);
      }
    };

    fetchUploads();
  }, [user?.id]);

  const handleEdit = (image: Upload) => {
    setEditingImage(image);
  };

  const handleSave = async (id: string, title: string, description: string, sentiment: string) => {
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('sentiment', sentiment);

      const response = await fetch(`http://127.0.0.1:5000/edit/${id}`, {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to update image');
      }

      setImages(images.map(img => 
        img.id === id ? { ...img, title, description, sentiment } : img
      ));

      toast.success('Changes saved successfully!');
    } catch (error) {
      console.error('Error updating image:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to save changes');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this image?')) {
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:5000/delete/${id}`, {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to delete image');
      }

      setImages(images.filter(img => img.id !== id));
      toast.success('Image deleted successfully!');
    } catch (error) {
      console.error('Error deleting image:', error);
      toast.error(error instanceof Error ? error.message : 'Failed to delete image');
    }
  };

  const handleFileClick = (filename: string) => {
    setSelectedFile(filename);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
  };

  const handleDownload = (filename: string) => {
    const url = `http://127.0.0.1:5000/static/uploads/${filename}`;
    window.open(url, '_blank');
    toast.success('File opened in new window!');
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

  const renderFilePreview = () => {
    if (!selectedFile) return null;

    const fileUrl = `http://127.0.0.1:5000/static/uploads/${selectedFile}`;
    const isPDF = selectedFile.toLowerCase().endsWith('.pdf');

    if (isPDF) {
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

  const getThumbnailUrl = (filename: string) => {
    if (filename.toLowerCase().endsWith('.pdf')) {
      // For PDFs, use the thumbnail
      return `http://127.0.0.1:5000/static/uploads/thumbnails/${filename.replace('.pdf', '.jpg')}`;
    }
    // For images, use the original file
    return `http://127.0.0.1:5000/static/uploads/${filename}`;
  };

  const getSentimentColor = (sentiment?: string) => {
    if (!sentiment) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100';
      case 'negative':
        return 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100';
      case 'neutral':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  const getGridCols = () => {
    switch (gridSize) {
      case 'small':
        return 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4';
      case 'medium':
        return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';
      case 'large':
        return 'grid-cols-1 md:grid-cols-2';
      default:
        return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3';
    }
  };

  const getCardSize = () => {
    switch (gridSize) {
      case 'small':
        return 'h-40';
      case 'medium':
        return 'h-48';
      case 'large':
        return 'h-64';
      default:
        return 'h-48';
    }
  };

  const handleRollingNavigation = (direction: 'prev' | 'next') => {
    if (direction === 'prev') {
      setCurrentRollingIndex(prevIndex => (prevIndex === 0 ? images.length - 1 : prevIndex - 1));
    } else {
      setCurrentRollingIndex(prevIndex => (prevIndex === images.length - 1 ? 0 : prevIndex + 1));
    }
  };

  const renderRollingView = () => {
    return (
      <div className="relative w-full mx-auto overflow-hidden">
        {/* Enhanced Navigation Controls */}
        <div className="absolute top-1/2 -translate-y-1/2 lg:left-1 lg:right-1 left-0 right-0 z-10 flex justify-between pointer-events-none">
          <motion.button
            onClick={() => handleRollingNavigation('prev')}
            className="p-3 rounded-full bg-yellow-400 backdrop-blur-sm hover:bg-yellow-500 text-white shadow-lg pointer-events-auto transition-all duration-200 group"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <ChevronLeftIcon className="h-6 w-6" />
            <span className="absolute left-full ml-2 px-2 py-1 bg-black/80 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
              Previous
            </span>
          </motion.button>
          <motion.button
            onClick={() => handleRollingNavigation('next')}
            className="p-3 rounded-full bg-yellow-400 backdrop-blur-sm hover:bg-yellow-500 text-white shadow-lg pointer-events-auto transition-all duration-200 group"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <ChevronRightIcon className="h-6 w-6" />
            <span className="absolute right-full mr-2 px-2 py-1 bg-black/80 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
              Next
            </span>
          </motion.button>
        </div>

        {/* Image Counter */}
        <div className="absolute top-4 right-4 z-10">
          <div className="px-4 py-2 rounded-full bg-black/50 backdrop-blur-sm text-white text-sm font-medium">
            {currentRollingIndex + 1} / {images.length}
          </div>
        </div>

        {/* Main Image Display */}
        <div className="relative h-[75vh] w-full">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentRollingIndex}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05 }}
              transition={{ duration: 0.4, ease: "easeOut" }}
              className="absolute inset-0 flex items-center justify-center"
            >
              <div className="relative w-full h-full max-w-5xl mx-auto">
                <div className="relative w-full h-full rounded-2xl overflow-hidden shadow-2xl">
                  <img
                    src={getThumbnailUrl(images[currentRollingIndex].filename)}
                    alt={images[currentRollingIndex].title}
                    className="w-full h-full object-contain bg-gray-100 dark:bg-gray-800"
                  />
                  
                  {/* Enhanced Overlay */}
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/50 to-transparent p-8"
                  >
                    <div className="max-w-3xl mx-auto">
                      <motion.h3 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="text-3xl font-bold text-white mb-3"
                      >
                        {images[currentRollingIndex].title}
                      </motion.h3>
                      <motion.p 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="text-gray-200 text-lg mb-6"
                      >
                        {images[currentRollingIndex].description}
                      </motion.p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          {images[currentRollingIndex].sentiment && (
                            <motion.span
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: 0.5 }}
                              className={`px-4 py-2 rounded-full text-sm font-medium ${getSentimentColor(images[currentRollingIndex].sentiment)}`}
                            >
                              {images[currentRollingIndex].sentiment}
                            </motion.span>
                          )}
                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.6 }}
                            className="text-sm text-gray-300"
                          >
                            Uploaded: {new Date(images[currentRollingIndex].created_at).toLocaleDateString()}
                          </motion.div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          <motion.button
                            onClick={() => handleEdit(images[currentRollingIndex])}
                            className="p-2.5 rounded-full bg-white/20 hover:bg-white/30 text-white transition-all duration-200 group"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <PencilIcon className="h-5 w-5" />
                            <span className="absolute bottom-full mb-2 px-2 py-1 bg-black/80 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                              Edit
                            </span>
                          </motion.button>
                          <motion.button
                            onClick={() => handleDelete(images[currentRollingIndex].id)}
                            className="p-2.5 rounded-full bg-white/20 hover:bg-white/30 text-white transition-all duration-200 group"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <TrashIcon className="h-5 w-5" />
                            <span className="absolute bottom-full mb-2 px-2 py-1 bg-black/80 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                              Delete
                            </span>
                          </motion.button>
                          <motion.button
                            onClick={() => handleDownload(images[currentRollingIndex].filename)}
                            className="p-2.5 rounded-full bg-white/20 hover:bg-white/30 text-white transition-all duration-200 group"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                          >
                            <ArrowDownTrayIcon className="h-5 w-5" />
                            <span className="absolute bottom-full mb-2 px-2 py-1 bg-black/80 text-white text-sm rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap">
                              Download
                            </span>
                          </motion.button>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Enhanced Dot Navigation */}
        <div className="mt-6 mb-6 flex justify-center space-x-3">
          {images.map((_, index) => (
            <motion.button
              key={index}
              onClick={() => setCurrentRollingIndex(index)}
              className={`w-3 h-3 rounded-full transition-all duration-200 ${
                index === currentRollingIndex
                  ? 'bg-yellow-400 scale-125'
                  : 'bg-gray-300 dark:bg-gray-600 hover:bg-gray-400 dark:hover:bg-gray-500'
              }`}
              whileHover={{ scale: 1.2 }}
              whileTap={{ scale: 0.9 }}
            />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="py-8 bg-gray-50 dark:bg-gray-900 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Gallery</h1>
          
          <div className="flex items-center space-x-4">
            <div className="relative">
              <button
                onClick={() => setShowLayoutOptions(!showLayoutOptions)}
                className="p-2 rounded-lg bg-white dark:bg-gray-800 shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                title="Layout Options"
              >
                <AdjustmentsHorizontalIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              </button>
              
              {showLayoutOptions && (
                <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg py-2 z-10">
                  <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300">Grid Size</p>
                  </div>
                  <div className="px-4 py-2">
                    {['small', 'medium', 'large'].map((size) => (
                      <button
                        key={size}
                        onClick={() => {
                          setGridSize(size as 'small' | 'medium' | 'large');
                          setShowLayoutOptions(false);
                        }}
                        className={`w-full text-left px-2 py-1 rounded-md text-sm ${
                          gridSize === size
                            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100'
                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                      >
                        {size.charAt(0).toUpperCase() + size.slice(1)}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex rounded-lg bg-white dark:bg-gray-800 shadow-sm p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded-md transition-colors duration-200 ${
                  viewMode === 'grid'
                    ? 'bg-yellow-400 text-black'
                    : 'text-gray-600 hover:text-yellow-400 dark:text-gray-400'
                }`}
                title="Grid View"
              >
                <Squares2X2Icon className="h-5 w-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded-md transition-colors duration-200 ${
                  viewMode === 'list'
                    ? 'bg-yellow-400 text-black'
                    : 'text-gray-600 hover:text-yellow-400 dark:text-gray-400'
                }`}
                title="List View"
              >
                <ListBulletIcon className="h-5 w-5" />
              </button>
              <button
                onClick={() => setViewMode('rolling')}
                className={`p-2 rounded-md transition-colors duration-200 ${
                  viewMode === 'rolling'
                    ? 'bg-yellow-400 text-black'
                    : 'text-gray-600 hover:text-yellow-400 dark:text-gray-400'
                }`}
                title="Rolling View"
              >
                <ChevronRightIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
          </div>
        ) : viewMode === 'rolling' ? (
          renderRollingView()
        ) : (
          <div className={viewMode === 'grid' ? `grid gap-6 ${getGridCols()}` : 'space-y-4'}>
            {images.map((image, index) => (
              <motion.div
                key={image.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{
                  duration: 0.3,
                  delay: index * 0.1,
                  ease: "easeOut"
                }}
                whileHover={{ scale: 1.02 }}
                className={`bg-white dark:bg-gray-800 rounded-xl shadow-sm overflow-hidden transition-all duration-200 hover:shadow-md ${
                  viewMode === 'list' ? 'flex items-center' : ''
                }`}
              >
                <motion.div
                  className={`relative cursor-pointer group ${
                    viewMode === 'list' ? 'w-32 h-32 flex-shrink-0' : 'w-full'
                  }`}
                  onClick={() => handleFileClick(image.filename)}
                  whileHover={{ scale: 1.05 }}
                  transition={{ duration: 0.2 }}
                >
                  <img
                    src={getThumbnailUrl(image.filename)}
                    alt={image.title}
                    className={`w-full h-full object-cover transition-transform duration-200`}
                  />
                  {image.sentiment && (
                    <motion.span
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(image.sentiment)}`}
                    >
                      {image.sentiment}
                    </motion.span>
                  )}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-opacity duration-200" />
                </motion.div>

                <div className={`p-4 ${viewMode === 'list' ? 'flex-grow flex flex-col justify-between min-w-0' : ''}`}>
                  <div className="flex-grow">
                    <div className="flex items-start justify-between gap-4">
                      <div className="min-w-0 flex-1">
                        <motion.h3 
                          className="text-lg font-semibold mb-1 text-gray-900 dark:text-white truncate"
                          whileHover={{ x: 5 }}
                          transition={{ duration: 0.2 }}
                        >
                          {image.title}
                        </motion.h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                          {image.description}
                        </p>
                        {viewMode === 'list' && (
                          <motion.div 
                            className="text-xs text-gray-500 dark:text-gray-400 mt-1"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.2 }}
                          >
                            Uploaded: {new Date(image.created_at).toLocaleDateString()}
                          </motion.div>
                        )}
                      </div>
                      <div className="flex items-center space-x-2 flex-shrink-0">
                        <motion.button
                          onClick={() => handleEdit(image)}
                          className="p-1.5 text-gray-600 hover:text-yellow-400 dark:text-gray-400 transition-colors duration-200"
                          title="Edit"
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <PencilIcon className="h-4 w-4" />
                        </motion.button>
                        <motion.button
                          onClick={() => handleDelete(image.id)}
                          className="p-1.5 text-gray-600 hover:text-red-500 dark:text-gray-400 transition-colors duration-200"
                          title="Delete"
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <TrashIcon className="h-4 w-4" />
                        </motion.button>
                        <motion.button
                          onClick={() => handleDownload(image.filename)}
                          className="p-1.5 text-gray-600 hover:text-yellow-400 dark:text-gray-400 transition-colors duration-200"
                          title="Download"
                          whileHover={{ scale: 1.1 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <ArrowDownTrayIcon className="h-4 w-4" />
                        </motion.button>
                      </div>
                    </div>
                  </div>

                  {image.audio_filename && (
                    <motion.div 
                      className="flex items-center space-x-2 mt-2"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                    >
                      <motion.button
                        onClick={() => handleAudioClick(image.audio_filename!)}
                        className={`p-1.5 rounded-full transition-colors duration-200 ${
                          currentAudio === image.audio_filename
                            ? 'bg-yellow-400 text-black'
                            : 'text-gray-600 hover:text-yellow-400 dark:text-gray-400'
                        }`}
                        title="Play Voice Note"
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.95 }}
                      >
                        <SpeakerWaveIcon className="h-4 w-4" />
                      </motion.button>
                      {currentAudio === image.audio_filename && (
                        <motion.audio
                          ref={audioRef}
                          src={`http://127.0.0.1:5000/audio/${image.audio_filename}`}
                          controls
                          className="h-6"
                          onEnded={() => setCurrentAudio(null)}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.2 }}
                        />
                      )}
                    </motion.div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {editingImage && (
          <EditModal
            image={editingImage}
            onClose={() => setEditingImage(null)}
            onSave={handleSave}
          />
        )}

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
    </div>
  );
};

export default Gallery; 