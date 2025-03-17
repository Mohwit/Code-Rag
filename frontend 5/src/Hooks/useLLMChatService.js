import { useState, useCallback, useEffect } from "react";

const useLLMChatService = () => {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const sessionId = useState(() => crypto.randomUUID())[0];


    // Handle user verification response for canvas diffs
    const handleDiffVerification = async (messageId, canvasIndex, isAccepted) => {

        setMessages((prevMessages) => {
            return prevMessages.map((msg) => {
                if (msg.id === messageId) {
                    const updatedCanvas = [...msg.canvas];
                    if (updatedCanvas[canvasIndex]) {
                        const chosenFile = isAccepted
                            ? updatedCanvas[canvasIndex].newFile
                            : updatedCanvas[canvasIndex].oldFile;

                        updatedCanvas[canvasIndex] = {
                            ...updatedCanvas[canvasIndex],
                            oldFile: null,
                            newFile: null,
                            chosenFile,
                            verified: true,
                            accepted: isAccepted
                        };
                    }
                    return { ...msg, canvas: updatedCanvas };
                }
                return msg;
            });
        });

        // Send to backend if accepted
        const latestMessage = messages.find(msg => msg.id === messageId);
        const file_path = latestMessage?.canvas[canvasIndex]?.file_path;
        await sendFileToBackend(file_path, messageId, canvasIndex, isAccepted);
    };

    // Send verified file to backend
    const sendFileToBackend = async (file_path, messageId, canvasIndex, isAccepted) => {
        console.log("sending......to.....backend...file_path:", file_path);
        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/update-file`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ file_path: file_path, status: isAccepted }),
            });

            if (!response.ok) {
                throw new Error(`Failed with status ${response.status}`);
            }

            const result = await response.json();
            console.log("File sent successfully to backend:", result);
            setMessages((prevMessages) =>
                prevMessages.map((msg) => {
                    if (msg.id === messageId) {
                        const updatedCanvas = [...msg.canvas];
                        if (updatedCanvas[canvasIndex]) {
                            updatedCanvas[canvasIndex] = {
                                ...updatedCanvas[canvasIndex],
                                synced: true,
                                syncResult: result,
                            };
                        }
                        return { ...msg, canvas: updatedCanvas };
                    }
                    return msg;
                })
            );
        } catch (error) {
            console.error("Error sending file to backend:", error);

            setMessages((prevMessages) =>
                prevMessages.map((msg) => {
                    if (msg.id === messageId) {
                        const updatedCanvas = [...msg.canvas];
                        if (updatedCanvas[canvasIndex]) {
                            updatedCanvas[canvasIndex] = {
                                ...updatedCanvas[canvasIndex],
                                syncError: true,
                                errorMessage: error.message || "Failed to sync file with backend",
                            };
                        }
                        return { ...msg, canvas: updatedCanvas };
                    }
                    return msg;
                })
            );
        }
    };



    //************************************ LLM CHAT HOOK***********************************************************/   

    // Fetch response from backend
    // Fetch response from backend
    const fetchResponse = async (userMessage, selectedFiles) => {
        setIsLoading(true);
        let accumulatedMessage = "";

        const userMessageObj = {
            id: messages.length + 1,
            text: userMessage,
            type: "user",
        };
        setMessages((prev) => [...prev, userMessageObj]);

        const tempAIMessageObj = {
            id: userMessageObj.id + 1,
            text: "",
            type: "ai",
            isLoading: true,
            canvas: [],
        };
        setMessages((prev) => [...prev, tempAIMessageObj]);

        let eventSource;
        let receivedData = false; // Track if any data has been received

        try {
            let eventSourceUrl = `${import.meta.env.VITE_API_URL}/chat?message=${encodeURIComponent(userMessage)}&sessionId=${sessionId}`;
            if (selectedFiles.length > 0) {
                eventSourceUrl += "&files=" + encodeURIComponent(JSON.stringify(selectedFiles));
            }
            eventSource = new EventSource(eventSourceUrl);

            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    receivedData = true;
                    console.log("data:-", data);

                    setMessages((prev) =>
                        prev.map((msg) => {
                            if (msg.id === tempAIMessageObj.id) {
                                // Create the new message object based on data type
                                let updatedMsg = { ...msg };

                                if (data.type === "message" && data.content?.text) {
                                    accumulatedMessage += data.content.text;
                                    updatedMsg = {
                                        ...updatedMsg,
                                        text: accumulatedMessage
                                    };
                                } else if (data.type === "canvas") {
                                    const canvasContent = {
                                        ...data.content,
                                        verified: false,
                                        oldFile: data.content?.oldFile || 'no content',
                                        newFile: data.content?.newFile || '',
                                        filename: data.content?.filename || null,
                                        file_path: data.content?.file_path || null,
                                        needsVerification: !!(data.content?.oldFile && data.content?.newFile),
                                    };
                                    updatedMsg = {
                                        ...updatedMsg,
                                        canvas: [...msg.canvas, canvasContent]
                                    };
                                }

                                // If the event is done, always set isLoading to false
                                if (data.done) {
                                    updatedMsg.isLoading = false;
                                }

                                return updatedMsg;
                            }
                            return msg;
                        })
                    );

                    if (data.done) {
                        eventSource.close();
                        setIsLoading(false);
                    }
                } catch (error) {
                    console.error("Error parsing response:", error);

                    // Update message to remove loading state
                    setMessages((prev) =>
                        prev.map((msg) =>
                            msg.id === tempAIMessageObj.id
                                ? { ...msg, isLoading: false }
                                : msg
                        )
                    );

                    setIsLoading(false);
                    eventSource.close();
                }
            };

            eventSource.onerror = (error) => {
                console.error("Streaming error:", error);

                if (!receivedData) {
                    // Only show error message if NO data has been received
                    setMessages((prev) =>
                        prev.map((msg) =>
                            msg.id === tempAIMessageObj.id
                                ? { ...msg, text: "Server error. Please try again.", isLoading: false }
                                : msg
                        )
                    );
                } else {
                    // If some data was received, just ensure isLoading is set to false
                    setMessages((prev) =>
                        prev.map((msg) =>
                            msg.id === tempAIMessageObj.id
                                ? { ...msg, isLoading: false }
                                : msg
                        )
                    );
                }

                setIsLoading(false);
                eventSource.close();
            };

            // Cleanup eventSource when component unmounts
            return () => {
                if (eventSource) eventSource.close();
                setIsLoading(false);
            };
        } catch (error) {
            console.error("Error fetching response:", error);
            setIsLoading(false);
            setMessages((prev) => [
                ...prev.slice(0, -1),
                { id: userMessageObj.id + 1, text: "Failed to process request", type: "error", isLoading: false },
            ]);
        }
    };

    return { messages, isLoading, fetchResponse, handleDiffVerification };
};

export default useLLMChatService;