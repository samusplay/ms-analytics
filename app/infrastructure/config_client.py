# infrastructure/config_client.py
import requests

class ConfigClient:

    def get_active_configuration(self):
        response = requests.get("http://ms-configuration/config/active")
        return response.json()["data"]