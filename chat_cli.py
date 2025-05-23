from openai import OpenAI
import os
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def save_history(history, filename=None):
    """Save chat history to a JSON file."""
    if filename is None:
        filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"\nChat history saved to {filename}")

def load_history(filename):
    """Load chat history from a JSON file."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Error: {filename} is not a valid JSON file")
        return []

def chat_loop():
    """Main chat loop function."""
    print("Welcome to the OpenRouter Chat CLI!")
    print("Type 'exit' or 'quit' to end the chat")
    print("Type 'save' to save the chat history")
    print("Type 'load <filename>' to load a previous chat")
    print("-" * 50)

    history = []
    
    while True:
        try:
            # Get user input
            prompt = input("\nYou: ").strip()
            
            # Handle special commands
            if prompt.lower() in ['exit', 'quit']:
                save = input("Would you like to save the chat history? (y/n): ").lower()
                if save == 'y':
                    save_history(history)
                print("Goodbye!")
                break
                
            elif prompt.lower() == 'save':
                save_history(history)
                continue
                
            elif prompt.lower().startswith('load '):
                filename = prompt[5:].strip()
                history = load_history(filename)
                print(f"Loaded chat history from {filename}")
                continue
            
            # Add user message to history
            history.append({"role": "user", "content": prompt})
            
            # Get response from the model
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                messages=history,
                extra_headers={
                    "HTTP-Referer": os.getenv("APP_URL"),
                    "X-Title": os.getenv("APP_TITLE"),
                }
            )
            
            # Extract and print the response
            reply = response.choices[0].message.content
            print("\nBot:", reply)
            
            # Add assistant's response to history
            history.append({"role": "assistant", "content": reply})
            
        except KeyboardInterrupt:
            print("\nChat interrupted. Would you like to save the history? (y/n): ", end='')
            if input().lower() == 'y':
                save_history(history)
            break
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again or type 'exit' to quit")

if __name__ == "__main__":
    chat_loop() 