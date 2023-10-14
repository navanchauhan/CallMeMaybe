import logging
import asyncio 
import os
from langchain.agents import tool
from dotenv import load_dotenv

from langchain.llms import OpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.prompts.prompt import PromptTemplate


load_dotenv()

@tool("summarize")
def summarize(input: str) -> bool:
    """
    Summarize the response to the input prompt.
    """
    data = input

    llm = OpenAI(temperature=0)

    template = "Human: Can you summarize this in a couple of sentences: {data}"
    prompt = PromptTemplate(input_variables=["data"], template=template)
    pred = llm.predict(prompt.format(data=data))
    return pred
    #preferred_forums[make] = [make_url]
    
