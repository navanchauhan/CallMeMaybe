import os
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)

from speller_agent import SpellerAgentConfig

BASE_URL = os.environ["BASE_URL"]


async def main():
    config_manager = RedisConfigManager()

    outbound_call = OutboundCall(
        base_url=BASE_URL,
        to_phone="+17208828227",
        from_phone="+18445610144",
        config_manager=config_manager,
                    agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="What up"),
                prompt_preamble="Have a polite conversation about life while talking like a pirate.",
                generate_responses=True,
            ),
        synthesizer_config=ElevenLabsSynthesizerConfig.from_telephone_output_device(
            api_key=os.getenv("ELEVENLABS_API_KEY"),
            voice_id=os.getenv("YOUR VOICE ID")
        )
    )

    input("Press enter to start call...")
    await outbound_call.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())