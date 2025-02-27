import React, { useState, useEffect, useRef } from 'react';
import styles from './UserAndLLmChats.module.css';
import { GiArtificialHive } from "react-icons/gi";
import CodeBlock from '../CodeBlock/CodeBlock';
import ResponseFormater from '../ResponseFormater/ResponseFormater';

const UserAndLLmChats = ({ messages, isLoading, onRecentQuestionClick, setOpenCanvas, isOpenCanvas, setCanvas}) => {
    const chatEndRef = useRef(null);
    const [streamingMessages, setStreamingMessages] = useState([]);
    const [showInitialMessage, setShowInitialMessage] = useState(true);
    const processingRef = useRef(new Set());
    const intervalRefs = useRef({});

    const recentQuestions = [
        "What is Docker?",
        "How does Kubernetes work?",
        "Explain React useState hook.",
        "How to set up Next.js with TypeScript?",
        "Best practices for microservices in AWS?"
    ];

    const TYPING_SPEED = 10;
    const CHARS_PER_CHUNK = 3;

    useEffect(() => {
        const latestMessage = messages[messages.length - 1];
        if (latestMessage?.type === 'ai' && latestMessage?.codeCanvas) {
            setCanvas(latestMessage.codeCanvas);
             setOpenCanvas(true); 
        }
    }, [messages, setCanvas, setOpenCanvas]);

    useEffect(() => {
        const newAiMessages = messages.filter(msg =>
            msg.type === 'ai' &&
            !processingRef.current.has(msg.id)
        );

        newAiMessages.forEach(msg => {
            processingRef.current.add(msg.id);
            let currentIndex = 0;
            const fullText = msg.text;

            intervalRefs.current[msg.id] = setInterval(() => {
                currentIndex = Math.min(currentIndex + CHARS_PER_CHUNK, fullText.length);
                const currentText = fullText.slice(0, currentIndex);

                setStreamingMessages(prev => {
                    const existingIndex = prev.findIndex(m => m.id === msg.id);
                    if (existingIndex > -1) {
                        const newMessages = [...prev];
                        newMessages[existingIndex] = { ...msg, text: currentText };
                        return newMessages;
                    }
                    return [...prev, { ...msg, text: currentText }];
                });

                if (currentIndex >= fullText.length) {
                    clearInterval(intervalRefs.current[msg.id]);
                    delete intervalRefs.current[msg.id];
                }
            }, TYPING_SPEED);
        });

        const userMessages = messages.filter(msg => msg.type === 'user');
        if (userMessages.length > 0 && showInitialMessage) {
            setShowInitialMessage(false);
        }

        return () => {
            Object.values(intervalRefs.current).forEach(clearInterval);
        };
    }, [messages, showInitialMessage]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [streamingMessages, isLoading]);

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
                        <div className={styles.recentQuestionsBox}>
                            <p className={styles.recentQuestionsTitle}>Recently Asked Questions:</p>
                            <div className={styles.recentQuestions}>
                                {recentQuestions.map((question, index) => (
                                    <button
                                        key={index}
                                        className={styles.questionButton}
                                        onClick={() => onRecentQuestionClick(question)}
                                    >
                                        {question}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {messages.map((message) => {
                    const isStreamingMessage = streamingMessages.find(m => m.id === message.id);
                    const displayMessage = isStreamingMessage || message;
                    const isStreaming = isStreamingMessage?.text?.length !== displayMessage.text.length;

                    return (
                        <div
                            key={displayMessage.id}
                            className={`${styles.message} ${
                                displayMessage.type === 'user' ? styles.userMessage : styles.aiMessage
                            }`}
                        >
                            {displayMessage.type === 'ai' ? (
                                <div className={styles.aiMessageContainer}>
                                    <GiArtificialHive className={styles.aiLogo} />
                                    <div className={styles.aiText}>
                                        <ResponseFormater
                                            message={displayMessage.text}
                                            role={displayMessage.text}
                                        />
                                        {displayMessage.codeCanvas && !isOpenCanvas && (
                                            <div className={styles.codeContainer}>
                                                <CodeBlock
                                                    language={displayMessage.codeCanvas.language || 'python'}
                                                    value={displayMessage.codeCanvas.text}
                                                    highlightLine={''}
                                                    editorColor={true}
                                                />
                                                <button
                                                    className={styles.openCanvasButton}
                                                    onClick={() => handleCanvasOpen(displayMessage.codeCanvas)}
                                                >
                                                    Open Canvas
                                                </button>
                                            </div>
                                        )}
                                        {isStreaming && <span className={styles.fastCursor}></span>}
                                    </div>
                                </div>
                            ) : (
                                <div className={styles.userMessageContainer}>
                                    <div className={styles.userText}>
                                        <p>{displayMessage.text}</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    );
                })}

                {isLoading && (
                    <div className={`${styles.message} ${styles.aiMessage}`}>
                        <div className={styles.aiMessageContainer}>
                            <GiArtificialHive className={styles.aiLogo} />
                            <div className={styles.aiText}>
                                <div className={styles.dotFlashing}>
                                    <div className={styles.fastDot}></div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                <span ref={chatEndRef} className={styles.chatEnd} />
            </div>
        </div>
    );
};

export default UserAndLLmChats;