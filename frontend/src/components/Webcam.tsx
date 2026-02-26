import { useEffect, useRef, useState } from "react";
import { CameraIcon, XMarkIcon, ArrowPathIcon, CheckIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";

interface WebcamProps {
  onCapture: (file: File) => void;
  onClose?: () => void;
}

const Webcam = ({ onCapture, onClose }: WebcamProps) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [capturedFile, setCapturedFile] = useState<File | null>(null);
  const [availableCameras, setAvailableCameras] = useState<MediaDeviceInfo[]>([]);
  const [currentCameraId, setCurrentCameraId] = useState<string | null>(null);

  const enumerateCameras = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      setAvailableCameras(videoDevices);
      return videoDevices;
    } catch (err) {
      console.error("Failed to enumerate cameras:", err);
      return [];
    }
  };

  const startCamera = async (deviceId?: string) => {
    try {
      setError(null);

      const constraints: MediaStreamConstraints = {
        video: deviceId
          ? { deviceId: { exact: deviceId }, width: { ideal: 1280 }, height: { ideal: 720 } }
          : { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);

      // Store current device ID
      const videoTrack = stream.getVideoTracks()[0];
      const settings = videoTrack.getSettings();
      setCurrentCameraId(settings.deviceId || null);

      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setIsCameraActive(true);

      // Enumerate cameras after first access (permissions granted)
      await enumerateCameras();
    } catch (err) {
      console.error("Camera error:", err);
      const errorMessage =
        err instanceof Error
          ? err.name === "NotAllowedError"
            ? "Camera permission denied. Please allow camera access."
            : err.name === "NotFoundError"
              ? "No camera found on this device."
              : "Failed to access camera."
          : "Failed to access camera.";
      setError(errorMessage);
      toast.error(errorMessage);
    }
  };

  const stopCamera = () => {
    // Stop all tracks in the stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => {
        track.stop();
      });
      streamRef.current = null;
    }

    // Clear video element source and pause
    if (videoRef.current) {
      videoRef.current.srcObject = null;
      videoRef.current.pause();
      videoRef.current.load(); // Reset the video element
    }

    setIsCameraActive(false);
  };

  const capturePhoto = () => {
    if (!videoRef.current || !canvasRef.current) {
      toast.error("Camera not ready");
      return;
    }

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext("2d");

    if (!context) {
      toast.error("Failed to capture photo");
      return;
    }

    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert canvas to blob and then to file
    canvas.toBlob(
      (blob) => {
        if (!blob) {
          toast.error("Failed to capture photo");
          return;
        }

        const timestamp = new Date().getTime();
        const file = new File([blob], `webcam-capture-${timestamp}.png`, {
          type: "image/png",
        });

        // Stop camera and show preview
        stopCamera();
        const imageUrl = URL.createObjectURL(blob);
        setCapturedImage(imageUrl);
        setCapturedFile(file);
        toast.success("Photo captured!");
      },
      "image/png",
      0.95
    );
  };

  const handleRetake = () => {
    // Reset captured image state
    setCapturedImage(null);
    setCapturedFile(null);
    // Restart camera
    startCamera();
  };

  const switchCamera = async () => {
    if (availableCameras.length <= 1) {
      toast.error("No other cameras available");
      return;
    }

    // Find next camera
    const currentIndex = availableCameras.findIndex(
      cam => cam.deviceId === currentCameraId
    );
    const nextIndex = (currentIndex + 1) % availableCameras.length;
    const nextCamera = availableCameras[nextIndex];

    // Stop current camera
    stopCamera();

    // Start new camera
    await startCamera(nextCamera.deviceId);

    toast.success(`Switched to ${nextCamera.label || 'camera ' + (nextIndex + 1)}`);
  };

  const handleSubmit = () => {
    if (capturedFile) {
      stopCamera();

      onCapture(capturedFile);

      setCapturedImage(null);
      setCapturedFile(null);
    }
  };


  useEffect(() => {
    // Cleanup on unmount
    return () => {
      stopCamera();
    };
  }, []);

  useEffect(() => {
    // This effect manages the lifecycle of the captured image URL.
    // It will be revoked on unmount or when a new image is captured.
    if (!capturedImage) return;

    return () => {
      URL.revokeObjectURL(capturedImage);
    };
  }, [capturedImage]);

  const handleClose = () => {
    stopCamera();
    onClose?.();
  };

  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center">

      {capturedImage ? (
        <img
          src={capturedImage}
          alt="Captured"
          className="w-full h-[70vh] object-cover rounded-lg"
        />
      ) : (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full h-[70vh] object-cover rounded-lg"
        />
      )}

      {/* Hidden canvas for capturing */}
      <canvas ref={canvasRef} className="hidden" />


      {error && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-red-500 text-white px-6 py-4 rounded-lg shadow-lg text-center max-w-md z-20">
          <p className="font-semibold mb-2">Camera Error</p>
          <p className="text-sm">{error}</p>
          <button
            onClick={handleClose}
            className="mt-4 px-4 py-2 bg-white text-red-500 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Close
          </button>
        </div>
      )}

      {/* Camera Controls */}
      {isCameraActive && !error && !capturedImage && (
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex items-center gap-4">
          <button
            onClick={capturePhoto}
            className="w-16 h-16 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-all transform hover:scale-105 flex items-center justify-center"
            title="Capture Photo"
          >
            <div className="w-14 h-14 bg-yellow-400 rounded-full flex items-center justify-center">
              <CameraIcon className="h-8 w-8 text-black" />
            </div>
          </button>
        </div>
      )}

      {/* Preview Controls - Retake and Submit Buttons */}
      {capturedImage && (
        <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 flex items-center gap-4">
          {/* Retake Button */}
          <button
            onClick={handleRetake}
            className="flex items-center gap-2 bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors shadow-lg"
            title="Retake Photo"
          >
            <ArrowPathIcon className="h-5 w-5" />
            <span>Retake</span>
          </button>

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            className="flex items-center gap-2 bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-3 px-6 rounded-lg transition-colors shadow-lg"
            title="Submit Photo"
          >
            <CheckIcon className="h-5 w-5" />
            <span>Submit</span>
          </button>
        </div>
      )}

      {/* Switch Camera Button */}
      {isCameraActive && !error && !capturedImage && availableCameras.length > 1 && (
        <button
          onClick={switchCamera}
          className="absolute top-4 left-4 p-2 bg-white rounded-full text-black shadow-lg hover:bg-gray-100 transition-colors z-10"
          title="Switch Camera"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            className="h-6 w-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99"
            />
          </svg>
        </button>
      )}

      {/* Close Button */}
      {onClose && (
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 p-2 bg-white rounded-full text-black shadow-lg hover:bg-gray-100 transition-colors z-10"
          title="Close Camera"
        >
          <XMarkIcon className="h-6 w-6" />
        </button>
      )}

      {/* Start Camera Button */}
      {!isCameraActive && !error && !capturedImage && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <button
            onClick={() => startCamera()}
            className="flex items-center gap-2 bg-yellow-400 hover:bg-yellow-500 text-black font-semibold py-3 px-6 rounded-lg transition-colors shadow-lg"
          >
            <CameraIcon className="h-6 w-6" />
            <span>Start Camera</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default Webcam;