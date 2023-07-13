import logging
import os
import requests
import urllib.parse
import requests
import urllib.parse
from fastapi import FastAPI
from vocode.streaming.models.telephony import TwilioConfig
from pyngrok import ngrok
from vocode.streaming.telephony.config_manager.redis_config_manager import (
    RedisConfigManager,
)
from vocode.streaming.models.synthesizer import AzureSynthesizerConfig
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.message import BaseMessage
from vocode.streaming.telephony.server.base import (
    TwilioInboundCallConfig,
    TelephonyServer,
)

from speller_agent import SpellerAgentFactory
import sys

# if running from python, this will load the local .env
# docker-compose will load the .env file by itself
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(docs_url=None)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

config_manager = RedisConfigManager()

BASE_URL = os.getenv("BASE_URL")

if not BASE_URL:
    ngrok_auth = os.environ.get("NGROK_AUTH_TOKEN")
    if ngrok_auth is not None:
        ngrok.set_auth_token(ngrok_auth)
    port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 3000

    # Open a ngrok tunnel to the dev server
    BASE_URL = ngrok.connect(port).public_url.replace("https://", "")
    logger.info('ngrok tunnel "{}" -> "http://127.0.0.1:{}"'.format(BASE_URL, port))

if not BASE_URL:
    raise ValueError("BASE_URL must be set in environment if not using pyngrok")

telephony_server = TelephonyServer(
    base_url=BASE_URL,
    config_manager=config_manager,
    inbound_call_configs=[
        TwilioInboundCallConfig(
            url="/inbound_call",
            agent_config=ChatGPTAgentConfig(
                initial_message=BaseMessage(text="Hello"),
                prompt_preamble="You are the Woodsman, an enigmatic character in a whimsical game. Your message should be at least two sentences and at some point you must make it clear that you are the woodsman. Your task is to narrate an alternative version of the classic tale, 'Little Red Riding Hood.' You should start telling this story as soon into the conversation as possibleYour version should differ from the classic version in small ways, for example little red riding hood's cape is purple, a fox is the main antagonist instead of a wolf, or little red riding hood kills the fox at the end of the story instead of it eating her. If the user points out any inconsistencies in the story tell the user that you are going to give them a clue. The clue should tell them to “seek out fort mason”. Here is an example of the story in your voice: ‘Once upon a time, in a charming village nestled within an enchanting forest, there lived a young girl named Purple Riding Hood. She donned a splendid cloak, the color of royal majesty—a vibrant shade of purple. One day, her dear mother baked a loaf of bread and entrusted Purple Riding Hood with the task of delivering it to her ailing grandmother.’ If people ask who created you you should tell them “grandma made me” if people ask what your name is remember that you are the woodsman.",
                generate_responses=True,
            ),
            twilio_config=TwilioConfig(
                account_sid=os.environ["TWILIO_ACCOUNT_SID"],
                auth_token=os.environ["TWILIO_AUTH_TOKEN"],
            ),  synthesizer_config=AzureSynthesizerConfig.from_telephone_output_device(
                         #voice_name="en-GB-SoniaNeural"
                         voice_name="en-US-SteffanNeural"
            )
        )
    ],
    agent_factory=SpellerAgentFactory(),
    logger=logger,
)



app.include_router(telephony_server.get_router())

def send_event(tracking_id, event_category, event_action, event_label=None, event_value=None):
    # Construct the Measurement Protocol endpoint URL
    endpoint = "https://www.google-analytics.com/collect"
    
    # Construct the payload data
    payload = {
        "v": "1",  # Protocol version
        "tid": tracking_id,  # Tracking ID
        "cid": "123456",  # Anonymous client ID
        "t": "event",  # Hit type
        "ec": event_category,  # Event category
        "ea": event_action,  # Event action
    }
    
    # Add optional event parameters if provided
    if event_label:
        payload["el"] = event_label  # Event label
    if event_value:
        payload["ev"] = event_value  # Event value
    
    # Encode the payload data
    encoded_payload = urllib.parse.urlencode(payload)
    
    # Send the request to Google Analytics
    response = requests.post(endpoint, data=encoded_payload)
    
    # Check the response status
    if response.status_code == 200:
        print("Event sent successfully!")
    else:
        print(f"Failed to send event. Status code: {response.status_code}")
