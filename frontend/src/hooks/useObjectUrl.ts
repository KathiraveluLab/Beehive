import { useEffect, useState } from 'react';

const useObjectUrl = (file: File | Blob | null): string | null => {
  const [objectUrl, setObjectUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!file) {
      setObjectUrl(null);
      return undefined;
    }

    const url = URL.createObjectURL(file);
    setObjectUrl(url);

    return () => URL.revokeObjectURL(url);
  }, [file]);

  return objectUrl;
};

export default useObjectUrl;
