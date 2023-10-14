import logging
import asyncio 
import os
from langchain.agents import tool
from dotenv import load_dotenv

from langchain.agents.agent_toolkits import GmailToolkit

from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType

load_dotenv()
toolkit = GmailToolkit()

tools = toolkit.get_tools()

@tool("summarize")
def summarize(input: str) -> bool:
    """
    Summarize the response to the input prompt.
    """
    prompt = input

    llm = OpenAI(temperature=0)
    agent = initialize_agent(
        prompt=prompt,
        llm=llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    )

    return agent.run(prompt)
    
