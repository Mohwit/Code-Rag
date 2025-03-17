import React, { useState, useEffect, useRef,useCallback } from 'react';
import styles from './UserAndLLmChats.module.css';
import { GiArtificialHive } from "react-icons/gi";
import CodeBlockEditor from '../CodeBlock/CodeBlock';
import ResponseFormater from '../ResponseFormater/ResponseFormater';
import { FaRegEdit } from "react-icons/fa";
import { BsArrowsAngleExpand } from "react-icons/bs";
import { AiOutlineSlack } from "react-icons/ai";


const UserAndLLmChats = ({  messages,isLoading,setOpenCanvas, isOpenCanvas, setCanvas }) => {
    const chatEndRef = useRef(null);
    const canvasLock = useRef(false);
    const [showInitialMessage, setShowInitialMessage] = useState(true);

    // useEffect(() => {
    //     if (messages.length > 0) {
    //         const latestMessage = messages[messages.length - 1];
    //         if (latestMessage?.type === 'ai' && latestMessage?.canvas?.length) {
    //             // Only open the last canvas automatically if there are canvases that need verification
    //             const needsVerificationCanvas = latestMessage.canvas.findIndex(
    //                 canvas => canvas.needsVerification && !canvas.verified
    //             );
                
    //             if (needsVerificationCanvas !== -1) {
    //                 setCanvas({ id: latestMessage.id, index: needsVerificationCanvas, canvas: latestMessage.canvas[needsVerificationCanvas] });
    //                 setOpenCanvas(true);
    //             }
    //         }
    //     }
    // }, [messages, setCanvas, setOpenCanvas]);
    
    

    useEffect(() => {
        if (messages.some(msg => msg.type === 'user')) {
            setShowInitialMessage(false);
        }
    }, [messages]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isLoading]);

    const handleCanvasOpen = useCallback((id, index, canvas) => {
        if (!canvasLock.current) {
            canvasLock.current = true;
            setCanvas({ id, index, canvas });
            setOpenCanvas(true);
    
            setTimeout(() => {
                canvasLock.current = false;
            }, 500);
        }
    }, [setCanvas, setOpenCanvas]);

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

                                    { message.canvas?.length > 0  &&
                                        message.canvas.map((canvas, index) => (
                                            <div key={index} className={styles.codeContainer}
                                                onClick={() => handleCanvasOpen(message.id,index,canvas)}
                                            >
                                                <span className={styles.menu}>
                                                    <span className={styles.menuIcon}>
                                                        <FaRegEdit />
                                                        <span>{canvas.filename}</span>
                                                    </span>
                                                    <BsArrowsAngleExpand />
                                                </span>
                                                {!isOpenCanvas &&  (<CodeBlockEditor
                                                    language={canvas.language || 'python'}
                                                    value={canvas?.chosenFile || canvas?.newFile || 'unknown'}
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
