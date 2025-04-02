from locust import HttpUser, task, between
import json
import random
import time
import hashlib
from enum import Enum, auto
from store_requests.bodys import get_token_body, get_card_token_body, get_order_body
from store_requests.config import Config
from store_requests.helpers import generate_order_number

class RequestState(Enum):
    START = auto()
    GOT_AUTH_TOKEN = auto()
    GOT_ACCESS_CARD_TOKEN = auto()
    GOT_CARD_TOKEN = auto()
    COMPLETED = auto()

class YggPerformanceUser(HttpUser):
    wait_time = between(1, 3)
    host = Config.BASE_URL
    request_timeout = 60
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reset_state()

    def reset_state(self):
        """Reinicia o estado do usuário"""
        self.state = RequestState.START
        self.auth_token = None
        self.card_access_token = None
        self.card_token = None
        self.order_number = generate_order_number() #Gera um order_number e aloca para a order

    @task
    def execute_flow(self):
        try:
            if self.state == RequestState.START:
                self.get_auth_token()
            
            elif self.state == RequestState.GOT_AUTH_TOKEN:
                self.get_access_card_token()
            
            elif self.state == RequestState.GOT_ACCESS_CARD_TOKEN:
                self.get_card_token()
            
            elif self.state == RequestState.GOT_CARD_TOKEN:
                self.create_order()
            
            elif self.state == RequestState.COMPLETED:
                self.reset_state()  # Reinicia para novo ciclo
                
        except Exception as e:
            print(f"⚠️ Erro no fluxo | Order: {self.order_number} | Erro: {str(e)}")
            time.sleep(3)
            self.reset_state()

    def get_auth_token(self):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        with self.client.post("/token",
                           headers=headers, name= "token ygg",
                           data=get_token_body(),
                           timeout=self.request_timeout,
                           catch_response=True) as response:
            
            if response.ok and "access_token" in response.json():
                self.auth_token = response.json()["access_token"]
                self.state = RequestState.GOT_AUTH_TOKEN
                print(f"✅ AuthToken obtido | Order: {self.order_number}")
            else:
                response.failure(f"Falha no AuthToken: {response.text}")
                time.sleep(2)

    def get_access_card_token(self):
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
            "TENANT_ID": Config.TENANT_ID
        }
        with self.client.get("/financial/payments/v1/braspag/token/credit",
                           headers=headers, name= "token braspag",
                           timeout=self.request_timeout,
                           catch_response=True) as response:
            
            if response.ok:
                json_data = response.json()
                if json_data.get("success") and "accessToken" in json_data.get("results", {}):
                    self.card_access_token = json_data["results"]["accessToken"]
                    self.state = RequestState.GOT_ACCESS_CARD_TOKEN
                    print(f"✅ AccessCardToken obtido | Order: {self.order_number}")
                else:
                    response.failure("Resposta inválida do AccessCardToken")
                    self.state = RequestState.START  # Reinicia o fluxo
            else:
                response.failure(f"HTTP {response.status_code}")
                self.state = RequestState.START

    def get_card_token(self):
        headers = {
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded"
        }
        with self.client.post(f"{Config.BRASPAG_URL}/post/api/public/v1/card",
                            headers=headers, name= "cark token",
                            data=get_card_token_body(self.card_access_token),
                            timeout=self.request_timeout,
                            catch_response=True) as response:
            
            if response.ok and "CardToken" in response.json():
                self.card_token = response.json()["CardToken"]
                self.state = RequestState.GOT_CARD_TOKEN
                print(f"✅ CardToken gerado | Order: {self.order_number}")
            else:
                response.failure(f"Falha ao gerar CardToken: {response.text}")
                self.state = RequestState.GOT_ACCESS_CARD_TOKEN  # Tenta novamente

    def create_order(self):
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json",
            "X-Request-ID": self.order_number,
            "TENANT_ID": Config.TENANT_ID
        }
        
        try:
            payload = get_order_body(
                card_token=self.card_token,
                order_number=self.order_number,
                installments=random.randint(1, 3),
                auth_token=self.auth_token
            )
            
            with self.client.post("/external/bff/central/orders",
                                headers=headers,
                                name="bff order",
                                data=json.dumps(payload),
                                timeout=self.request_timeout,
                                catch_response=True) as response:
                
                if response.ok:
                    json_response = response.json()
                    if json_response.get("success", False):
                        received_order = json_response.get("order_number", "N/A")
                        print(f"✅ Pedido concluído | Gerado: {self.order_number} | Recebido: {received_order}")
                        self.state = RequestState.COMPLETED
                    else:
                        error_msg = json_response.get("messages", [{"key": "Error", "value": "Erro desconhecido"}])
                        formatted_errors = ", ".join([f"{e['key']}: {e['value']}" for e in error_msg])
                        response.failure(f"Falha no pedido: {formatted_errors} | Order: {self.order_number}")
                        self.state = RequestState.GOT_CARD_TOKEN
                else:
                    response.failure(f"HTTP {response.status_code} - {response.text}")
                    self.state = RequestState.GOT_CARD_TOKEN
                    
        except Exception as e:
            print(f"⚠️ Erro ao criar pedido | Order: {self.order_number} | Erro: {str(e)}")
            self.state = RequestState.GOT_CARD_TOKEN