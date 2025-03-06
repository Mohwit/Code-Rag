import { useState, useCallback } from 'react';

const useFolderUpload = () => {
  const uploadEndpoint = import.meta.env.VITE_API_URL;

  const [folderStructure, setFolderStructure] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  // Build folder structure from file list
  const buildFolderStructure = (fileList) => {
    const structure = [];
    const folderMap = {};

    Array.from(fileList).forEach(file => {
      const path = file.webkitRelativePath || file.name;
      const parts = path.split('/');

      let currentLevel = structure;
      let currentPath = '';

      // Process each part of the path
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        currentPath += (i > 0 ? '/' : '') + part;

        // If this is the file name (last part)
        if (i === parts.length - 1 && !path.endsWith('/')) {
          currentLevel.push({
            name: part,
            type: 'file',
            path: currentPath,
            size: file.size,
            lastModified: file.lastModified
          });
        }
        // If this is a directory
        else {
          // Check if we've already seen this folder
          if (!folderMap[currentPath]) {
            const newFolder = {
              name: part,
              type: 'folder',
              path: currentPath,
              children: []
            };
            folderMap[currentPath] = newFolder;
            currentLevel.push(newFolder);
          }

          // Move the pointer to the children of this folder
          currentLevel = folderMap[currentPath].children;
        }
      }
    });

    return structure;
  };

  // Upload folder to backend
  const uploadFolder = useCallback(async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setProgress(0);
    setError(null);

    // Store files for later structure building
    const selectedFiles = Array.from(files);

    try {
      // Create FormData for uploading all files
      const formData = new FormData();

      // Add all files to FormData
      selectedFiles.forEach(file => {
        // Use webkitRelativePath to preserve folder structure
        formData.append('files', file);
        formData.append('paths', file.webkitRelativePath || file.name);
      });

      // Upload files to the server
      let response = await fetch(uploadEndpoint + '/upload-folder', {
        method: 'POST',
        body: formData,
        // Use XHR for progress tracking
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          setProgress(percentCompleted);
        }
      });

      if (!response.ok) {
        throw new Error(`Upload failed with status: ${response.status}`);
      }

      // Response is successful, now build folder structure
      const structure = buildFolderStructure(selectedFiles);
      setFolderStructure(structure);

      const result = await response.json();
      setProgress(100);

      return {
        success: true,
        folderStructure: structure,
        serverResponse: result,
      };

    } catch (err) {
      setError(err.message);
      return { success: false, error: err.message };
    } finally {
      setIsUploading(false);
    }
  }, [uploadEndpoint]);

  // Fetch a specific file from the backend
  const fetchFile = useCallback(async (filePath) => {
    try {
      const response = await fetch(`${uploadEndpoint}/file?path=${encodeURIComponent(filePath)}`, {
        method: 'GET'
      });

      if (!response.ok) {
        throw new Error(`Failed to retrieve file with status: ${response.status}`);
      }

      return await response.blob();
    } catch (err) {
      // We don't set error state here, we'll handle it with notifications in the component
      throw err;
    }
  }, [uploadEndpoint]);

  // Reset error state
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    folderStructure,
    setFolderStructure,
    uploadFolder,
    fetchFile,
    isUploading,
    progress,
    error,
    clearError
  };
};

export default useFolderUpload;