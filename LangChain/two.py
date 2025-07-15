from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.agents import initialize_agent, AgentType




load_dotenv()
api_key = os.getenv("API_KEY")


def generate_pet_name(animal_type, pet_color):

    prompt_template_name = PromptTemplate(
        input_variables=['animal_type','pet_color'],
        template="I have a {animal_type} pet and I want a cool name for it, it is {pet_color} in color. Suggest me five cool names for my pet."
    )
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.8, google_api_key=api_key)
    name_chain = prompt_template_name | llm
    response = name_chain.invoke({'animal_type':animal_type, 'pet_color':pet_color})
    return response.content



def langchain_agent():
    llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0.8, google_api_key=api_key)
    tools = load_tools(["wikipedia","llm-math"], llm=llm)

    agent = initialize_agent(
        tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True
    )


    result = agent.run(
        "What is the average age of dog? Multiply the result by 2"
    )

    print(result)

if __name__ == "__main__":
    # print(generate_pet_name("cat", "Black"))
    langchain_agent()
