import pandas as pd
import os

def load_dataset(file_name: str, nrows: int = 5000):
    path = os.path.join("data", file_name)
    if os.path.exists(path):
        df = pd.read_csv(path, nrows=nrows)
        # LA CORRECTION : Remplace les valeurs manquantes (NaN) par des valeurs valides pour JSON
        return df.fillna(0)
    return pd.DataFrame()