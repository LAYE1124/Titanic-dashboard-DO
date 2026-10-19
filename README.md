# Titanic Dashboard - Projet DevOps Data/IA

Dashboard interactif Streamlit pour l'analyse exploratoire du dataset Titanic avec un cycle DevOps complet.

## Apercu

Application web interactive permettant d'explorer le dataset Titanic (891 passagers, 15 variables) a travers 4 pages de visualisation :
- **Vue generale** : KPI principaux, repartition par classe/sexe/age
- **Analyse de survie** : Taux de survie par sexe, classe et tranche d'age
- **Filtres interactifs** : Exploration dynamique avec sidebar de filtres
- **Donnees brutes** : Tableau pagine avec export CSV

## Stack Technologique

| Outil | Role |
|-------|------|
| Python 3.11 | Langage principal |
| Streamlit | Framework web interactif |
| Plotly | Graphiques interactifs |
| Pandas / Seaborn | Manipulation et chargement des donnees |
| Pytest | Tests unitaires |
| Flake8 | Linting du code Python |
| Docker | Conteneurisation |
| DockerHub | Registre d'images |
| GitHub Actions | Pipeline CI/CD |
| ELK Stack | Monitoring des logs |
| ydata-profiling | Rapport d'analyse automatique |

## Structure du Projet

```
titanic-dashboard/
├── app.py                      # Application Streamlit principale
├── data/
│   ├── __init__.py
│   └── loader.py               # Chargement et nettoyage du dataset Titanic
├── tests/
│   ├── __init__.py
│   └── test_loader.py          # Tests unitaires pytest
├── scripts/
│   └── simulate_interactions.py # Script de simulation d'interactions ELK
├── requirements.txt            # Dependances Python
├── Dockerfile                  # Image Docker de l'application
├── docker-compose.yml          # Stack complete (App + ELK)
├── filebeat/
│   └── filebeat.yml            # Configuration Filebeat
├── logstash/
│   └── pipeline/
│       └── logstash.conf       # Pipeline Logstash
├── .github/
│   └── workflows/
│       ├── ci.yml              # Pipeline CI/CD (4 jobs)
│       └── report.yml          # Generation du rapport profiling
├── .gitignore
└── .dockerignore
```

## Installation et Execution

### Prerequis
- Python 3.11+
- pip

### Installation locale

```bash
# Cloner le depot
git clone https://github.com/votre-user/titanic-dashboard.git
cd titanic-dashboard

# Creer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer les dependances
pip install -r requirements.txt

# Lancer l'application
streamlit run app.py
```

L'application est accessible sur : **http://localhost:8501**

### Docker

```bash
# Build de l'image
docker build -t titanic-dashboard:v1.0 .

# Lancer le conteneur
docker run -d -p 8501:8501 --name titanic-dashboard titanic-dashboard:v1.0
```

### Docker Compose (avec ELK Stack)

```bash
# Lancer la stack complete
docker compose up -d

# Arreter la stack
docker compose down
```

| Service | URL |
|---------|-----|
| Dashboard Streamlit | http://localhost:8501 |
| Kibana | http://localhost:5601 |
| Elasticsearch | http://localhost:9200 |

## Tests

```bash
# Lancer les tests unitaires
pytest tests/ -v

# Lancer les tests avec couverture
pytest tests/ -v --cov=data --cov-report=term-missing

# Linting du code
flake8 app.py data/loader.py tests/ --max-line-length=100
```

## Pipeline CI/CD (GitHub Actions)

Le pipeline est declenche automatiquement lors d'un push sur `main` ou `develop` :

1. **Job 1 - Lint & Test** : flake8 + pytest (bloquant si erreur)
2. **Job 2 - Rapport** : Generation rapport HTML + publication artefact
3. **Job 3 - Docker Build & Push** : Build image + push DockerHub
4. **Job 4 - Deploy** : Deploiement avec docker-compose

### Variables requises (GitHub Secrets)

| Secret | Description |
|--------|-------------|
| `DOCKER_USERNAME` | Nom d'utilisateur DockerHub |
| `DOCKER_PASSWORD` | Mot de passe ou token d'acces DockerHub |

## Monitoring ELK

### Simulation d'interactions

```bash
# Generer des logs de demonstration
python scripts/simulate_interactions.py
```

### Visualisations Kibana

Une fois la stack ELK demarree, accedez a Kibana sur http://localhost:5601 et creez les visualisations suivantes :

1. **Pages les plus visitees** (Bar chart) : Nombre de visites par page
2. **Filtres appliques** (Pie chart) : Distribution des filtres utilises
3. **Activite dans le temps** (Line chart) : Volume d'interactions par heure

## Rapport d'Analyse

```bash
# Generer le rapport de profiling du dataset
python -c "
from data.loader import load_titanic_data
from ydata_profiling import ProfileReport
df = load_titanic_data()
profile = ProfileReport(df, title='Titanic Report', minimal=True)
profile.to_file('report.html')
"
```

## Auteur

Projet realise dans le cadre du module DevOps - Filiere Data/IA

## Licence

Ce projet est utilise a des fins pedagogiques uniquement.
