import logging
from typing import Optional, Tuple
import typing
import requests
import urllib.parse
from vocode.streaming.agent.chat_gpt_agent import ChatGPTAgent
from vocode.streaming.models.agent import AgentConfig, AgentType, ChatGPTAgentConfig
from vocode.streaming.agent.base_agent import BaseAgent, RespondAgent
from vocode.streaming.agent.factory import AgentFactory


class SpellerAgentConfig(AgentConfig, type="agent_speller"):
    pass


class SpellerAgent(RespondAgent[SpellerAgentConfig]):
    def __init__(self, agent_config: SpellerAgentConfig):
        super().__init__(agent_config=agent_config)

    async def respond(
        self,
        human_input,
        conversation_id: str,
        is_interrupt: bool = False,
    ) -> Tuple[Optional[str], bool]:
        return "".join(c + " " for c in human_input), False


def send_event(tracking_id, event_category, event_action, event_label=None, event_value=None):
    # Construct the Measurement Protocol endpoint URL
        #self.logger.info("send_event is running")
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



class SpellerAgentFactory(AgentFactory):
    def create_agent(
        self, agent_config: AgentConfig, logger: Optional[logging.Logger] = None
    ) -> BaseAgent:
        if agent_config.type == AgentType.CHAT_GPT:
            #here here here!!!!!
            #self.logger.debug("hey!!! I can write to the consolm{}".format(id))
            send_event('G-599HPZ77RD', 'phone call', 'connected', 'label', 42)
            return ChatGPTAgent(
                agent_config=typing.cast(ChatGPTAgentConfig, agent_config)
            )
        elif agent_config.type == "agent_speller":
            return SpellerAgent(
                agent_config=typing.cast(SpellerAgentConfig, agent_config)
            )
        raise Exception("Invalid agent config")
