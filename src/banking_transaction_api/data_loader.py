import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any

class DataLoader:
    """
    Singleton class to load and preprocess data files.
    Ensures data is loaded only once into memory for the entire application.
    """
    _instance = None
    _data: Dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataLoader, cls).__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        # Define the base path for the data folder relative to this script
        # Structure: src/banking_transaction_api/data_loader.py -> ../../data
        base_path = Path(__file__).resolve().parent.parent.parent / "data"
        
        # Load CSV files (Matches the files seen in your explorer)
        self._data["transactions"] = pd.read_csv(base_path / "transactions_data.csv")
        self._data["users"] = pd.read_csv(base_path / "users_data.csv")
        
        # Load JSON files
        with open(base_path / "mcc_codes.json", 'r') as f:
            self._data["mcc_codes"] = json.load(f)
            
        with open(base_path / "train_fraud_labels.json", 'r') as f:
            self._data["fraud_labels"] = json.load(f)

        # Apply preprocessing steps
        self._preprocess_transactions()
        self._preprocess_users()

    def _preprocess_transactions(self):
        df = self._data["transactions"]
        
        # Clean amount column: convert currency strings (e.g., "$77.00") to floats
        if 'amount' in df.columns:
            df['amount'] = df['amount'].replace(r'[$,]', '', regex=True).astype(float)
        
        # Map fraud labels from the JSON structure: {"target": {"id": "Yes"/"No"}}
        fraud_labels = self._data["fraud_labels"]
        
        if isinstance(fraud_labels, dict) and "target" in fraud_labels:
            target_dict = fraud_labels["target"]
            # Convert "Yes" to 1 and "No" to 0
            fraud_map = {str(k): (1 if v == "Yes" else 0) for k, v in target_dict.items()}
            df['is_fraud'] = df['id'].astype(str).map(fraud_map)
            df['is_fraud'] = df['is_fraud'].fillna(0).astype(int)
        
        # Add 'type' column based on 'use_chip' for spec compatibility
        if 'use_chip' in df.columns and 'type' not in df.columns:
            df['type'] = df['use_chip']
        
        self._data["transactions"] = df

    def _preprocess_users(self):
        df = self._data["users"]
        # Clean currency columns in users dataset
        currency_cols = ['per_capita_income', 'yearly_income', 'total_debt']
        for col in currency_cols:
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
    
    @property
    def fraud_labels(self) -> Dict:
        return self._data.get("fraud_labels")
    