# Ygg Performance BFF - Monomarca

## ✅ Pré-requisitos

Antes de executar este projeto, certifique-se de ter:

```plaintext
1.Python 3.10+ instalado.
2.Dependências listadas no arquivo requirements.txt (se aplicável): pip install -r requirements.txt
```

## Configuração do Ambiente

1. **Crie um ambiente virtual:**

    ```bash
    python3 -m venv ygg_performance_proxy_souk_env
    ```

2. **Ative o ambiente virtual:**

    ```bash
    No Linux/Mac:

    source ygg_performance_proxy_souk_env/bin/activate
    ```

    ```bash
    No Windows:

    ygg_performance_proxy_souk_env\Scripts\activate
    ```

## 📝 Execução Locust

```plaintext
locust -f locustfile.py (interface grafica -> localhost:8089)
locust --headless -f locustfile.py --users 1 --spawn-rate 1
locust --headless -f locustfile.py --tags test1 --users 1 --spawn-rate 1
locust -f ./locustfiles/locustfile.py
locust -f locustfiles/ --users 10 --spawn-rate 1

-u 10: Define o número de usuários simultâneos.
-r 2: Define a taxa de criação de novos usuários (2 usuários por segundo).
--run-time 1m: Define a duração do teste (1 minuto).
```
