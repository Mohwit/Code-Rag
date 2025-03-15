import React, { useState, useEffect, useRef } from 'react';
import styles from './UserAndLLmChats.module.css';
import { GiArtificialHive } from "react-icons/gi";
import CodeBlockEditor from '../CodeBlock/CodeBlock';
import ResponseFormater from '../ResponseFormater/ResponseFormater';
import { FaRegEdit } from "react-icons/fa";
import { BsArrowsAngleExpand } from "react-icons/bs";
import { AiOutlineSlack } from "react-icons/ai";


const UserAndLLmChats = ({  messages,isLoading,setOpenCanvas, isOpenCanvas, setCanvas, setCollapsed }) => {
    const chatEndRef = useRef(null);
    const [showInitialMessage, setShowInitialMessage] = useState(true);
    useEffect(() => {
        const latestMessage = messages[messages.length - 1];
        
        if (latestMessage?.type === 'ai' && latestMessage?.canvas?.length) {
            let index = 0;
    
            const interval = setInterval(() => {
                if (index < latestMessage.canvas.length) {
                    setCanvas(latestMessage.canvas[index]);
                    setOpenCanvas(true);
                    index++;
                } else {
                    clearInterval(interval);
                }
            }, 1000); 
    
            return () => clearInterval(interval); 
        }
    }, [messages, setCanvas, setOpenCanvas]);
    

    useEffect(() => {
        if (messages.some(msg => msg.type === 'user')) {
            setShowInitialMessage(false);
        }
    }, [messages]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    const handleCanvasOpen = (messageCanvas) => {
        setCanvas(messageCanvas);
        setOpenCanvas(true);
    };

    return (
        <div className={styles.chatWrapper}>
            <div className={styles.chatBot}>
                {showInitialMessage && (
                    <div className={styles.initialMessageContainer}>
                        <div className={styles.initialMessage}>
                            Welcome! 👋 How can I assist you today?
                        </div>
                    </div>
                )}

                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`${styles.message} ${
                            message.type === 'user' ? styles.userMessage : styles.aiMessage
                        }`}
                    >
                        {message.type === 'ai' ? (
                            <div className={styles.aiMessageContainer}>
                                <span className={styles.aiLogoAndThinking}>
                                    <GiArtificialHive className={styles.aiLogo} />
                                    <span className={styles.thinking}>
                                    <AiOutlineSlack /><span> {message.isLoading ? 'Analyzing...':`Here's the answer!✨`}</span>
                                    </span>
                               </span>
                                <div className={styles.aiText}>
                                    <ResponseFormater
                                        message={message.text}
                                        role={message.role}
                                    />

                                    {message.canvas?.length > 0  &&
                                        message.canvas.map((canvas, index) => (
                                            <div key={index} className={styles.codeContainer}
                                                onClick={() => handleCanvasOpen(canvas)}
                                            >
                                                <span className={styles.menu}>
                                                    <FaRegEdit />
                                                    <BsArrowsAngleExpand />
                                                </span>
                                                {!isOpenCanvas && (<CodeBlockEditor
                                                    language={canvas.language || 'python'}
                                                    value={canvas.text}
                                                    highlightLine={''}
                                                    editorColor={false}
                                                />)}
                                            </div>
                                        ))
                                    }
                                    {message.isLoading && <span className={styles.fastCursor}></span>}
                                </div>
                            </div>
                        ) : (
                            <div className={styles.userMessageContainer}>
                                <div className={styles.userText}>
                                    <p>{message.text}</p>
                                </div>
                            </div>
                        )}
                    </div>
                ))}


                <span ref={chatEndRef} className={styles.chatEnd} />
            </div>
        </div>
    );
};

export default UserAndLLmChats;
