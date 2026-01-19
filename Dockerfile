# 1. Image de base
FROM python:3.11-slim

# 2. Dossier de travail
WORKDIR /app

# 3. Mise à jour des outils de base
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 4. Copie des fichiers de configuration ET du code source
# IL FAUT COPIER LE CODE AVANT L'INSTALLATION pour un projet en "src-layout"
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY tests/ ./tests/

# 5. Installation du projet et des dépendances
# On retire le mode éditable (-e) qui est inutile en Docker de production
# On garde [dev] pour tes spécifications techniques (tests unitaires)
RUN pip install --no-cache-dir ".[dev]"

# 6. Copie du reste (fichiers comme .gitignore, LICENSE, etc.)
COPY . .

# 7. Port FastAPI
EXPOSE 8000

# 8. Commande de lancement
# Note : uvicorn cherchera dans le dossier de travail /app
CMD ["uvicorn", "src.banking_transaction_api.main:app", "--host", "0.0.0.0", "--port", "8000"]