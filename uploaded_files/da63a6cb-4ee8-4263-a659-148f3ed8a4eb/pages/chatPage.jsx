import InputBar from '../components/InputBar/InputBar'
import UserAndLLmChats from '../components/UserAndLLmChats/UserAndLLmChats';
import styles from './canvasPage.module.css'
import { useState, useEffect } from 'react';

const ChatPage = ({ isLoading, messages, fetchResponse , setOpenCanvas ,isOpenCanvas,setCanvas}) => {
   const [input, setInput] = useState('');
 
   const handleSend = async () => {
      if (input.trim()) {
        setInput('');
        await fetchResponse(input);
      }
   };

   return (
      <>
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
               <InputBar input={input} setInput={setInput} handleSend={handleSend} isLoading={isLoading} />
            </div>
            </div>
         </div>
      </>
   );
};

export default ChatPage;
