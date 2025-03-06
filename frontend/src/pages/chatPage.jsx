import InputBar from '../components/InputBar/InputBar'
import UserAndLLmChats from '../components/UserAndLLmChats/UserAndLLmChats';
import Sidebar from '../components/Sidebar/Sidebar';
import styles from './canvasPage.module.css'
import { useState } from 'react';
import { FaFolder } from 'react-icons/fa';

const ChatPage = ({ isLoading, messages, fetchResponse, setOpenCanvas, isOpenCanvas, setCanvas }) => {
   const [input, setInput] = useState('');
   const [isSidebarOpen, setIsSidebarOpen] = useState(true);
   // const [folders, setFolders] = useState([]);

   const handleSend = async () => {
      if (input.trim()) {
        setInput('');
        await fetchResponse(input);
      }
   };

   return (
      <>
         <div className={styles.mainContainer}>
            {/* Left Sidebar */}
               {isSidebarOpen && (
                  <Sidebar 
                     className={`${styles.sidebar} ${!isSidebarOpen ? styles.hidden : ''}`}
                     isSidebarOpen={isSidebarOpen} 
                     setIsSidebarOpen={setIsSidebarOpen} 
                     onFileSelect={''}
                  />
               )}

            {!isSidebarOpen && (
               <button 
                  className={styles.toggleSidebar}
                  onClick={() => setIsSidebarOpen(true)}
               >
                  <FaFolder />
               </button>
            )}

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
                      />
                  </div>
               </div>
            </div>
         </div>
      </>
   );
};

export default ChatPage;