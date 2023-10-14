import asyncio

import os
from typing import AsyncGenerator, AsyncIterable, Awaitable, Optional, Tuple

from vocode.streaming.models.agent import AgentConfig, AgentType
from vocode.streaming.agent.base_agent import BaseAgent, RespondAgent

import logging
import os
from fastapi import FastAPI
from vocode.streaming.models.telephony import TwilioConfig
from pyngrok import ngrok
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.telephony.server.base import (
    TwilioInboundCallConfig,
    TelephonyServer,
)

from vocode.streaming.telephony.server.base import TwilioCallConfig

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import BaseModel

from speller_agent import SpellerAgentFactory
import sys

# if running from python, this will load the local .env
# docker-compose will load the .env file by itself
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config_manager = RedisConfigManager()

BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    ngrok_auth = os.environ.get("NGROK_AUTH_TOKEN")
    if ngrok_auth is not None:
        ngrok.set_auth_token(ngrok_auth)
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 6789

    # Open a ngrok tunnel to the dev server
    BASE_URL = ngrok.connect(port).public_url.replace("https://", "")
    logger.info('ngrok tunnel "{}" -> "http://127.0.0.1:{}"'.format(BASE_URL, port))

if not BASE_URL:
    raise ValueError("BASE_URL must be set in environment if not using pyngrok")

from speller_agent import SpellerAgentConfig

print(AgentType)

telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/inbound_call",
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Ahoy Matey! Pizza Ahoy here! How may I help you."),
                prompt_preamble="You are receiving calls on behald of 'Pizza Ahoy!', a pizza establisment taking orders only for pickup. YOu will be provided the transcript from a speech to text model, say what you would say in that siutation. Talk like a pirate. Apologise to customer if they ask for delivery.",
                generate_responses=True,
                model_name="gpt-3.5-turbo"
            ),
            # agent_config=SpellerAgentConfig(generate_responses=False, initial_message=BaseMessage(text="What up.")),
            twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
                record=True
            ),
            synthesizer_config=ElevenLabsSynthesizerConfig.from_telephone_output_device(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("YOUR VOICE ID")
        )
        )
    ],
    agent_factory=SpellerAgentFactory(),
    logger=logger,
)

import os
import sys
import typing
from dotenv import load_dotenv

from tools.contacts import get_all_contacts
from tools.vocode import call_phone_number
from tools.summarize import summarize
from tools.get_user_inputs import get_desired_inputs
from tools.email_tool import email_tasks
from langchain.memory import ConversationBufferMemory
from langchain.agents import load_tools

from stdout_filterer import RedactPhoneNumbers

load_dotenv()

from langchain.chat_models import ChatOpenAI
# from langchain.chat_models import BedrockChat
from langchain.agents import initialize_agent
from langchain.agents import AgentType

from langchain.tools import WikipediaQueryRun

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
tools=load_tools(["human", "wikipedia"]) + [get_all_contacts, call_phone_number, email_tasks, summarize]

tools_desc = ""
for tool in tools:
    tools_desc += tool.name + " : "  + tool.description + "\n"

def rephrase_prompt(objective: str) -> str:
    # llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")  # type: ignore
    # pred = llm.predict(f"Based on these tools {tools_desc} with the {objective} should be done in the following manner (outputting a single sentence), allowing for failure: ")
    # print(pred)
    # return pred
    return f"{objective}"

with open("info.txt") as f:
    my_info = f.read()
    memory.chat_memory.add_user_message("User information to us " + my_info + " end of user information.")


class QueryItem(BaseModel):
    query: str

@app.post("/senpai")
def exec_and_return(item: QueryItem):
    query = item.query
    verbose_value = False
    print(query)
    OBJECTIVE = (
        query
        or "Find a random person in my contacts and tell them a joke"
    )
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")  # type: ignore
    #llm = BedrockChat(model_id="anthropic.claude-instant-v1", model_kwargs={"temperature":0})  # type: ignore
    #memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    # Logging of LLMChains
    verbose = True
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        verbose=verbose_value,
        memory=memory,
    )

    out = agent.run(OBJECTIVE)

    return out

app.include_router(telephony_server.get_router())