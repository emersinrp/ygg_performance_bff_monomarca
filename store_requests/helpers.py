import random
from datetime import datetime, timedelta
from faker import Faker
import hashlib
import time
import requests
from store_requests.config import Config
from store_requests.queries import get_delivery_window_query

fake = Faker()

def generate_order_number():
    unique_str = f"{time.time()}{random.randint(0, 9999)}"
    hash_str = hashlib.md5(unique_str.encode()).hexdigest()[:5].upper()
    return f"TEST{hash_str}"

def get_delivery_window(auth_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {auth_token}",
        "User-Agent": Config.USER_AGENT,
        "TENANT_ID": Config.TENANT_ID
    }
    
    try:
        query_data = get_delivery_window_query()
        
        response = requests.post(
            f"{Config.BASE_URL}/person/deliverywindow/search",
            headers=headers,
            json=query_data,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        items = data['data']['get_person_delivery_window']['items']
        
        if not items or not items[0]['delivery_windows']:
            raise ValueError("Nenhuma janela de entrega encontrada")
            
        valid_windows = [w for w in items[0]['delivery_windows'] if w['allowed_low_shelf_life']]
        
        if not valid_windows:
            raise ValueError("Nenhuma janela de entrega válida encontrada")
            
        full_date = valid_windows[0]['delivery_date']
        return full_date.split('T')[0]
        
    except Exception as e:
        print(f"Erro ao obter delivery window: {str(e)}")
        fallback_date = (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%d')
        return fallback_date

def get_payment_method(installments):
    return f"bp{installments}c"