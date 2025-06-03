import { useState, useRef } from 'react';
import { useUser } from '@clerk/clerk-react';
import { CloudArrowUpIcon, MicrophoneIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

type SentimentType = 'positive' | 'neutral' | 'negative';

const Upload = () => {
  const { user } = useUser();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [sentiment, setSentiment] = useState<SentimentType>('neutral');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [selectedVoiceNote, setSelectedVoiceNote] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
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
        stream.getTracks().forEach(track => track.stop());
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedImage) {
      toast.error('Please select an image');
      return;
    }

    // TODO: Implement actual upload logic when backend is ready
    toast.success('Upload successful!');
    
    // Reset form
    setTitle('');
    setDescription('');
    setSentiment('neutral');
    setSelectedImage(null);
    setSelectedVoiceNote(null);
    setImagePreview(null);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Upload Media</h1>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Image Upload */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
          <div className="p-6">
            <label className="block mb-2 font-medium">Image</label>
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 border-gray-300 dark:border-gray-600 transition-colors duration-200">
                {imagePreview ? (
                  <img
                    src={imagePreview}
                    alt="Preview"
                    className="w-full h-full object-contain rounded-lg"
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <CloudArrowUpIcon className="w-10 h-10 text-gray-400 mb-3" />
                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                      <span className="font-semibold">Click to upload</span> or drag and drop
                    </p>
                  </div>
                )}
                <input
                  type="file"
                  className="hidden"
                  accept="image/*"
                  onChange={handleImageChange}
                />
              </label>
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
              />
            </div>

            <div>
              <label className="block mb-2 font-medium">Sentiment</label>
              <select
                value={sentiment}
                onChange={(e) => setSentiment(e.target.value as SentimentType)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-yellow-400 focus:border-transparent dark:bg-gray-700 dark:text-white transition-colors duration-200"
              >
                <option value="positive">Positive</option>
                <option value="neutral">Neutral</option>
                <option value="negative">Negative</option>
              </select>
            </div>
          </div>
        </div>

        {/* Voice Note */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
          <div className="p-6">
            <label className="block mb-2 font-medium">Voice Note</label>
            <div className="flex items-center space-x-4">
              <button
                type="button"
                onClick={isRecording ? stopRecording : startRecording}
                className={`flex items-center space-x-2 ${
                  isRecording
                    ? 'bg-red-500 hover:bg-red-600'
                    : 'bg-yellow-400 hover:bg-yellow-500'
                } text-black font-semibold py-2 px-4 rounded-lg transition-colors duration-200`}
              >
                <MicrophoneIcon className="h-5 w-5" />
                <span>{isRecording ? 'Stop Recording' : 'Start Recording'}</span>
              </button>
              {selectedVoiceNote && (
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Voice note recorded
                </span>
              )}
            </div>
          </div>
        </div>

        <button 
          type="submit" 
          className="w-full bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
        >
          Upload Media
        </button>
      </form>
    </div>
  );
};

export default Upload; 