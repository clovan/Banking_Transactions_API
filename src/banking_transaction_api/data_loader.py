import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any

class DataLoader:
    _instance = None
    _data: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        # Usamos Path para manejar rutas de forma más limpia
        # Localiza la raíz del proyecto desde este archivo
        base_path = Path(__file__).resolve().parent.parent.parent / "data"
        
        # Carga de CSVs (Ajustado a lo que se ve en tu captura)
        self._data["transactions"] = pd.read_csv(base_path / "transactions_data.csv")
        self._data["users"] = pd.read_csv(base_path / "users_data.csv")
        
        # NOTA: cards_data.csv no se ve en tu captura, lo comento para evitar errores
        # self._data["cards"] = pd.read_csv(base_path / "cards_data.csv")
        
        # Carga de JSONs
        with open(base_path / "mcc_codes.json", 'r') as f:
            self._data["mcc_codes"] = json.load(f)
            
        with open(base_path / "train_fraud_labels.json", 'r') as f:
            self._data["fraud_labels"] = json.load(f)

        self._preprocess_transactions()
        self._preprocess_users()

    def _preprocess_transactions(self):
        df = self._data["transactions"]
        # Limpieza de montos
        if 'amount' in df.columns:
            df['amount'] = df['amount'].replace(r'[$,]', '', regex=True).astype(float)
        
        fraud_labels = self._data["fraud_labels"]
        
        if isinstance(fraud_labels, dict) and "target" in fraud_labels:
            target_dict = fraud_labels["target"]
            fraud_map = {str(k): (1 if v == "Yes" else 0) for k, v in target_dict.items()}
            df['is_fraud'] = df['id'].astype(str).map(fraud_map)
            df['is_fraud'] = df['is_fraud'].fillna(0).astype(int)
        
        if 'use_chip' in df.columns and 'type' not in df.columns:
            df['type'] = df['use_chip']
        
        self._data["transactions"] = df

    def _preprocess_users(self):
        df = self._data["users"]
        for col in ['per_capita_income', 'yearly_income', 'total_debt']:
            if col in df.columns:
                df[col] = df[col].replace(r'[$,]', '', regex=True).astype(float)
        self._data["users"] = df

    @property
    def transactions(self) -> pd.DataFrame:
        return self._data.get("transactions")

    @property
    def users(self) -> pd.DataFrame:
        return self._data.get("users")

    @property
    def mcc_codes(self) -> Dict:
        return self._data.get("mcc_codes")