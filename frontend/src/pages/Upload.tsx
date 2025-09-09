import { useState, useRef } from 'react';
import { useUser, useClerk } from '@clerk/clerk-react';
import {
  CloudArrowUpIcon,
  MicrophoneIcon,
  PlayIcon,
  StopIcon,
  ArrowPathIcon,
  EyeIcon,
  TrashIcon,
  XMarkIcon,
  DocumentIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

type SentimentType = 'positive' | 'neutral' | 'negative' | 'custom';

const Upload = () => {
  const { user } = useUser();
  const clerk = useClerk();
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [sentiment, setSentiment] = useState<SentimentType>('neutral');
  const [customSentiment, setCustomSentiment] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [selectedVoiceNote, setSelectedVoiceNote] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPreviewing, setIsPreviewing] = useState(false);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const allowedTypes = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/heif',
        'application/pdf',
      ];
      if (!allowedTypes.includes(file.type)) {
        toast.error('Invalid file type. Please upload an image or PDF.');
        return;
      }

      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveFile = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setIsPreviewing(false);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };

      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioFile = new File([audioBlob], 'voice-note.wav', { type: 'audio/wav' });
        setSelectedVoiceNote(audioFile);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      toast.error('Error accessing microphone');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handlePlayback = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play().catch((error) => {
          console.error('Error playing audio:', error);
          toast.error('Error playing audio');
        });
        setIsPlaying(true);
      }
    }
  };

  const handleRerecord = () => {
    setSelectedVoiceNote(null);
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    setIsPlaying(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!selectedImage) {
      toast.error('Please select a file');
      return;
    }

    if (!user?.id) {
      toast.error('User not authenticated');
      return;
    }

    try {
      setIsUploading(true);
      const formData = new FormData();
      formData.append('username', user.firstName + ' ' + user.lastName);
      formData.append('files', selectedImage);
      formData.append('title', title);
      formData.append('description', description);
      formData.append('sentiment', sentiment === 'custom' ? customSentiment : sentiment);

      if (selectedVoiceNote) {
        const audioReader = new FileReader();
        audioReader.readAsDataURL(selectedVoiceNote);
        await new Promise((resolve, reject) => {
          audioReader.onloadend = async () => {
            try {
              formData.append('audioData', audioReader.result as string);
              resolve(null);
            } catch (error) {
              reject(error);
            }
          };
          audioReader.onerror = reject;
        });
      }

      const token = await clerk.session?.getToken();
      const response = await fetch(`http://127.0.0.1:5000/api/user/upload/${user.id}`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
        credentials: 'include',
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
      }

      toast.success('Upload successful!');
      navigate('/gallery');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error instanceof Error ? error.message : 'Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto py-8">
      <h1 className="text-3xl font-bold mb-8">Upload Media</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Image or PDF Upload */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
          <div className="p-6">
            <label className="block mb-2 font-medium">Image or PDF</label>
            <div className="flex items-center justify-center w-full">
              {selectedImage ? (
                <div className="flex items-center justify-between w-full p-4 border-2 border-gray-300 dark:border-gray-600 rounded-lg">
                  <div className="flex items-center gap-3">
                    <DocumentIcon className="h-6 w-6 text-gray-500" />
                    <span className="text-sm font-medium truncate">{selectedImage.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setIsPreviewing(true)}
                      className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                      title="Preview File"
                    >
                      <EyeIcon className="h-5 w-5" />
                    </button>
                    <button
                      type="button"
                      onClick={handleRemoveFile}
                      className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                      title="Remove File"
                    >
                      <TrashIcon className="h-5 w-5 text-red-500" />
                    </button>
                  </div>
                </div>
              ) : (
                <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 border-gray-300 dark:border-gray-600 transition-colors duration-200">
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <CloudArrowUpIcon className="w-10 h-10 text-gray-400 mb-3" />
                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                      <span className="font-semibold">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      PNG, JPG, GIF, WEBP, HEIF or PDF
                    </p>
                  </div>
                  <input
                    type="file"
                    className="hidden"
                    accept="image/*,.pdf"
                    onChange={handleImageChange}
                  />
                </label>
              )}
            </div>
          </div>
        </div>

        {/* Title and Description */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
          <div className="p-6 space-y-4">
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
                required
              />
            </div>
            <div>
              <label className="block mb-2 font-medium">Sentiment</label>
              <div className="space-y-2">
                <select
                  value={sentiment}
                  onChange={(e) => setSentiment(e.target.value as SentimentType)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent dark:bg-gray-700 dark:text-white transition-colors duration-200"
                >
                  <option value="positive">Positive</option>
                  <option value="neutral">Neutral</option>
                  <option value="negative">Negative</option>
                  <option value="custom">Custom</option>
                </select>
                {sentiment === 'custom' && (
                  <input
                    type="text"
                    value={customSentiment}
                    onChange={(e) => setCustomSentiment(e.target.value)}
                    placeholder="Enter custom sentiment"
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent dark:bg-gray-700 dark:text-white transition-colors duration-200"
                    required
                  />
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Voice Note */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
          <div className="p-6">
            <label className="block mb-2 font-medium">Voice Note (Optional)</label>
            <div className="space-y-4">
              <div className="flex flex-wrap items-center gap-4">
                <button
                  type="button"
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`flex items-center space-x-2 ${
                    isRecording
                      ? 'bg-red-500 hover:bg-red-600'
                      : 'bg-yellow-400 hover:bg-yellow-500'
                  } text-black font-semibold py-2 px-4 rounded-lg transition-colors duration-200`}
                >
                  {isRecording ? (
                    <>
                      <StopIcon className="h-5 w-5" />
                      <span>Stop Recording</span>
                    </>
                  ) : (
                    <>
                      <MicrophoneIcon className="h-5 w-5" />
                      <span>Start Recording</span>
                    </>
                  )}
                </button>
                {selectedVoiceNote && (
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={handlePlayback}
                      className="p-2 rounded-full bg-yellow-400 hover:bg-yellow-500 text-black transition-colors duration-200"
                      title={isPlaying ? 'Pause' : 'Play'}
                    >
                      {isPlaying ? <StopIcon className="h-5 w-5" /> : <PlayIcon className="h-5 w-5" />}
                    </button>
                    <button
                      type="button"
                      onClick={handleRerecord}
                      className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 transition-colors duration-200"
                      title="Record Again"
                    >
                      <ArrowPathIcon className="h-5 w-5" />
                    </button>
                    <audio
                      ref={audioRef}
                      src={selectedVoiceNote ? URL.createObjectURL(selectedVoiceNote) : ''}
                      className="hidden"
                      onEnded={() => setIsPlaying(false)}
                      onError={(e) => {
                        console.error('Audio error:', e);
                        toast.error('Error playing audio');
                        setIsPlaying(false);
                      }}
                    />
                  </div>
                )}
              </div>
              {selectedVoiceNote && (
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Voice note recorded. Click play to preview or the refresh icon to record again.
                </div>
              )}
            </div>
          </div>
        </div>

        <button
          type="submit"
          disabled={isUploading}
          className={`w-full bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 px-4 rounded-lg transition-colors duration-200 ${
            isUploading ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          {isUploading ? 'Uploading...' : 'Upload Media'}
        </button>
      </form>

      {/* Preview Modal */}
      {isPreviewing && imagePreview && selectedImage && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-75"
          onClick={() => setIsPreviewing(false)}
        >
          <div
            className="relative bg-white dark:bg-gray-800 rounded-lg shadow-xl w-11/12 max-w-4xl h-5/6"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={() => setIsPreviewing(false)}
              className="absolute -top-3 -right-3 z-10 p-1 bg-white rounded-full text-black shadow-lg"
              title="Close Preview"
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
            {selectedImage.type === 'application/pdf' ? (
              <iframe
                src={imagePreview}
                className="w-full h-full rounded-lg"
                title="PDF Preview"
              />
            ) : (
              <img
                src={imagePreview}
                alt="Preview"
                className="w-full h-full object-contain rounded-lg"
              />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Upload;