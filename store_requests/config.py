import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_URL = os.getenv('BASE_URL')
    BRASPAG_URL = os.getenv('BRASPAG_URL')
    
    CLIENT_ID = os.getenv('CLIENT_ID')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    SCOPE = os.getenv('SCOPE')

    TENANT_ID = os.getenv('TENANT_ID')
    USER_AGENT = os.getenv('USER_AGENT')

    CARD_HOLDER = os.getenv('CARD_HOLDER')
    CARD_NUMBER = os.getenv('CARD_NUMBER')
    CARD_EXPIRATION = os.getenv('CARD_EXPIRATION')
    CARD_CVV = os.getenv('CARD_CVV')
    
    @staticmethod
    def get_headers(content_type=None):
        headers = {
            "Accept": "application/json",
            "User-Agent": Config.USER_AGENT
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers