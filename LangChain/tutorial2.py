from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits.load_tools import load_tools

from langchain.agents import initialize_agent, AgentType
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API KEY not found. Please check your .env file")

llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.8, google_api_key = api_key)

tools = load_tools(["wikipedia", "llm-math"], llm=llm)

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)


query = input("User : ")

# query = "what is the average age of a dolphon? multiply it my 2 and exaplain the result"
result = agent.run(query)

print("\n Final Answer: \n", result)