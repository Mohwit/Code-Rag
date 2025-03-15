import { useState } from "react";

const useLLMChatService = () => {
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const sessionId = useState(() => crypto.randomUUID())[0];

    const fetchResponse = async (userMessage) => {
        setIsLoading(true);
        let accumulatedMessage = "";

   
        const userMessageObj = {
            id: messages.length + 1,
            text: userMessage,
            type: "user",
        };
        setMessages((prevMessages) => [...prevMessages, userMessageObj]);


        const tempAIMessageObj = {
            id: userMessageObj.id + 1,
            text: "",
            type: "ai",
            isLoading: true,
            canvas: [], 
        };
        setMessages((prevMessages) => [...prevMessages, tempAIMessageObj]);

        try {
            let eventSourceUrl = `${import.meta.env.VITE_API_URL}/chat?message=${encodeURIComponent(userMessage)}`;
            eventSourceUrl += `&sessionId=${sessionId}`;

            const eventSource = new EventSource(eventSourceUrl);

            eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
    
                setMessages((prevMessages) =>
                    prevMessages.map((msg) => {
                        if (msg.id === tempAIMessageObj.id) {
                            if (data.type === "message" && data.content?.text) {
                               
                                accumulatedMessage += data.content.text;
                                return { ...msg, text: accumulatedMessage, isLoading: false };
                            } else if (data.type === "canvas") {
                               
                                return { ...msg, canvas: [...msg.canvas, data.content] };
                            }
                        }
                        return msg;
                    })
                );

                if (data.done) {
                    eventSource.close();
                    setIsLoading(false);
                   
                }
            };

            eventSource.onerror = (error) => {
                console.error("Error streaming response:", error);
                eventSource.close();
                setIsLoading(false);
            };

            eventSource.addEventListener("end", () => {
                eventSource.close();
                setIsLoading(false);
            });
        } catch (error) {
            console.error("Error fetching response:", error);
            setMessages((prevMessages) => [
                ...prevMessages,
                {
                    id: userMessageObj.id ,
                    text: "Sorry, an error occurred while processing your request.",
                    type: "error",
                },
            ]);
            setIsLoading(false);
        } finally {
            setIsLoading(false);
        }
    };

    return { messages, isLoading, fetchResponse };
};

export default useLLMChatService;
