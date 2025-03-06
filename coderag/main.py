""" Main file for code analyzer """
from agent import chat

def main():
    # Initialize conversation history
    messages = []
    
    while True:
        user_input = input("\nEnter your query (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        
        response, messages = chat(user_input, messages)

if __name__ == "__main__":
    main()
