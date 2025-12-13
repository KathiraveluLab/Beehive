import { useEffect, useRef, useState } from 'react';
import ImageEditor from 'tui-image-editor';
import 'tui-image-editor/dist/tui-image-editor.css';
import toast from 'react-hot-toast';
import { XMarkIcon } from '@heroicons/react/24/outline'; 

interface ImageEditorProps {
  imageFile: File;
  imagePreview: string;
  onSave: (editedImage: File) => void;
  onCancel: () => void;
}

const ImageEditorComponent = ({
  imageFile,
  imagePreview,
  onSave,
  onCancel,
}: ImageEditorProps) => {
  const editorRef = useRef<ImageEditor | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!containerRef.current) return;

    // Initialize tui-image-editor
    const editor = new ImageEditor(containerRef.current, {
      includeUI: {
        loadImage: {
          path: imagePreview,
          name: 'Image',
        },
        theme: {
          'common.bi.image': 'url()',
          'common.bisize.width': '0px',
          'common.bisize.height': '0px',

        },
        menu: ['crop'],
        initMenu: 'crop',
        uiSize: {
          width: '100%',
          height: '100%',
        },
      },
      cssMaxWidth: window.innerWidth,
      cssMaxHeight: window.innerHeight,
      selectionStyle: {
        cornerSize: 20,
        rotatingPointOffset: 70,
      },
    });

    editorRef.current = editor;
    setIsLoading(false);

    return () => {
      if (editorRef.current) {
        editorRef.current.destroy();
      }
    };
  }, [imagePreview]);

  const handleSave = () => {
    if (!editorRef.current) return;

    try {
      // Export the edited image
      const dataURL = editorRef.current.toDataURL();
      
      // Convert data URL to blob
      fetch(dataURL)
        .then((res) => res.blob())
        .then((blob) => {
          const editedFile = new File([blob], imageFile.name, {
            type: 'image/png',
          });

          onSave(editedFile);
        })
        .catch(() => {
          toast.error('Failed to save image');
        });
    } catch (error) {
      toast.error('Error saving image');
      console.error(error);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/75 flex flex-col">
      <div className="bg-gray-900 text-white p-4 shadow-lg flex items-center justify-between">
        <h2 className="text-2xl font-bold">Image Editor</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={handleSave}
            className="px-4 py-2 rounded-lg bg-yellow-400 text-black font-semibold hover:bg-yellow-500 transition-colors"
          >
            Save & Continue
          </button>
          <button
            onClick={onCancel}
            className="p-2 rounded-lg bg-red-600 hover:bg-red-700 transition-colors"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-hidden bg-gray-100">
        {isLoading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-600">Loading editor...</div>
          </div>
        )}
        <div ref={containerRef} className="h-full" />
      </div>
    </div>
  );
};

export default ImageEditorComponent;
