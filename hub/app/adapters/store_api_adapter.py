import json
import logging
from typing import List
import requests
from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_api_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        try:
            data = [json.loads(item.json()) for item in processed_agent_data_batch]
            response = requests.post(f"{self.api_base_url}/processed_agent_data/", json=data)
            if response.status_code != 200:
                logging.error(f"Failed to save data to the Store API: {response.text}")
                return False
            return True
        except Exception as e:
            logging.error(f"An error occurred while saving data to the Store API: {e}")
            return False
