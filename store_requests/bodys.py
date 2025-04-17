from store_requests.config import Config
from store_requests.helpers import get_delivery_window, get_payment_method
import random

def get_token_body():
    return {
        "client_id": Config.CLIENT_ID,
        "grant_type": "client_credentials",
        "client_secret": Config.CLIENT_SECRET,
        "scope": Config.SCOPE
    }

def get_card_token_body(access_token):
    return {
        "HolderName": Config.CARD_HOLDER,
        "RawNumber": Config.CARD_NUMBER,
        "Expiration": Config.CARD_EXPIRATION,
        "SecurityCode": Config.CARD_CVV,
        "AccessToken": access_token,
        "EnableTokenize": "true",
        "EnableVerifyCard":"true",
        "EnableBinQuery": "true"
    }

def get_delivery_window_query():
    return {
        "query": """
        query ValidacaoDeliveryWindow($buyer_codes: [String!]!, $allowed_low_shelf_life: Boolean) {
          get_person_delivery_window(
            filters: {buyer_codes: $buyer_codes, allowed_low_shelf_life: $allowed_low_shelf_life, only_valids_delivery_windows: true}
          ) {
            items {
              delivery_windows {
                allowed_low_shelf_life
                delivery_date
              }
            }
          }
        }
        """,
        "variables": {
            "buyer_codes": ["0000247276"],
            "allowed_low_shelf_life": True
        }
    }

def get_order_body(card_token, order_number, installments=1, auth_token=None):
    if not all([card_token, order_number, 1 <= installments <= 3]):
        raise ValueError("Parâmetros inválidos para criação do pedido")
    
    if not auth_token:
        raise ValueError("Token de autenticação é necessário para obter a janela de entrega")
    
    delivery_date = get_delivery_window(auth_token)

    items = [
        {
            "unit_of_measurement": "CX",
            "total": 61.09,  # Valor base para 1 unidade
            "sku": "000000000000459183",
            "quantity": random.randint(1, 5),
            "price": {
                "value": 15.69,
                "unit": "KG",
                "promotion": "0",
                "currency": "BRL"
            },
            "fifo_category": "GREEN",
            "description": "Lasanha Bolonhesa Perdigão 600g -Caixa c/6",
            "additional_info": None
        },
        {
            "unit_of_measurement": "CX",
            "total": 134.55,  # Valor base para 1 unidade
            "sku": "000000000000460677",
            "quantity": random.randint(1, 5),
            "price": {
                "value": 25.66,
                "unit": "KG",
                "promotion": "0",
                "currency": "BRL"
            },
            "fifo_category": "GREEN",
            "description": "Nuggets Tradicional Sadia 300g -Caixa c/16",
            "additional_info": None
        },
        {
            "unit_of_measurement": "CX",
            "total": 287.70,  # Valor base para 1 unidade
            "sku": "000000000000515649",
            "quantity": random.randint(1, 5),
            "price": {
                "value": 19.18,
                "unit": "KG",
                "promotion": "0",
                "currency": "BRL"
            },
            "fifo_category": "GREEN",
            "description": "Tulipa de Frango Perdigão Food Service Caixa 15Kg -Caixa c/1",
            "additional_info": None
        }
    ]
    total_amount = 0
    for item in items:
        item["total"] = round(item["total"] * item["quantity"], 2)
        total_amount += item["total"]

    return {
        "purchase_type": "desktop_central",
        "payment": {
            "voucher": False,
            "type": "creditcard",
            "method": "01",
            "external_authentication": None,
            "card": {
                "installments": installments,
                "card_token": card_token
            },
            "capture": True,
            "amount": round(total_amount, 2)
        },
        "items": items,
        "ip": "",
        "delivery_date": delivery_date,
        "customer": {
            "sales_organization": "1684",
            "phone": "16 3322-5748",
            "payment_method": get_payment_method(installments),
            "origin_distribution_center": "1624",
            "order_number": order_number,
            "name": "CENTRAL PEREIRA SERVE SUPERMERCADO",
            "identity_type": "CNPJ",
            "identity": "02205030000160",
            "email": "centralsuper@hotmail.com",
            "birth_date": "1999-01-01",
            "addresses": [
                {
                    "zip_code": "14808-526",
                    "type": "delivery",
                    "street": "AV PEDRO GRECCO, 478 - HORTENCIAS",
                    "state": "SP",
                    "number": "",
                    "district": "",
                    "country": "BR",
                    "complement": "",
                    "city": "ARARAQUARA"
                },
                {
                    "zip_code": "14808-526",
                    "type": "billing",
                    "street": "AV PEDRO GRECCO",
                    "state": "SP",
                    "number": "478",
                    "district": "HORTENCIAS",
                    "country": "BR",
                    "complement": "",
                    "city": "ARARAQUARA"
                }
            ]
        },
        "additional_info": None
    }