import { useState } from 'react';

const useLLMChatService = () => {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    
    const sessionId = useState(() => crypto.randomUUID())[0];

    const fetchResponse = async (userMessage) => {
        setIsLoading(true);

        const userMessageObj = { 
            id: messages.length + 1, 
            text: userMessage, 
            type: 'user' 
        };
        setMessages(prevMessages => [...prevMessages, userMessageObj]);

        try {
            const response = await fetch(`${import.meta.env.VITE_API_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: sessionId
                })
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        try {
                            const eventData = JSON.parse(line.slice(6));
                            handleServerMessage(eventData, userMessageObj.id);
                        } catch (e) {
                            console.error('Error parsing event data:', e);
                        }
                    }
                }
            }

        } catch (error) {
            console.error('Error fetching response:', error);
            setMessages(prevMessages => [
                ...prevMessages,
                {
                    id: userMessageObj.id + 1,
                    text: 'Sorry, an error occurred while processing your request.',
                    type: 'error'
                }
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleServerMessage = (data, userMessageId) => {
        switch (data.type) {
            case 'canvas':
                // When canvas data arrives, match it with the appropriate AI message
                setMessages(prevMessages => {
                    const updatedMessages = [...prevMessages];
                    const aiMessageIndex = updatedMessages.findIndex(
                        msg => msg.type === 'ai' && msg.id === userMessageId + 1
                    );
    
                    if (aiMessageIndex === -1) {
                        updatedMessages.push({
                            id: userMessageId + 1,
                            text: '',  // Empty text initially
                            type: 'ai',
                            codeCanvas: {  // Add canvas content
                                name: data.content.name,
                                text: data.content.text
                            }
                        });
                    } else {
                        // Update the existing AI message with canvas
                        updatedMessages[aiMessageIndex].codeCanvas = {
                            name: data.content.name,
                            text: data.content.text
                        };
                    }
    
                    return updatedMessages;
                });
                break;
    
            case 'message':
                setMessages(prevMessages => {
                    const updatedMessages = [...prevMessages];
                    const aiMessageIndex = updatedMessages.findIndex(
                        msg => msg.type === 'ai' && msg.id === userMessageId + 1
                    );
    
                    if (aiMessageIndex === -1) {
                        updatedMessages.push({
                            id: userMessageId + 1,
                            text: data.content.text,
                            type: 'ai',
                            codeCanvas: null  // No canvas initially
                        });
                    } else {
                        updatedMessages[aiMessageIndex].text = data.content.text;
                    }
    
                    return updatedMessages;
                });
                break;
    
            case 'error':
                setMessages(prevMessages => [
                    ...prevMessages,
                    {
                        id: userMessageId + 1,
                        text: data.message,
                        type: 'error'
                    }
                ]);
                break;
    
            default:
                console.log('Unknown message type:', data);
        }
    };
    

    return {
        isLoading,
        messages,
          
        fetchResponse
    };
};

export default useLLMChatService;
