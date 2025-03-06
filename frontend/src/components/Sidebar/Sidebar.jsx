import { useState, useEffect } from 'react';
import { FaFolderPlus, FaTimes, FaFolder, FaFolderOpen, FaFile, FaChevronDown, FaChevronRight } from 'react-icons/fa';
import { notification } from 'antd';
import styles from './Sidebar.module.css';
import useFolderUpload from '../../Hooks/useFolderUpload';

const Sidebar = ({ isSidebarOpen, setIsSidebarOpen, onFileSelect }) => {
  const [expandedFolders, setExpandedFolders] = useState({});
  
  // Use our custom hook
  const { 
    folderStructure, 
    uploadFolder, 
    fetchFile,
    isUploading, 
    progress, 
    error 
  } = useFolderUpload(); 

  // Show notification for errors
  useEffect(() => {
    if (error) {
      notification.error({
        message: 'Upload Error',
        description: error,
        placement: 'topRight',
        duration: 4
      });
    }
  }, [error]);

  // Toggle folder expansion
  const toggleFolder = (path) => {
    setExpandedFolders(prev => ({
      ...prev,
      [path]: !prev[path]
    }));
  };

  // Handle file click - fetch from backend
  const handleFileClick = async (filePath) => {
    try {
      // Show loading state (optional)
      onFileSelect && onFileSelect({ path: filePath, status: 'loading' });
      
      // Fetch file from backend
      const fileBlob = await fetchFile(filePath);
      
      // Call the parent component's handler with file info
      onFileSelect && onFileSelect({
        path: filePath,
        content: fileBlob,
        url: URL.createObjectURL(fileBlob),
        status: 'loaded'
      });
    } catch (error) {
      // Show error notification instead of console error
      notification.error({
        message: 'File Retrieval Failed',
        description: `Could not retrieve ${filePath}: ${error.message}`,
        placement: 'topRight',
        duration: 4
      });
      
      onFileSelect && onFileSelect({ 
        path: filePath, 
        status: 'error', 
        error: error.message 
      });
    }
  };

  // Initialize expanded state for top-level folders when structure changes
  useEffect(() => {
    if (folderStructure.length > 0) {
      const initialExpandedState = {};
      folderStructure.forEach(item => {
        if (item.type === 'folder') {
          initialExpandedState[item.path] = true; // Only top-level folders are expanded initially
        }
      });
      setExpandedFolders(initialExpandedState);
      
      // Show success notification on successful upload
      notification.success({
        message: 'Folder Uploaded',
        description: 'Folder structure has been successfully uploaded.',
        placement: 'topRight',
        duration: 3
      });
    }
  }, [folderStructure]);

  // Recursive component to render folder structure
  const FolderTree = ({ items, level = 0 }) => {
    return (
      <ul className={styles.folderList}>
        {items.map((item, index) => (
          <li key={index} className={styles.folderItem}>
            {item.type === 'folder' ? (
              <>
                <div 
                  className={styles.folderName}
                  onClick={() => toggleFolder(item.path)}
                >
                  <span className={styles.folderToggle}>
                    {item.children && item.children.length > 0 && (
                      expandedFolders[item.path] 
                      ? <FaChevronDown className={styles.chevronIcon} /> 
                      : <FaChevronRight className={styles.chevronIcon} />
                    )}
                  </span>
                  
                  {expandedFolders[item.path] 
                    ? <FaFolderOpen className={styles.folderIcon} /> 
                    : <FaFolder className={styles.folderIcon} />
                  }
                  <span className={styles.itemName}>{item.name}</span>
                </div>
                
                {/* Render children only if expanded */}
                {expandedFolders[item.path] && item.children && item.children.length > 0 && 
                  <FolderTree items={item.children} level={level + 1} />
                }
              </>
            ) : (
              <div 
                className={styles.fileName}
                onClick={() => handleFileClick(item.path)}
              >
                <span className={styles.fileIndent} />
                <FaFile className={styles.fileIcon} />
                <span className={styles.itemName}>{item.name}</span>
              </div>
            )}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className={`${styles.sidebar} ${isSidebarOpen ? styles.open : styles.closed}`}>
      <div className={styles.sidebarHeader}>
        <h3>Files</h3>
        <div className={styles.sidebarActions}>
          <label className={styles.uploadButton}>
            <FaFolderPlus className={styles.uploadIcon} />
            <input 
              type="file" 
              webkitdirectory="true" 
              directory="true"
              multiple 
              onChange={uploadFolder} 
              style={{ display: 'none' }}
            />
          </label>
          <FaTimes 
            className={styles.closeIcon} 
            onClick={() => setIsSidebarOpen(false)} 
          />
        </div>
      </div>
      <div className={styles.sidebarContent}>
        {isUploading && (
          <div className={styles.uploadProgress}>
            <progress value={progress} max="100" />
            <span>{progress}%</span>
          </div>
        )}
        
        {folderStructure.length > 0 ? (
          <FolderTree items={folderStructure} />
        ) : (
          <div className={styles.emptyState}>
            <p>No folders uploaded yet</p>
            <p>Click the folder icon to upload</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;