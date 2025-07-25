from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")


def generate_pet_name():
    llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-pro", temperature=0.8, google_api_key=api_key)
    prompt = "I have a dog pet and I want a cool name for it. Suggest me five cool names for my pet."
    name = llm.invoke(prompt)
    return name


if __name__ == "__main__":
    print(generate_pet_name().content)
