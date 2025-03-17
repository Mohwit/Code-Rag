import { useState, useCallback, useEffect } from 'react';
import { notification } from 'antd';

const useFolderUpload = () => {
  const uploadEndpoint = import.meta.env.VITE_API_URL;

  const [folderStructure, setFolderStructure] = useState(() => {
    // Retrieve from local storage
    const storedData = localStorage.getItem('folderStructure');
    return storedData ? JSON.parse(storedData) : [];
  });
  
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  // Save folder structure to local storage whenever it changes
  useEffect(() => {
    localStorage.setItem('folderStructure', JSON.stringify(folderStructure));
  }, [folderStructure]);

  // Build folder structure from file list
  const buildFolderStructure = (fileList) => {
    const structure = [];
    const folderMap = {};
    
    Array.from(fileList).forEach(file => {
      const path = file.webkitRelativePath || file.name;
      const parts = path.split('/');
      
      let currentLevel = structure;
      let currentPath = '';
      
      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        currentPath += (i > 0 ? '/' : '') + part;
        
        if (i === parts.length - 1 && !path.endsWith('/')) {
          currentLevel.push({
            name: part,
            type: 'file',
            path: currentPath,
            size: file.size,
            lastModified: file.lastModified
          });
        } else {
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
    
    const selectedFiles = Array.from(files);
   
    try {
      const formData = new FormData();
      
      selectedFiles.forEach(file => {
        formData.append('files', file);
        formData.append('paths', file.webkitRelativePath || file.name);
      });
      
      let response = await fetch(uploadEndpoint+'/upload-folder', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed with status: ${response.status}`);
      }
      
      notification.success({
        message: 'Folder Uploaded',
        description: 'Folder structure has been successfully uploaded.',
        placement: 'topRight',
        duration: 3
      });
      
      const structure = buildFolderStructure(selectedFiles);
      setFolderStructure(structure); // This also saves to local storage

      const result = await response.json();
      console.log('Uploaded files:', result.files);
      setProgress(100);
      
      return { success: true, folderStructure: structure, serverResponse: result };
      
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
      const fileBlob = await response.blob();
      return await fileBlob.text();
    } catch (err) {
      throw err;
    }
  }, [uploadEndpoint]);

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
