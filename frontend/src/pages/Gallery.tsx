import { useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import {
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  SpeakerWaveIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

// Mock data - replace with actual data from backend
const mockImages = [
  {
    id: 1,
    title: 'Beautiful Sunset',
    description: 'Captured this amazing sunset at the beach',
    imageUrl: 'https://source.unsplash.com/random/800x600?sunset',
    sentiment: 'positive',
    hasVoiceNote: true,
    createdAt: '2024-02-01T12:00:00Z',
  },
  {
    id: 2,
    title: 'City Lights',
    description: 'Night view of the city skyline',
    imageUrl: 'https://source.unsplash.com/random/800x600?city',
    sentiment: 'neutral',
    hasVoiceNote: false,
    createdAt: '2024-02-02T12:00:00Z',
  },
  // Add more mock images as needed
];

interface EditModalProps {
  image: typeof mockImages[0];
  onClose: () => void;
  onSave: (id: number, title: string, description: string) => void;
}

const EditModal = ({ image, onClose, onSave }: EditModalProps) => {
  const [title, setTitle] = useState(image.title);
  const [description, setDescription] = useState(image.description);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(image.id, title, description);
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
  const [images] = useState(mockImages);
  const [editingImage, setEditingImage] = useState<typeof mockImages[0] | null>(null);

  const handleEdit = (image: typeof mockImages[0]) => {
    setEditingImage(image);
  };

  const handleSave = (id: number, title: string, description: string) => {
    // TODO: Implement actual update logic when backend is ready
    toast.success('Changes saved successfully!');
  };

  const handleDelete = (id: number) => {
    // TODO: Implement actual delete logic when backend is ready
    toast.success('Image deleted successfully!');
  };

  const handleDownload = (imageUrl: string, title: string) => {
    // TODO: Implement actual download logic when backend is ready
    toast.success('Download started!');
  };

  const handlePlayVoiceNote = (id: number) => {
    // TODO: Implement actual voice note playback when backend is ready
    toast.success('Playing voice note...');
  };

  return (
    <div className="py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold mb-8">My Gallery</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {images.map((image) => (
            <div key={image.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden transition-colors duration-200">
              <img
                src={image.imageUrl}
                alt={image.title}
                className="w-full h-48 object-cover"
              />
              <div className="p-4">
                <h3 className="text-xl font-semibold mb-2">{image.title}</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  {image.description}
                </p>
                <div className="flex items-center justify-between">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(image)}
                      className="p-2 text-gray-600 hover:text-yellow-400 dark:text-gray-400 transition-colors duration-200"
                      title="Edit"
                    >
                      <PencilIcon className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(image.id)}
                      className="p-2 text-gray-600 hover:text-red-500 dark:text-gray-400 transition-colors duration-200"
                      title="Delete"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => handleDownload(image.imageUrl, image.title)}
                      className="p-2 text-gray-600 hover:text-yellow-400 dark:text-gray-400 transition-colors duration-200"
                      title="Download"
                    >
                      <ArrowDownTrayIcon className="h-5 w-5" />
                    </button>
                  </div>
                  {image.hasVoiceNote && (
                    <button
                      onClick={() => handlePlayVoiceNote(image.id)}
                      className="p-2 text-gray-600 hover:text-yellow-400 dark:text-gray-400 transition-colors duration-200"
                      title="Play Voice Note"
                    >
                      <SpeakerWaveIcon className="h-5 w-5" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {editingImage && (
          <EditModal
            image={editingImage}
            onClose={() => setEditingImage(null)}
            onSave={handleSave}
          />
        )}
      </div>
    </div>
  );
};

export default Gallery; 