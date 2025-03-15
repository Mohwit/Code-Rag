import { useState, useEffect } from 'react';
import {
  FaFolderPlus, FaTimes, FaFolder, FaFolderOpen, FaFile,
  FaChevronDown, FaChevronRight, FaPlus, FaDownload, FaEllipsisV
} from 'react-icons/fa';
import { notification, Spin, Empty, Button, Modal } from 'antd';
import { GrView } from "react-icons/gr";

import styles from './Sidebar.module.css';

const Sidebar = ({
  isSidebarOpen,
  setIsSidebarOpen,
  folderStructure,
  uploadFolder,
  fetchFile,
  isUploading,
  progress,
  error,
  clearError,
  onFileSelect
}) => {
  const [expandedFolders, setExpandedFolders] = useState({});
  const [activeFile, setActiveFile] = useState(null);
  const [fileContent, setFileContent] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loadingFiles, setLoadingFiles] = useState({});


  useEffect(() => {
    if (error) {
      notification.error({
        message: 'Upload Error',
        description: error,
        placement: 'topRight',
        duration: 4
      });
      clearError && clearError();
    }
  }, [error, clearError]);


  const toggleFolder = (path) => {
    setExpandedFolders(prev => ({
      ...prev,
      [path]: !prev[path]
    }));
  };


  const handleAddToInput = (item, e) => {
    e.stopPropagation();
    setActiveFile(null);

    if (onFileSelect) {
      onFileSelect({
        path: item.path,
        name: item.name,
        type: 'file'
      });

      notification.success({
        message: 'File Added',
        description: `${item.name} has been added to your message`,
        placement: 'bottomRight',
        duration: 2
      });
    }
  };

  // Handle retrieve file from backend
  const handleRetrieveFile = async (item, e) => {
    e.stopPropagation();
    setActiveFile(null);

    // Set loading state for this file
    setLoadingFiles(prev => ({ ...prev, [item.path]: true }));

    try {

      const textFile = await fetchFile(item.path);
      setFileContent({ textFile: textFile, path: item.path });
      setIsModalOpen(true);

    } catch (error) {
      notification.error({
        message: 'Retrieval Failed',
        description: `Could not retrieve ${item.name}: ${error.message}`,
        placement: 'bottomRight',
        duration: 4
      });
    } finally {
      // Clear loading state
      setLoadingFiles(prev => ({ ...prev, [item.path]: false }));
    }
  };

  // Initialize expanded state for top-level folders when structure changes
  useEffect(() => {
    if (folderStructure && folderStructure.length > 0) {
      const initialExpandedState = {};
      folderStructure.forEach(item => {
        if (item.type === 'folder') {
          initialExpandedState[item.path] = true; // Only top-level folders are expanded initially
        }
      });
      setExpandedFolders(initialExpandedState);

      // Show success notification on successful upload
      // notification.success({
      //   message: 'Folder Uploaded',
      //   description: 'Folder structure has been successfully uploaded.',
      //   placement: 'topRight',
      //   duration: 3
      // });
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
              <div className={styles.fileContainer}>
                <div
                  className={styles.fileName}
                  onClick={() => setActiveFile(activeFile === item.path ? null : item.path)}
                >
                  <span className={styles.fileIndent} />
                  <FaFile className={styles.fileIcon} />
                  <span className={styles.itemName}>{item.name}</span>

                  {/* Options button or loading spinner */}
                  {loadingFiles[item.path] ? (
                    <Spin size="small" className={styles.fileSpinner} />
                  ) : (
                    <div
                      className={`${styles.fileOptions} ${activeFile === item.path ? styles.active : ''}`}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <FaEllipsisV className={styles.optionsIcon} />
                    </div>
                  )}
                </div>

                {/* File options dropdown */}
                {activeFile === item.path && !loadingFiles[item.path] && (
                  <div className={styles.fileActionsDropdown}>
                    <div
                      className={styles.fileAction}
                      onClick={(e) => handleAddToInput(item, e)}
                    >
                      <FaPlus className={styles.actionIcon} />
                      <span>Add to input</span>
                    </div>
                    <div
                      className={styles.fileAction}
                      onClick={(e) => handleRetrieveFile(item, e)}
                    >
                      <GrView className={styles.actionIcon} />
                      <span>View file</span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </li>
        ))}
      </ul>
    );
  };

  // Click outside to close active file options
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (activeFile && !event.target.closest(`.${styles.fileContainer}`)) {
        setActiveFile(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [activeFile]);

  return (
    <div className={`${styles.sidebar} ${isSidebarOpen ? styles.open : styles.closed}`}>
      <div className={styles.sidebarHeader}>
        <h3>Files</h3>
        <div className={styles.sidebarActions}>
          <label className={styles.uploadButton} title="Upload Folder">
            <FaFolderPlus className={styles.uploadIcon} />
            <input
              type="file"
              webkitdirectory="true"
              directory="true"
              multiple
              onChange={uploadFolder}
              style={{ display: 'none' }}
              id="folderUpload"
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

        {folderStructure && folderStructure.length > 0 ? (
          <FolderTree items={folderStructure} />
        ) : (
          <div className={styles.emptyState}>
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={
                <div className={styles.emptyDescription}>
                  <p>No folders uploaded yet</p>
                  {/* <Button
                    type="primary"
                    icon={<FolderAddOutlined />}
                    className={styles.uploadFolderButton}
                    onClick={() => document.getElementById('folderUpload').click()}
                  >
                    Upload Folder
                  </Button> */}
                </div>
              }
            />
          </div>
        )}
      </div>
      {/* Ant Design Modal */}
      <Modal
        title={fileContent.path}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        width={700}

      >
        <pre style={{ whiteSpace: "pre-wrap", wordWrap: "break-word", maxHeight: "600px", overflowY: "auto" }}>
          {fileContent.textFile}

        </pre>
      </Modal>
    </div>
  );
};

export default Sidebar;