import React, { useState, useEffect, useRef } from 'react';
import CodeBlock from '../components/CodeBlock/CodeBlock';
import styles from './CanvasPage.module.css';
import { MdOutlineClose } from "react-icons/md";

const CanvasPage = ({ codeCanvas, setOpenCanvas }) => {
  const [streamingText, setStreamingText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const streamInterval = useRef(null);
  
  const TYPING_SPEED = 10;
  const CHARS_PER_CHUNK = 3;

  useEffect(() => {
    if (codeCanvas?.text) {
      setIsStreaming(true);
      let currentIndex = 0;
      const fullText = codeCanvas.text;
      setStreamingText('');

      streamInterval.current = setInterval(() => {
        currentIndex = Math.min(currentIndex + CHARS_PER_CHUNK, fullText.length);
        const currentText = fullText.slice(0, currentIndex);
        setStreamingText(currentText);

        if (currentIndex >= fullText.length) {
          clearInterval(streamInterval.current);
          setIsStreaming(false);
        }
      }, TYPING_SPEED);
    }

    return () => {
      if (streamInterval.current) {
        clearInterval(streamInterval.current);
      }
    };
  }, [codeCanvas]);

  return (
    <div className={styles.container}>
      <div onClick={() => setOpenCanvas(false)}>
        <MdOutlineClose className={styles.crossIcon} />
      </div>

      <div className={styles.codeBlock}>
        <CodeBlock 
          language={codeCanvas?.language || 'python'} 
          value={streamingText}
          highlightLine={''}
          isStreaming={isStreaming}
        />
      </div>
    </div>
  );
};

export default CanvasPage;