# =============================================================================
# Dockerfile - Titanic Dashboard Streamlit
# =============================================================================
# Image de base Python 3.11 slim pour une taille minimale
# Port expose : 8501 (port par defaut Streamlit)
# =============================================================================

FROM python:3.11-slim

# Labels de metadata
LABEL maintainer="titanic-dashboard"
LABEL description="Dashboard Streamlit interactif - Titanic Dataset"
LABEL version="1.0"

# Definition du repertoire de travail
WORKDIR /app

# Installation des dependances systeme
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copie et installation des dependances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code de l'application
COPY app.py .
COPY data/ ./data/

# Creation du repertoire pour les logs
RUN mkdir -p /app/logs

# Exposition du port Streamlit
EXPOSE 8501

# Configuration de l'environnement Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV PYTHONUNBUFFERED=1

# Point d'entree
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
