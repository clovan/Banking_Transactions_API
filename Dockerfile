# 1. Utilisation de Python 3.11 (compatible avec ton >= 3.10)
FROM python:3.11-slim

# 2. Dossier de travail dans le conteneur
WORKDIR /app

# 3. Installation des outils de build
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 4. Copie des fichiers de configuration en premier (Optimisation du cache)
COPY pyproject.toml README.md ./

# 5. Installation des dépendances de production ET de dev (pour pouvoir tester)
# On utilise [dev] car tu as défini tes tests dans optional-dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# 6. Copie tout le reste du code source
COPY . .

# 7. Port utilisé par FastAPI
EXPOSE 8000

# 8. Commande de lancement (adapter "main:app" si ton fichier s'appelle différemment)
CMD ["uvicorn", "src.banking_transaction_api.main:app", "--host", "0.0.0.0", "--port", "8000"]