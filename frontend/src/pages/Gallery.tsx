import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { useUser, useClerk } from '@clerk/clerk-react';
import { useSearchParams } from 'react-router-dom';
import { apiUrl } from '../utils/api';
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
  MagnifyingGlassIcon,
  FunnelIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

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
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
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
  const clerk = useClerk();
  const [searchParams, setSearchParams] = useSearchParams();
  const [images, setImages] = useState<Upload[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [editingImage, setEditingImage] = useState<Upload | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [currentAudio, setCurrentAudio] = useState<string | null>(null);
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list' | 'rolling'>('grid');
  const [gridSize, setGridSize] = useState<'small' | 'medium' | 'large'>('medium');
  const [showLayoutOptions, setShowLayoutOptions] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [currentRollingIndex, setCurrentRollingIndex] = useState(0);
  
  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize] = useState(12);
  const observerTarget = useRef<HTMLDivElement>(null);
  
  // Search and filter states
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [sentiment, setSentiment] = useState(searchParams.get('sentiment') || '');
  const [fromDate, setFromDate] = useState(searchParams.get('from') || '');
  const [toDate, setToDate] = useState(searchParams.get('to') || '');
  const [sortBy, setSortBy] = useState(searchParams.get('sort_by') || 'date');
  const [sortOrder, setSortOrder] = useState(searchParams.get('sort_order') || 'desc');
  const [showFilters, setShowFilters] = useState(false);
  
  const [totalResults, setTotalResults] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const limit = 12;
  
  const searchTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Sync search params to URL (including page)
  useEffect(() => {
    const params: Record<string, string> = {};
    if (searchQuery) params.q = searchQuery;
    if (sentiment) params.sentiment = sentiment;
    if (fromDate) params.from = fromDate;
    if (toDate) params.to = toDate;
    if (sortBy !== 'date') params.sort_by = sortBy;
    if (sortOrder !== 'desc') params.sort_order = sortOrder;
    if (currentPage > 1) params.page = currentPage.toString();
    
    setSearchParams(params, { replace: true });
  }, [searchQuery, sentiment, fromDate, toDate, sortBy, sortOrder, currentPage, setSearchParams]);

  // Sync URL params to state on mount and URL changes
  useEffect(() => {
    const pageParam = searchParams.get('page');
    if (pageParam) {
      const page = parseInt(pageParam, 10);
      if (!isNaN(page) && page > 0) {
        setCurrentPage(page);
      }
    }
  }, [searchParams.get('page')]);

  // Function for authenticated API calls
  const authenticatedFetch = useCallback(async (path: string, options: RequestInit = {}) => {
    const token = await clerk.session?.getToken();
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    };
    return fetch(apiUrl(path), { 
      ...options, 
      headers, 
      credentials: 'include' 
    });
  }, [clerk]);

  // Revoke current audio object URL and clear state
  const revokeCurrentAudioUrl = useCallback(() => {
    setCurrentAudioUrl((url) => {
      if (url) {
        URL.revokeObjectURL(url);
      }
      return null;
    });
  }, []);

  // Fetch uploads with search and filters
  const fetchUploads = useCallback(async (page: number = 1, append: boolean = false) => {
    if (!user?.id) return;
    
    // Cancel previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    // Create new AbortController for this request
    const abortController = new AbortController();
    abortControllerRef.current = abortController;
    
    try {
      if (page === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }
      
      // Check if using search/filter functionality
      const useSearch = searchQuery.trim() || sentiment || fromDate || toDate || sortBy !== 'date' || sortOrder !== 'desc';
      
      let response;
      if (useSearch) {
        // Use offset/limit pagination for search
        const offset = (page - 1) * limit;
        const params = new URLSearchParams({
          limit: limit.toString(),
          offset: offset.toString(),
        });
        
        if (searchQuery.trim()) params.append('q', searchQuery.trim());
        if (sentiment) params.append('sentiment', sentiment);
        if (fromDate) params.append('from', fromDate);
        if (toDate) params.append('to', toDate);
        if (sortBy) params.append('sort_by', sortBy);
        if (sortOrder) params.append('sort_order', sortOrder);
        
        response = await authenticatedFetch(`/api/user/user_uploads?${params}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          mode: 'cors',
          signal: abortController.signal
        });
      } else {
        // Use page-based pagination for simple list
        response = await authenticatedFetch(`/api/user/user_uploads?page=${page}&page_size=${pageSize}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          mode: 'cors',
          signal: abortController.signal
        });
      }
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      
      if (useSearch) {
        // Handle search response format
        setImages(data.images || []);
        setTotalResults(data.total || 0);
        setHasMore(data.hasMore || false);
        setTotalPages(Math.ceil((data.total || 0) / limit));
      } else {
        // Handle page-based response format
        const sortedImages: Upload[] = data.images.sort((a: Upload, b: Upload) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );

        if (append) {
          setImages(prev => [...prev, ...sortedImages]);
        } else {
          setImages(sortedImages);
        }
        
        setTotalPages(data.totalPages || 1);
        setTotalCount(data.total_count || 0);
        setCurrentPage(data.page || 1);
      }
      
      console.log(`Loaded page ${page}, ${data.images?.length || 0} images`);
    } catch (error: any) {
      // Ignore abort errors
      if (error.name === 'AbortError') {
        console.log('Request cancelled');
        return;
      }
      console.error('Error fetching uploads:', error);
      if (page === 1) {
        toast.error('Failed to fetch uploads');
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [user?.id, searchQuery, sentiment, fromDate, toDate, sortBy, sortOrder, authenticatedFetch, pageSize]);

  //Initial fetch and search trigger with debouncing
  useEffect(() => {
    setCurrentPage(1);
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    searchTimeoutRef.current = setTimeout(() => {
      fetchUploads(1, false);
    }, 300);
    
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery, sentiment, fromDate, toDate, sortBy, sortOrder, user?.id, fetchUploads]);

  // Page navigation for search results
  useEffect(() => {
    if (currentPage > 1 && (searchQuery || sentiment || fromDate || toDate || sortBy !== 'date')) {
      fetchUploads(currentPage, false);
    }
  }, [currentPage, fetchUploads, searchQuery, sentiment, fromDate, toDate, sortBy]);

  // Infinite scroll for non-search mode
  useEffect(() => {
    if (viewMode === 'rolling') return;
    if (searchQuery || sentiment || fromDate || toDate || sortBy !== 'date') return; // Disable for search mode

    const observer = new IntersectionObserver(
      (entries) => {
        const target = entries[0];
        if (target.isIntersecting && !loadingMore && !loading && currentPage < totalPages) {
          const nextPage = currentPage + 1;
          console.log(`Loading page ${nextPage}...`);
          fetchUploads(nextPage, true);
        }
      },
      {
        root: null,
        rootMargin: '1200px',
        threshold: 0,
      }
    );

    const currentTarget = observerTarget.current;
    if (currentTarget) {
      observer.observe(currentTarget);
    }

    return () => {
      if (currentTarget) {
        observer.unobserve(currentTarget);
      }
    };
  }, [currentPage, totalPages, loadingMore, loading, fetchUploads, viewMode, searchQuery, sentiment, fromDate, toDate, sortBy]);
  
  const handleClearFilters = () => {
    setSearchQuery('');
    setSentiment('');
    setFromDate('');
    setToDate('');
    setSortBy('date');
    setSortOrder('desc');
    setCurrentPage(1);
  };

  const handleEdit = (image: Upload) => {
    setEditingImage(image);
  };

  const handleSave = async (id: string, title: string, description: string, sentiment: string) => {
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('description', description);
      formData.append('sentiment', sentiment);

      const response = await authenticatedFetch(`/edit/${id}`, {
        method: 'PATCH',
        body: formData,
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
      const response = await authenticatedFetch(`/delete/${id}`, {
        method: 'DELETE',
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
    const url = apiUrl(`/static/uploads/${filename}`);
    window.open(url, '_blank');
    toast.success('File opened in new window!');
  };

  const handleAudioClick = async (audioFilename: string) => {
    // Stop and clear if toggling the same audio
    if (currentAudio === audioFilename) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      setCurrentAudio(null);
      revokeCurrentAudioUrl();
      return;
    }

    // Stop any current playback before loading the next file
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }

    try {
      const response = await authenticatedFetch(`/audio/${audioFilename}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error(`Audio load failed (${response.status})`);
      }

      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);

      setCurrentAudioUrl((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return objectUrl;
      });
      setCurrentAudio(audioFilename);

      if (audioRef.current) {
        audioRef.current.src = objectUrl;
        audioRef.current.play().catch((error) => {
          console.error('Error playing audio:', error);
          toast.error('Error playing audio');
          setCurrentAudio(null);
        });
      }
    } catch (error) {
      console.error('Error fetching audio:', error);
      toast.error('Unable to load audio');
      setCurrentAudio(null);
      revokeCurrentAudioUrl();
    }
  };

  useEffect(() => {
    return () => {
      revokeCurrentAudioUrl();
    };
  }, [revokeCurrentAudioUrl]);

  const renderFilePreview = () => {
    if (!selectedFile) return null;

    const fileUrl = apiUrl(`/static/uploads/${selectedFile}`);
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
      return apiUrl(`/static/uploads/thumbnails/${filename.replace('.pdf', '.jpg')}`);
    }
    // For images, use the original file
    return apiUrl(`/static/uploads/${filename}`);
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

  const filteredImages = useMemo((): Upload[] => {
    const lowercasedQuery = searchQuery.toLowerCase();

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const weekAgo = new Date(today);
    weekAgo.setDate(today.getDate() - 7);
    const monthAgo = new Date(today);
    monthAgo.setDate(today.getDate() - 30);
    const fromDate = customDateFrom ? new Date(customDateFrom) : null;
    if (fromDate) fromDate.setHours(0, 0, 0, 0);
    const toDate = customDateTo ? new Date(customDateTo) : null;
    if (toDate) toDate.setHours(23, 59, 59, 999);

    return images.filter((image) => {
      const matchesSearch = lowercasedQuery === '' || 
        image.title.toLowerCase().includes(lowercasedQuery) || 
        image.description.toLowerCase().includes(lowercasedQuery);
      
      const matchesSentiment = sentimentFilter === 'all' || 
        (sentimentFilter === 'custom' && image.sentiment && !['positive', 'neutral', 'negative'].includes(image.sentiment.toLowerCase())) ||
        (image.sentiment?.toLowerCase() === sentimentFilter.toLowerCase());
      
      let matchesDate = true;
      if (dateFilter !== 'all') {
        const imageDate = new Date(image.created_at);
        if (dateFilter === 'lastWeek') {
          matchesDate = imageDate >= weekAgo;
        } else if (dateFilter === 'lastMonth') {
          matchesDate = imageDate >= monthAgo;
        } else if (dateFilter === 'custom' && fromDate && toDate) {
          matchesDate = imageDate >= fromDate && imageDate <= toDate;
        } else {
          matchesDate = false;
        }
      }
      
      return matchesSearch && matchesSentiment && matchesDate;
    });
  }, [images, searchQuery, sentimentFilter, dateFilter, customDateFrom, customDateTo]);

  const handleRollingNavigation = (direction: 'prev' | 'next') => {
    if (direction === 'prev') {
      setCurrentRollingIndex(prevIndex => (prevIndex === 0 ? filteredImages.length - 1 : prevIndex - 1));
    } else {
      setCurrentRollingIndex(prevIndex => (prevIndex === filteredImages.length - 1 ? 0 : prevIndex + 1));
    }
  };

  useEffect(() => {
    setCurrentRollingIndex(prevIndex => {
      if (prevIndex >= filteredImages.length && filteredImages.length > 0) {
        return 0;
      }
      return prevIndex;
    });
  }, [filteredImages.length]);

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

        <div className="absolute top-4 right-4 z-10">
          <div className="px-4 py-2 rounded-full bg-black/50 backdrop-blur-sm text-white text-sm font-medium">
            {filteredImages.length > 0 ? currentRollingIndex + 1 : 0} / {filteredImages.length}
          </div>
        </div>
        {filteredImages.length === 0 ? (
          <div className="flex items-center justify-center h-[75vh]">
            <p className="text-gray-500 dark:text-gray-400 text-lg">No images match your filters</p>
          </div>
        ) : (
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
                      src={getThumbnailUrl(filteredImages[currentRollingIndex].filename)}
                      alt={filteredImages[currentRollingIndex].title}
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
                        {filteredImages[currentRollingIndex].title}
                      </motion.h3>
                      <motion.p 
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.4 }}
                        className="text-gray-200 text-lg mb-6"
                      >
                        {filteredImages[currentRollingIndex].description}
                      </motion.p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          {filteredImages[currentRollingIndex].sentiment && (
                            <motion.span
                              initial={{ opacity: 0, scale: 0.8 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ delay: 0.5 }}
                              className={`px-4 py-2 rounded-full text-sm font-medium ${getSentimentColor(filteredImages[currentRollingIndex].sentiment)}`}
                            >
                              {filteredImages[currentRollingIndex].sentiment}
                            </motion.span>
                          )}
                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.6 }}
                            className="text-sm text-gray-300"
                          >
                            Uploaded: {new Date(filteredImages[currentRollingIndex].created_at).toLocaleDateString()}
                          </motion.div>
                        </div>
                        
                        <div className="flex items-center space-x-3">
                          <motion.button
                            onClick={() => handleEdit(filteredImages[currentRollingIndex])}
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
                            onClick={() => handleDelete(filteredImages[currentRollingIndex].id)}
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
                            onClick={() => handleDownload(filteredImages[currentRollingIndex].filename)}
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
        )}

        <div className="mt-6 mb-6 flex justify-center space-x-3">
          {filteredImages.map((_, index) => (
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
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">My Gallery</h1>
            {(totalResults > 0 || totalCount > 0) && (
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Showing {images.length} of {totalResults || totalCount} images
              </p>
            )}
          </div>
          
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

        {/* Search and Filter Section */}
        <div className="mb-6 space-y-4">
          {/* Search Bar */}
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by title or description..."
              className="block w-full pl-10 pr-12 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-colors duration-200"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <XMarkIcon className="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300" />
              </button>
            )}
          </div>

          {/* Filter Toggle Button */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center space-x-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
            >
              <FunnelIcon className="h-5 w-5 text-gray-600 dark:text-gray-400" />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                {showFilters ? 'Hide Filters' : 'Show Filters'}
              </span>
              {(sentiment || fromDate || toDate) && (
                <span className="ml-2 px-2 py-0.5 bg-yellow-400 text-black text-xs rounded-full font-medium">
                  Active
                </span>
              )}
            </button>

            {/* Results count */}
            <div className="text-sm text-gray-600 dark:text-gray-400">
              {totalResults > 0 ? (
                <span>
                  Showing {images.length} of {totalResults} upload{totalResults !== 1 ? 's' : ''}
                </span>
              ) : (
                !loading && <span>No uploads found</span>
              )}
            </div>
          </div>

          {/* Advanced Filters */}
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 space-y-4"
            >
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Sentiment Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Sentiment
                  </label>
                  <select
                    value={sentiment}
                    onChange={(e) => setSentiment(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-colors duration-200"
                  >
                    <option value="">All Sentiments</option>
                    <option value="positive">Positive</option>
                    <option value="neutral">Neutral</option>
                    <option value="negative">Negative</option>
                  </select>
                </div>

                {/* From Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    From Date
                  </label>
                  <input
                    type="date"
                    value={fromDate}
                    onChange={(e) => setFromDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-colors duration-200"
                  />
                </div>

                {/* To Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    To Date
                  </label>
                  <input
                    type="date"
                    value={toDate}
                    onChange={(e) => setToDate(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-colors duration-200"
                  />
                </div>

                {/* Sort By */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Sort By
                  </label>
                  <div className="flex space-x-2">
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-yellow-400 focus:border-transparent transition-colors duration-200"
                    >
                      <option value="date">Date</option>
                      <option value="title">Title</option>
                      {searchQuery && <option value="relevance">Relevance</option>}
                    </select>
                    <button
                      onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                      className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors duration-200"
                      title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
                    >
                      {sortOrder === 'asc' ? '↑' : '↓'}
                    </button>
                  </div>
                </div>
              </div>

              {/* Clear Filters Button */}
              <div className="flex justify-end">
                <button
                  onClick={handleClearFilters}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors duration-200"
                >
                  Clear All Filters
                </button>
              </div>
            </motion.div>
          )}
        </div>

        {loading && currentPage === 1 ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-400"></div>
          </div>
        ) : viewMode === 'rolling' ? (
          renderRollingView()
        ) : (
          <>
            <div className={viewMode === 'grid' ? `grid gap-6 ${getGridCols()}` : 'space-y-4'}>
              {filteredImages.length === 0 ? (
                <div className="col-span-full flex items-center justify-center h-64">
                  <p className="text-gray-500 dark:text-gray-400 text-lg">No images match your filters</p>
                </div>
              ) : (
                filteredImages.map((image, index) => (
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
                    viewMode === 'list' ? 'w-32 h-32 flex-shrink-0' : 'w-full aspect-[4/3]'
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
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-opacity duration-200" />
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
                      {currentAudio === image.audio_filename && currentAudioUrl && (
                        <motion.audio
                          ref={audioRef}
                          src={currentAudioUrl}
                          controls
                          className="h-6"
                          onEnded={() => {
                            setCurrentAudio(null);
                            revokeCurrentAudioUrl();
                          }}
                          onError={(e) => {
                            console.error('Audio playback error:', e);
                            toast.error('Error playing audio');
                            setCurrentAudio(null);
                          }}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.2 }}
                        />
                      )}
                    </motion.div>
                  )}
                </div>
              </motion.div>
              ))
            )}
            </div>



            {/* Infinite scroll observer target */}
            <div 
              ref={observerTarget} 
              className="w-full h-4 mt-8"
              aria-label="Infinite scroll trigger"
            />

            {/* Loading indicator */}
            {loadingMore && (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-400"></div>
              </div>
            )}

            {/* End of page indicator */}
            {currentPage >= totalPages && images.length > 0 && (
              <div className="flex justify-center py-8">
                <p className="text-gray-500 dark:text-gray-400 text-center">
                  You've viewed all {totalCount} images
                </p>
              </div>
            )}
          </>
        )}

        {/* Pagination Controls */}
        {!loading && totalResults > limit && (
          <div className="mt-8 flex items-center justify-between border-t border-gray-200 dark:border-gray-700 pt-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className={`relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md ${
                  currentPage === 1
                    ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={!hasMore}
                className={`ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md ${
                  !hasMore
                    ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                Next
              </button>
            </div>

            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Showing <span className="font-medium">{(currentPage - 1) * limit + 1}</span> to{' '}
                  <span className="font-medium">{Math.min(currentPage * limit, totalResults)}</span> of{' '}
                  <span className="font-medium">{totalResults}</span> results
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className={`relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 text-sm font-medium ${
                      currentPage === 1
                        ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                        : 'bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <span className="sr-only">Previous</span>
                    <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
                  </button>

                  {/* Page numbers - Optimized generation */}
                  {(() => {
                    const totalPageCount = Math.ceil(totalResults / limit);
                    const pages: number[] = [];
                    
                    // Always show first page
                    pages.push(1);
                    
                    // Show pages around current page
                    for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPageCount - 1, currentPage + 1); i++) {
                      pages.push(i);
                    }
                    
                    // Always show last page
                    if (totalPageCount > 1) {
                      pages.push(totalPageCount);
                    }
                    
                    // Remove duplicates and sort
                    const uniquePages = Array.from(new Set(pages)).sort((a, b) => a - b);
                    
                    return uniquePages.map((pageNum, index, array) => {
                      // Add ellipsis if needed
                      const showEllipsis = index > 0 && pageNum - array[index - 1] > 1;
                      return (
                        <div key={pageNum} className="inline-flex">
                          {showEllipsis && (
                            <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300">
                              ...
                            </span>
                          )}
                          <button
                            onClick={() => setCurrentPage(pageNum)}
                            className={`relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium ${
                              currentPage === pageNum
                                ? 'z-10 bg-yellow-400 border-yellow-500 text-black'
                                : 'bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                            }`}
                          >
                            {pageNum}
                          </button>
                        </div>
                      );
                    });
                  })()}

                  <button
                    onClick={() => setCurrentPage(currentPage + 1)}
                    disabled={!hasMore}
                    className={`relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 text-sm font-medium ${
                      !hasMore
                        ? 'bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed'
                        : 'bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                    }`}
                  >
                    <span className="sr-only">Next</span>
                    <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
                  </button>
                </nav>
              </div>
            </div>
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