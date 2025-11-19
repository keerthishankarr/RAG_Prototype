import React, { useState } from 'react';
import { X, Upload as UploadIcon } from 'lucide-react';
import { uploadDataset } from '../services/api';

interface DatasetManagerProps {
  onClose: () => void;
  onSuccess: () => void;
}

const DatasetManager: React.FC<DatasetManagerProps> = ({ onClose, onSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');
  const [chunkSize, setChunkSize] = useState(500);
  const [chunkOverlap, setChunkOverlap] = useState(50);
  const [strategy, setStrategy] = useState<'sentences' | 'characters'>('sentences');
  const [uploading, setUploading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !name) return;

    setUploading(true);
    try {
      await uploadDataset(file, name, chunkSize, chunkOverlap, strategy);
      alert('Dataset uploaded successfully!');
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error uploading dataset:', error);
      alert('Error uploading dataset: ' + (error as Error).message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-textPrimary">Upload Dataset</h2>
          <button onClick={onClose} className="text-textSecondary hover:text-textPrimary">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-textPrimary mb-1">
              Dataset Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-textPrimary mb-1">
              File (.txt, .pdf, .docx, .md)
            </label>
            <input
              type="file"
              accept=".txt,.pdf,.docx,.md"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full px-3 py-2 border border-border rounded-lg"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-textPrimary mb-1">
              Chunk Size: {chunkSize}
            </label>
            <input
              type="range"
              min="100"
              max="2000"
              step="50"
              value={chunkSize}
              onChange={(e) => setChunkSize(parseInt(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-textPrimary mb-1">
              Chunk Overlap: {chunkOverlap}
            </label>
            <input
              type="range"
              min="0"
              max="500"
              step="10"
              value={chunkOverlap}
              onChange={(e) => setChunkOverlap(parseInt(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-textPrimary mb-1">
              Chunking Strategy
            </label>
            <select
              value={strategy}
              onChange={(e) => setStrategy(e.target.value as 'sentences' | 'characters')}
              className="w-full px-3 py-2 border border-border rounded-lg"
            >
              <option value="sentences">Sentences</option>
              <option value="characters">Characters</option>
            </select>
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-border rounded-lg hover:bg-gray-50"
              disabled={uploading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-primary text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 flex items-center justify-center gap-2"
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : (
                <>
                  <UploadIcon size={16} />
                  Upload
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DatasetManager;
