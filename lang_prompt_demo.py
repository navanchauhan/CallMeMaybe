import os
import sys
import typing
from dotenv import load_dotenv

from tools.contacts import get_all_contacts
from tools.vocode import call_phone_number
from tools.get_user_inputs import get_desired_inputs
from tools.email_tool import email_tasks
from langchain.memory import ConversationBufferMemory
from langchain.agents import load_tools

from stdout_filterer import RedactPhoneNumbers

load_dotenv()

from langchain.chat_models import ChatOpenAI
from langchain.chat_models import BedrockChat
from langchain.agents import initialize_agent
from langchain.agents import AgentType

if __name__ == "__main__":
    # Redirect stdout to our custom class
    sys.stdout = typing.cast(typing.TextIO, RedactPhoneNumbers(sys.stdout))

    OBJECTIVE = (
        input("Objective: ")
        + "make sure you use the proper tool before calling final action to meet objective, feel free to say you need more information or cannot do something."
        or "Find a random person in my contacts and tell them a joke"
    )
    #llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")  # type: ignore
    llm = BedrockChat(model_id="anthropic.claude-instant-v1", model_kwargs={"temperature":0})  # type: ignore
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    # Logging of LLMChains
    verbose = True
    agent = initialize_agent(
        tools=[get_all_contacts, call_phone_number, email_tasks] + load_tools(["serpapi", "human"]),
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=verbose,
        memory=memory,
    )

    agent.run(OBJECTIVE)
