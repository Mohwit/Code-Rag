import React, { useState, useEffect } from 'react';
import CodeBlockEditor from '../components/CodeBlock/CodeBlock';

import styles from './CanvasPage.module.css'
import CanvasNavbar from '../components/CanvasNavbar/CanvasNavbar';
import DiffViewerComponent from '../components/DiffViewer/DiffViewer';
const CanvasPage = ({ codeCanvas, setOpenCanvas, handleDiffVerification, messages }) => {
  const [canvasState, setCanvasState] = useState(codeCanvas?.canvas);
  const [splitView,setSplitView] = useState(false);
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const updatedMessage = messages.find(msg => msg.id === codeCanvas?.id);
    if (updatedMessage) {
      setCanvasState(updatedMessage.canvas[codeCanvas.index]);
    }
  }, [messages, codeCanvas]);

  const handleAccept = async () => {
    setCanvasState((prev) => ({
      ...prev,
      oldFile: null,
      newFile: null,
      chosenFile: prev?.newFile,
      verified: true,
      accepted: true,
    }));
    await handleDiffVerification(codeCanvas.id, codeCanvas.index, true);
  };

  const handleReject = async () => {
    setCanvasState((prev) => ({
      ...prev,
      oldFile: null,
      newFile: null,
      chosenFile: prev?.oldFile,
      verified: true,
      accepted: false,
    }));
    await handleDiffVerification(codeCanvas.id, codeCanvas.index, false);
  };

  return (
    <div className={styles.container}>
       <div className={styles.navbar}>
          <CanvasNavbar
            handleAccept={handleAccept}
            handleReject={handleReject}
            setOpenCanvas={setOpenCanvas}
            setSplitView={setSplitView}
            splitView={splitView}
            canvasState={canvasState}
            setTheme={setTheme}
            theme={theme}
          />
       </div>

      <div className={styles.codeBlock}>
        {canvasState?.oldFile && canvasState?.newFile ? (
          <DiffViewerComponent 
            canvasState={canvasState} 
            splitView={splitView} 
            theme={theme}
            />
            
        ) : (
          <CodeBlockEditor 
            language={codeCanvas?.language || 'python'} 
            value={canvasState?.chosenFile} 
            highlightLine={''} 
            editorColor={theme === "light" ? false:true}
          />
        )}
      </div>
    </div>
  );
};

export default CanvasPage;

