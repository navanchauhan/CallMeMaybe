import logging
import asyncio
import os
from langchain.agents import tool
from dotenv import load_dotenv

from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.transcriber import (
    DeepgramTranscriberConfig,
    PunctuationEndpointingConfig,
)


load_dotenv()

from call_transcript_utils import delete_transcript, get_transcript

from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)
from vocode.streaming.models.agent import ChatGPTAgentConfig
import time

LOOP = asyncio.new_event_loop()
asyncio.set_event_loop(LOOP)


@tool("call phone number")
def call_phone_number(input: str) -> str:
    """Use when you need to make a phone call. Calls a phone number as a bot and returns a transcript of the conversation.

    the input to this tool is a pipe separated list of a phone number, a prompt, and the first thing the bot should say.
    The prompt should instruct the bot with what to do on the call and be in the 3rd person,
    like 'the assistant is performing this task' instead of 'perform this task'.

    should only use this tool once it has found an adequate phone number to call.

    for example, `+15555555555|the assistant is explaining the meaning of life|i'm going to tell you the meaning of life` will call +15555555555, say 'i'm going to tell you the meaning of life', and instruct the assistant to tell the human what the meaning of life is.
    """
    phone_number, prompt, initial_message = input.split("|", 2)
    call = OutboundCall(
        base_url=os.environ["BASE_URL"],
        to_phone=phone_number,
        from_phone=os.environ["TWILIO_PHONE"],
        config_manager=RedisConfigManager(),
        agent_config=ChatGPTAgentConfig(
            initial_message=BaseMessage(text=initial_message),
            prompt_preamble=prompt,
            generate_responses=True,
        ),
        synthesizer_config=ElevenLabsSynthesizerConfig.from_telephone_output_device(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("ELEVENLABS_VOICE_ID"),
        ),
        transcriber_config=DeepgramTranscriberConfig.from_telephone_input_device(
            endpointing_config=PunctuationEndpointingConfig()
        ),
        logger=logging.Logger("OutboundCall"),
    )
    LOOP.run_until_complete(call.start())
    while True:
        maybe_transcript = get_transcript(call.conversation_id)
        if maybe_transcript:
            delete_transcript(call.conversation_id)
            return maybe_transcript
        else:
            time.sleep(1)
