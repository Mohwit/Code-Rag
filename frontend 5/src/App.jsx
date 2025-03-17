import React,{useEffect, useState} from "react";
import {  Splitter } from "antd";
import CanvasPage from "./pages/canvasPage";
import ChatPage from "./pages/chatPage";
import useLLMChatService from './Hooks/useLLMChatService'
const App = () => {
  const { isLoading, messages,fetchResponse,handleDiffVerification } = useLLMChatService();
  const [isOpenCanvas, setOpenCanvas] = useState(false);
  
  const [canvas, setCanvas] = useState('');
  return (
  <>
  <div
    style={{
      width: "100%",
      height: "100vh",
      display: "flex",
      flexDirection: "column",
    }}
  >
    <Splitter
      style={{
        flex: 1,
        boxShadow: "0 0 100px rgba(0, 0, 0, 0.1)",
      }}
    >

     <Splitter.Panel
          defaultSize="40%"
          min="30%"
          max="70%"
          style={{
            color: 'black',
            boxShadow: '2px 0px 15px rgba(0, 0, 0, 0.1)', 
            zIndex: 2
          }}
        >
          <ChatPage
            isLoading={isLoading}
            messages={messages}
            fetchResponse={fetchResponse}
            setOpenCanvas={setOpenCanvas}
            isOpenCanvas={isOpenCanvas}
            setCanvas={setCanvas}
            canvas={canvas}
          />
        </Splitter.Panel>


      {isOpenCanvas && <Splitter.Panel style={{ backgroundColor: "white" }} >
        
        <CanvasPage 
          codeCanvas={canvas}
          setOpenCanvas={setOpenCanvas}
          handleDiffVerification={handleDiffVerification}
          messages={messages}
        />
      </Splitter.Panel>}
    </Splitter>
  </div>
  </>
  )
 }

export default App;
