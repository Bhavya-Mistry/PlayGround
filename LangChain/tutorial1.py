#chat model

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API key not found. Please check your .env file.")

# Set it where LangChain expects it
os.environ["GOOGLE_API_KEY"] = api_key

# Initialize the Gemini model
model = init_chat_model("gemini-1.5-flash", model_provider="google_genai")

# Simple chat loop
print("Gemini Chat is ready. Type 'exit' to quit.")
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    response = model.invoke(user_input)
    print("Gemini:", response.content)