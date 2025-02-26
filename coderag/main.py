""" Main file for code analyzer """
from agent import chat

def main():
    while True:
        user_input = input("\nEnter your query (or 'exit' to quit): ")
        if user_input.lower() == "exit":
            break
        chat(user_input)


if __name__ == "__main__":
    main()
