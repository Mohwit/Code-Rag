
import InputBar from '../components/InputBar/InputBar'
import UserAndLLmChats from '../components/UserAndLLmChats/UserAndLLmChats';
import Sidebar from '../components/Sidebar/Sidebar';
import styles from './chatPage.module.css'
import { useState, useEffect } from 'react';
import { FaFolder } from 'react-icons/fa';
import useFolderUpload from '../Hooks/useFolderUpload';

const ChatPage = ({isLoading, messages, fetchResponse, setOpenCanvas, isOpenCanvas, setCanvas }) => {
   const [input, setInput] = useState('');
   const [isSidebarOpen, setIsSidebarOpen] = useState(!isOpenCanvas);
   useEffect(() => {
      setIsSidebarOpen(!isOpenCanvas);
   },[isOpenCanvas,setOpenCanvas])
   const [selectedFiles, setSelectedFiles] = useState([]);
   
   const { 
      folderStructure, 
      uploadFolder, 
      fetchFile,
      isUploading, 
      progress, 
      error,
      clearError 
   } = useFolderUpload();

   const handleSend = async () => {
      if (input.trim()) {
       
        await fetchResponse(input,selectedFiles);
        setInput('');
        setSelectedFiles([]);
      }
   };

   // Handle file selection
   const handleFileSelect = (file) => {
      if (!selectedFiles.some(f => f.path === file.path)) {
         setSelectedFiles([...selectedFiles, file]);
      }
   };

   return (
      <>
         <div className={styles.mainContainer}>
            {/* Left Sidebar */}
            <div className={styles.sidebarContainer}>
            {isSidebarOpen && (
               <Sidebar 
                  className={`${styles.sidebar} ${!isSidebarOpen ? styles.hidden : ''}`}
                  isSidebarOpen={isSidebarOpen} 
                  setIsSidebarOpen={setIsSidebarOpen}
                  folderStructure={folderStructure}
                  uploadFolder={uploadFolder}
                  fetchFile={fetchFile}
                  isUploading={isUploading}
                  progress={progress}
                  error={error}
                  clearError={clearError}
                  onFileSelect={handleFileSelect}
               />
            )}
 
            {!isSidebarOpen  && (
               <button 
                  className={styles.toggleSidebar}
                  onClick={() => 
                     setIsSidebarOpen(true)}
               >
                  <FaFolder />
               </button>
            )}
          </div>
            {/* Main Chat Area */}
            <div className={styles.dashboardContainer}>
               <div className={styles.llmChat}>
                  <UserAndLLmChats 
                     messages={messages} 
                     isLoading={isLoading}
                     setOpenCanvas={setOpenCanvas}
                     isOpenCanvas={isOpenCanvas}
                     setCanvas={setCanvas}
                  />
               </div>
               <div className={styles.inputBar}>
                  <div className={styles.inputBarContainer}> 
                     <InputBar 
                        input={input}
                        setInput={setInput}
                        handleSend={handleSend} 
                        isLoading={isLoading}
                        folderStructure={folderStructure}
                        selectedFiles={selectedFiles}
                        setSelectedFiles={setSelectedFiles}
                     />
                  </div>
               </div>
            </div>
         </div>
      </>
   );
};

export default ChatPage;