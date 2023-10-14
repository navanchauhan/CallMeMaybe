import os
from dotenv import load_dotenv

load_dotenv()

from vocode.streaming.models.telephony import TwilioConfig

from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)

from speller_agent import SpellerAgentConfig, SpellerAgentFactory

from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent

from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage

from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig

BASE_URL = os.environ["BASE_URL"]

import logging
logging.basicConfig(level=logging.DEBUG)


async def main():
    config_manager = RedisConfigManager()

    outbound_call = OutboundCall(
        base_url=BASE_URL,
        to_phone="+12243882079",
        from_phone="+18445610144",
        config_manager=config_manager,
        agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Hello. Hello"),
                prompt_preamble="Act as a customer talking to 'Cosmos', a pizza establisment ordering a large pepperoni pizza for pickup. If asked for a name, your name is 'Hunter McRobie', and your credit card number is 4-7-4-3 2-4-0-1 5-7-9-2 0-5-39 CVV: 123 and expiratoin is 10/25. If asked for numbers, say them one by one",#"Have a polite conversation about life while talking like a pirate.",
                generate_responses=True,
            ),
        twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
                record=True
            ),
                    synthesizer_config=ElevenLabsSynthesizerConfig.from_telephone_output_device(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("ELEVENLABS_VOICE_ID")
        )
    )

    input("Press enter to start call...")
    await outbound_call.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())