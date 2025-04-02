import random
from datetime import datetime, timedelta  # Adicionei timedelta aqui
from faker import Faker
import hashlib
import time

fake = Faker()

def generate_order_number():
    unique_str = f"{time.time()}{random.randint(0, 9999)}"
    hash_str = hashlib.md5(unique_str.encode()).hexdigest()[:4].upper()
    return f"EMECBFF{hash_str}"

def calculate_delivery_date():
    today = datetime.utcnow()
    delivery_date = today + timedelta(days=2) 
    
    if delivery_date.weekday() >= 5:  # 5 = sábado, 6 = domingo
        extra_days = 7 - delivery_date.weekday()
        delivery_date += timedelta(days=extra_days)
    
    return delivery_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"

def get_payment_method(installments):
    return f"bp{installments}c"