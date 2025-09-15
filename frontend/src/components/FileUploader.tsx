import React, { useRef } from 'react';

interface Props {
  onFileChange: (file: File | null) => void;
}

function uploadFile(file: File, url: string) {
  return fetch(url, {
    method: 'PUT',
    body: file,
    headers: {
      'Content-Type': file.type,
    },
  });
}

const FileUploader = ({ onFileChange }: Props) => {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    onFileChange(file);
  };

  return (
    <div className="mb-4">
      <input
        ref={inputRef}
        type="file"
        onChange={handleChange}
        className="border p-2 w-full"
        accept=".pdf,.doc,.docx,.txt,.zip"
      />
    </div>
  );
};

FileUploader.uploadFile = uploadFile;

export default FileUploader;
