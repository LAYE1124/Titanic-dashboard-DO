#!/usr/bin/env python3
"""
Script de simulation d'interactions utilisateur
================================================
Genere des interactions fictives dans app.log pour alimenter
le dashboard Kibana ELK avec des donnees de demonstration.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent / "app.log"

PAGES = ["overview", "survival", "filters", "raw_data"]
FILTERS_COMBOS = [
    {"classes": ["1", "2", "3"], "sexes": ["male", "female"], "age_groups": ["0-12 (Enfant)", "13-18 (Adolescent)", "19-35 (Jeune adulte)", "36-60 (Adulte)", "61+ (Senior)"]},
    {"classes": ["1"], "sexes": ["female"], "age_groups": ["0-12 (Enfant)", "13-18 (Adolescent)", "19-35 (Jeune adulte)"]},
    {"classes": ["3"], "sexes": ["male"], "age_groups": ["19-35 (Jeune adulte)", "36-60 (Adulte)"]},
    {"classes": ["1", "2"], "sexes": ["female"], "age_groups": ["19-35 (Jeune adulte)", "36-60 (Adulte)", "61+ (Senior)"]},
    {"classes": ["2", "3"], "sexes": ["male"], "age_groups": ["0-12 (Enfant)", "13-18 (Adolescent)"]},
    {"classes": ["1"], "sexes": ["female", "male"], "age_groups": ["19-35 (Jeune adulte)"]},
    {"classes": ["2"], "sexes": ["female"], "age_groups": ["36-60 (Adulte)", "61+ (Senior)"]},
]

MESSAGES = {
    "overview": [
        "Visite de la page Vue generale",
        "Page Vue generale consultee",
        "Dashboard Vue generale affiche",
    ],
    "survival": [
        "Visite de la page Analyse de survie",
        "Analyse de survie consultee",
        "Graphiques de survie affiches",
    ],
    "filters": [
        "Visite de la page Filtres interactifs",
        "Filtres appliques sur les donnees",
        "Exploration interactive des donnees",
    ],
    "raw_data": [
        "Visite de la page Donnees brutes",
        "Export/consultation donnees brutes",
        "Tableau de donnees consulte",
    ],
}


def generate_log_entries(num_entries: int = 200) -> list:
    """Genere une liste d'entrees de log fictives."""
    entries = []
    base_time = datetime.now() - timedelta(hours=48)

    for i in range(num_entries):
        page = random.choice(PAGES)
        filters = random.choice(FILTERS_COMBOS) if page == "filters" else {}
        message = random.choice(MESSAGES[page])

        if page == "raw_data":
            message += f" ({random.randint(50, 891)} lignes)"
        elif page == "filters":
            message += f" ({random.randint(100, 800)} resultats)"

        timestamp = base_time + timedelta(
            minutes=random.randint(0, 2880),
            seconds=random.randint(0, 59),
        )

        entry = {
            "timestamp": timestamp.isoformat(),
            "level": "INFO",
            "message": message,
            "page": page,
            "filters": filters,
        }
        entries.append(entry)

    # Trier par timestamp
    entries.sort(key=lambda x: x["timestamp"])
    return entries


def write_logs(entries: list):
    """Ecrit les entrees de log dans app.log."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for entry in entries:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"{len(entries)} entrees de log ecrites dans {LOG_FILE}")


def main():
    print("=" * 50)
    print("Simulation d'interactions utilisateur")
    print("=" * 50)
    print()

    # Nettoyer le fichier existant
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        print(f"Fichier {LOG_FILE} nettoye.")

    # Generer et ecrire les logs
    entries = generate_log_entries(200)
    write_logs(entries)

    print()
    print("Distribution par page :")
    page_counts = {}
    for e in entries:
        p = e["page"]
        page_counts[p] = page_counts.get(p, 0) + 1
    for page, count in sorted(page_counts.items()):
        print(f"  - {page}: {count} interactions")

    print()
    print(f"Periode couverte : {entries[0]['timestamp']} -> {entries[-1]['timestamp']}")
    print()
    print("Les logs sont prets pour l'indexation dans ELK Stack.")


if __name__ == "__main__":
    main()
