# 🏦 Banking Transactions API

## 🏦 Banking Transactions API  
API REST complète permettant d’exposer, analyser et visualiser des données de transactions bancaires fictives.  
Ce projet a été réalisé dans le cadre du **MBA ESG – Projet FastAPI**.

L’application comporte :

- une **API FastAPI** (backend)  
- une **application Streamlit** (frontend)  
- un **module Python installable**  
- des **tests unitaires**  
- un **taux de couverture**  
- une **architecture professionnelle**  

---

## 💼 Résumé
Banking Transaction API est solution complète d’analyse de transactions bancaires comprenant :

- exposition des données via une API FastAPI

- visualisation et exploration via une application Streamlit

- détection simplifiée de fraude

- statistiques détaillées (montants, types, tendances journalières)

- packaging Python (pip install -e .)

- tests unitaires + couverture (pytest --cov)


## 📁 Architecture du projet

```
Banking_Transactions_API/
│
├── src/
│   └── banking_transaction_api/
│       ├── routers/
│       │   ├── customer.py
│       │   ├── fraud.py
│       │   ├── stats.py
│       │   ├── system.py
│       │   ├── transactions.py
│       │   └── users.py
│       │
│       ├── services/
│       │   ├── data_loader.py
│       │   └── main.py
│       │
│       └── __init__.py
│
├── Streamlit_app/
│   ├── app.py
│   ├── config/settings.py
│   ├── pages/
│   │   ├── 1_Transactions.py
│   │   ├── 2_Statistiques.py
│   │   ├── 3_Fraude.py
│   │   └── 4_Analyse_Clients.py
│   └── services/
│       ├── api_client.py
│       ├── customer_service.py
│       ├── fraud_service.py
│       ├── stats_service.py
│       └── transactions_service.py
│
├── tests/
│   ├── test_frauds.py
│   ├── test_json_validation.py
│   ├── test_performance.py
│   ├── test_simple.py
│   ├── test_stats.py
│   ├── test_system.py
│   ├── test_transactions.py
│   └── services/
│       ├── test_fraud_detection_service.py
│       └── test_stats_service.py
│
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/clovisMbeng/Banking_Transactions_API.git
cd Banking_Transactions_API
```

### 2. Créer et activer l’environnement virtuel

```bash
python -m venv .venv
.\.venv\Scripts\Activate
```

Tu dois voir apparaître :

```
(.venv)
```


### 3. Installer les dépendances du projet

```bash
pip install -e .
```

Cette commande lit automatiquement ton **pyproject.toml**.  
C’est la **commande magique**.

---

## ▶️ Lancer l’API FastAPI

Depuis la racine du projet :

```bash
uvicorn src.banking_transaction_api.main:app --reload
```

Documentation interactive :

- Swagger UI : `http://127.0.0.1:8000/docs` 

---

## 🖥️ Lancer l’application Streamlit

Se placer dans le dossier Streamlit :

```bash
cd Streamlit_app
streamlit run app.py
```

---

## 📡 Endpoints principaux

### 🔹 Transactions
- GET `/api/transactions`
- GET `/api/transactions/{id}`
- GET `/api/transactions/recent`
- GET `/api/transactions/by-customer/{customer_id}`
- GET `/api/transactions/to-customer/{customer_id}`

### 🔹 Statistiques
- GET `/api/stats/overview`
- GET `/api/stats/amount-distribution`
- GET `/api/stats/by-type`
- GET `/api/stats/daily`

### 🔹 Fraude
- GET `/api/fraud/summary`
- GET `/api/fraud/by-type`
- POST `/api/fraud/predict`

### 🔹 Clients
- GET `/api/customers`
- GET `/api/customers/{customer_id}`
- GET `/api/customers/top`

### 🔹 Système
- GET `/api/system/health`
- GET `/api/system/metadata`

---

## 📊 Exemple de réponse — 10 dernières transactions

```json
[
  {
    "id": 7535094,
    "date": "2010-01-16 11:11:00",
    "client_id": 1019,
    "card_id": 2602,
    "amount": 30.49,
    "transaction_type": "Swipe Transaction",
    "merchant_id": 32606,
    "merchant_city": "Chino",
    "merchant_state": "CA",
    "zip": 91710,
    "mcc": 7832,
    "errors": 0,
    "isFraud": 0,
    "type": 0
  },
  {
    "id": 7535093,
    "date": "2010-01-16 11:11:00",
    "client_id": 984,
    "card_id": 2796,
    "amount": 100,
    "transaction_type": "Swipe Transaction",
    "merchant_id": 27092,
    "merchant_city": "Fort Pierce",
    "merchant_state": "FL",
    "zip": 34951,
    "mcc": 4829,
    "errors": 0,
    "isFraud": 0,
    "type": 0
  }
]
```

---

## 🧪 Tests unitaires

### Installer les outils de test

```bash
pip install pytest pytest-cov
```

### Lancer tous les tests

Depuis la racine du projet :

```bash
pytest
```

### Taux de couverture

```bash
pytest --cov=src/banking_transaction_api --cov-report=term-missing
```

---

## 📦 Build du paquet Python
Methode standard
il faut installer

```bash
pip install build
```
ensuite faire

```bash
python -m build
```

Les fichiers générés apparaissent dans `dist/`.

---

## 👥 Auteurs

- **Milaine MEYOUDOM**  
- **Clovis MBENG**  
- **Irmeline GUEVOU**  
- **Amina SALIMI**

---

## 📄 Licence

Projet académique — MBA ESG — non destiné à un usage commercial.
