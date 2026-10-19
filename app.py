"""
Titanic Dashboard - Application Streamlit Principale
=====================================================
Dashboard interactif de visualisation du dataset Titanic
avec 4 pages, filtres dynamiques et logging JSON.
"""

import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ajout du repertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from data.loader import load_titanic_data, get_age_bins

# ---------------------------------------------------------------------------
# Configuration du logger JSON
# ---------------------------------------------------------------------------
LOG_FILE = Path(__file__).parent / "app.log"


def setup_json_logger():
    """
    Configure le logger pour ecrire chaque interaction utilisateur
    au format JSON dans le fichier app.log.
    """
    logger = logging.getLogger("titanic_dashboard")
    logger.setLevel(logging.INFO)

    # Eviter les handlers dupliques lors du rechargement Streamlit
    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "page": getattr(record, "page", None),
                "filters": getattr(record, "filters", {}),
            }
            return json.dumps(log_entry, ensure_ascii=False)

    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)
    return logger


logger = setup_json_logger()


def log_interaction(page: str, message: str, filters: dict = None):
    """
    Enregistre une interaction utilisateur dans le log JSON.

    Args:
        page (str): Nom de la page visitée.
        message (str): Description de l'action.
        filters (dict, optional): Filtres appliques par l'utilisateur.
    """
    extra = {"page": page, "filters": filters or {}}
    logger.info(message, extra=extra)


# ---------------------------------------------------------------------------
# Chargement des donnees avec cache Streamlit
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Chargement du dataset Titanic...")
def get_data():
    """Charge et met en cache les donnees Titanic."""
    return load_titanic_data()


# ---------------------------------------------------------------------------
# Page 1 : Vue generale (KPI)
# ---------------------------------------------------------------------------
def render_overview(df: pd.DataFrame, filters: dict):
    """Affiche la page Vue generale avec les KPI principaux."""
    log_interaction("overview", "Visite de la page Vue generale", filters)

    st.markdown("## Vue Generale")
    st.markdown(
        "Vue d'ensemble du dataset Titanic avec les indicateurs cles de performance."
    )

    # KPI en haut
    col1, col2, col3, col4 = st.columns(4)

    total_passengers = len(df)
    survival_rate = (df["survived"].sum() / total_passengers * 100) if total_passengers > 0 else 0
    mean_age = df["age"].mean()
    mean_fare = df["fare"].mean()

    with col1:
        st.metric(label="Total Passagers", value=f"{total_passengers:,}")
    with col2:
        st.metric(label="Taux de Survie", value=f"{survival_rate:.1f}%")
    with col3:
        st.metric(label="Age Moyen", value=f"{mean_age:.1f} ans")
    with col4:
        st.metric(label="Prix Moyen Billet", value=f"{mean_fare:.2f} $")

    st.markdown("---")

    # Repartition par classe
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Repartition par Classe")
        class_counts = df["pclass"].value_counts().sort_index()
        fig_class = px.bar(
            class_counts,
            x=class_counts.index,
            y=class_counts.values,
            labels={"x": "Classe", "y": "Nombre de passagers"},
            color=class_counts.index,
            color_discrete_map={1: "#636EFA", 2: "#FECB52", 3: "#EF553B"},
            title="",
        )
        fig_class.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_class, use_container_width=True)

    with col_right:
        st.markdown("### Repartition par Sexe")
        sex_counts = df["sex"].value_counts()
        fig_sex = px.pie(
            sex_counts,
            values=sex_counts.values,
            names=sex_counts.index,
            color=sex_counts.index,
            color_discrete_map={"male": "#636EFA", "female": "#FF6692"},
            title="",
            hole=0.55,
        )
        fig_sex.update_layout(height=350)
        st.plotly_chart(fig_sex, use_container_width=True)

    st.markdown("---")

    # Distribution des ages
    st.markdown("### Distribution des Ages")
    fig_age = px.histogram(
        df,
        x="age",
        nbins=30,
        color="survived",
        color_discrete_map={0: "#EF553B", 1: "#00CC96"},
        labels={"survived": "Survie", "age": "Age (annees)"},
        title="",
    )
    fig_age.update_layout(
        height=350,
        legend_title="Survie",
        xaxis_title="Age (annees)",
        yaxis_title="Nombre de passagers",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        barmode="stack",
    )
    for idx, trace in enumerate(fig_age.data):
        trace.name = "Decede" if idx == 0 else "Survecu"
    st.plotly_chart(fig_age, use_container_width=True)


# ---------------------------------------------------------------------------
# Page 2 : Analyse de survie
# ---------------------------------------------------------------------------
def render_survival_analysis(df: pd.DataFrame, filters: dict):
    """Affiche l'analyse de survie avec graphiques detailles."""
    log_interaction("survival", "Visite de la page Analyse de survie", filters)

    st.markdown("## Analyse de Survie")
    st.markdown(
        "Analyse approfondie des facteurs influencant la survie des passagers du Titanic."
    )

    # Taux de survie par sexe (bar chart)
    st.markdown("### Taux de Survie par Sexe")
    survival_sex = df.groupby("sex")["survived"].mean() * 100
    fig_sex = px.bar(
        survival_sex,
        x=survival_sex.index,
        y=survival_sex.values,
        color=survival_sex.index,
        color_discrete_map={"male": "#636EFA", "female": "#FF6692"},
        labels={"x": "Sexe", "y": "Taux de survie (%)"},
        title="",
        text_auto=".1f",
    )
    fig_sex.update_layout(height=380, showlegend=False, yaxis_range=[0, 100])
    fig_sex.update_traces(textposition="outside")
    st.plotly_chart(fig_sex, use_container_width=True)

    # Taux de survie par classe (pie chart)
    st.markdown("### Taux de Survie par Classe")
    survival_class = df.groupby("pclass")["survived"].mean() * 100
    labels = [f"Classe {c}" for c in survival_class.index]
    fig_class = px.pie(
        values=survival_class.values,
        names=labels,
        hole=0.6,
        title="",
        color=labels,
        color_discrete_sequence=["#636EFA", "#FECB52", "#EF553B"],
    )
    fig_class.update_layout(height=380)
    fig_class.update_traces(
        textinfo="label+percent",
        texttemplate="%{label}<br>%{value:.1f}%",
    )
    st.plotly_chart(fig_class, use_container_width=True)

    # Taux de survie par tranche d'age (histogram)
    st.markdown("### Taux de Survie par Tranche d'Age")
    age_bins = [0, 12, 18, 35, 60, 100]
    age_labels = ["0-12", "13-18", "19-35", "36-60", "61+"]
    df_age = df.copy()
    df_age["age_group"] = pd.cut(df_age["age"], bins=age_bins, labels=age_labels, right=True)

    survival_age = df_age.groupby("age_group", observed=False)["survived"].mean() * 100
    fig_age = px.bar(
        x=survival_age.index.astype(str),
        y=survival_age.values,
        color=survival_age.values,
        color_continuous_scale="RdYlGn",
        labels={"x": "Tranche d'age", "y": "Taux de survie (%)"},
        title="",
        text_auto=".1f",
    )
    fig_age.update_layout(height=380, coloraxis_showscale=False, yaxis_range=[0, 100])
    fig_age.update_traces(textposition="outside")
    st.plotly_chart(fig_age, use_container_width=True)

    # Tableau recapitulatif
    st.markdown("### Tableau Recapitulatif")
    summary = df.groupby(["sex", "pclass"]).agg(
        total=("survived", "count"),
        survived_count=("survived", "sum"),
        survival_rate=("survived", "mean"),
        mean_age=("age", "mean"),
        mean_fare=("fare", "mean"),
    ).reset_index()
    summary["survival_rate"] = (summary["survival_rate"] * 100).round(1)
    summary.columns = [
        "Sexe", "Classe", "Total", "Survecus",
        "Taux survie (%)", "Age moyen", "Prix moyen ($)",
    ]
    st.dataframe(summary, use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# Page 3 : Filtres interactifs
# ---------------------------------------------------------------------------
def render_interactive_filters(df: pd.DataFrame, filters: dict):
    """Affiche les filtres interactifs avec mise a jour dynamique."""
    log_interaction("filters", "Visite de la page Filtres interactifs", filters)

    st.markdown("## Filtres Interactifs")
    st.markdown(
        "Utilisez les filtres ci-dessous pour explorer les donnees du Titanic "
        "de maniere interactive. Toutes les visualisations se mettent a jour automatiquement."
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        classes = sorted(df["pclass"].unique())
        selected_classes = st.multiselect(
            "Classe", options=classes, default=classes, format_func=lambda x: f"Classe {x}"
        )

    with col2:
        sexes = sorted(df["sex"].unique())
        selected_sexes = st.multiselect(
            "Sexe", options=sexes, default=sexes
        )

    with col3:
        age_labels = get_age_bins(df)
        selected_age_groups = st.multiselect(
            "Tranche d'age", options=age_labels, default=age_labels
        )

    # Appliquer les filtres
    df_filtered = df.copy()

    if selected_classes:
        df_filtered = df_filtered[df_filtered["pclass"].isin(selected_classes)]

    if selected_sexes:
        df_filtered = df_filtered[df_filtered["sex"].isin(selected_sexes)]

    if selected_age_groups:
        age_bins = [0, 12, 18, 35, 60, 100]
        age_labels_clean = ["0-12", "13-18", "19-35", "36-60", "61+"]
        mapping = dict(zip(age_labels, age_labels_clean))
        selected_clean = [mapping[a] for a in selected_age_groups if a in mapping]
        if selected_clean:
            df_filtered["age_group"] = pd.cut(
                df_filtered["age"], bins=age_bins, labels=age_labels_clean, right=True
            )
            df_filtered = df_filtered[df_filtered["age_group"].isin(selected_clean)]
            df_filtered = df_filtered.drop(columns=["age_group"], errors="ignore")

    # Enregistrer les filtres dans le log
    current_filters = {
        "classes": [str(c) for c in selected_classes],
        "sexes": selected_sexes,
        "age_groups": selected_age_groups,
    }
    log_interaction("filters", f"Filtres appliques : {len(df_filtered)} resultats", current_filters)

    # KPI filtres
    st.markdown("---")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    with col_kpi1:
        st.metric("Passagers filtres", value=f"{len(df_filtered):,}")
    with col_kpi2:
        if len(df_filtered) > 0:
            filt_survival = df_filtered["survived"].mean() * 100
        else:
            filt_survival = 0
        st.metric("Taux de survie (filtre)", value=f"{filt_survival:.1f}%")
    with col_kpi3:
        if len(df_filtered) > 0:
            filt_age = df_filtered["age"].mean()
        else:
            filt_age = 0
        st.metric("Age moyen (filtre)", value=f"{filt_age:.1f} ans")

    if len(df_filtered) == 0:
        st.warning("Aucun passager ne correspond aux filtres selectionnes.")
        return

    st.markdown("---")

    # Graphiques avec donnees filtrees
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Survie par Sexe (filtre)")
        surv_sex = df_filtered.groupby("sex")["survived"].mean() * 100
        fig = px.bar(
            surv_sex,
            x=surv_sex.index,
            y=surv_sex.values,
            color=surv_sex.index,
            color_discrete_map={"male": "#636EFA", "female": "#FF6692"},
            title="",
            text_auto=".1f",
        )
        fig.update_layout(height=350, showlegend=False, yaxis_range=[0, 100])
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### Survie par Classe (filtre)")
        surv_class = df_filtered.groupby("pclass")["survived"].mean() * 100
        fig2 = px.pie(
            values=surv_class.values,
            names=[f"Classe {c}" for c in surv_class.index],
            hole=0.55,
            title="",
            color_discrete_sequence=["#636EFA", "#FECB52", "#EF553B"],
        )
        fig2.update_layout(height=350)
        fig2.update_traces(textinfo="label+percent")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Distribution des Ages (filtre)")
    fig3 = px.histogram(
        df_filtered,
        x="age",
        nbins=25,
        color="survived",
        color_discrete_map={0: "#EF553B", 1: "#00CC96"},
        labels={"survived": "Survie", "age": "Age"},
        title="",
        barmode="stack",
    )
    fig3.update_layout(
        height=350,
        legend_title="Survie",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig3, use_container_width=True)


# ---------------------------------------------------------------------------
# Page 4 : Donnees brutes
# ---------------------------------------------------------------------------
def render_raw_data(df: pd.DataFrame, filters: dict):
    """Affiche les donnees brutes dans un tableau pagine avec export CSV."""
    log_interaction("raw_data", "Visite de la page Donnees brutes", filters)

    st.markdown("## Donnees Brutes")
    st.markdown(
        "Tableau complet des passagers du Titanic avec toutes les variables disponibles. "
        "Vous pouvez filtrer les colonnes et exporter les donnees au format CSV."
    )

    st.markdown(f"**Nombre total de lignes :** {len(df):,}")

    # Preparation du DataFrame pour l'affichage
    display_df = df.copy()
    # Renommer certaines colonnes pour une meilleure lisibilite
    column_renames = {
        "pclass": "Classe",
        "survived": "Survécu",
        "sex": "Sexe",
        "age": "Age",
        "sibsp": "Freres/Soeurs",
        "parch": "Parents/Enfants",
        "fare": "Prix Billet ($)",
        "embarked": "Embarquement",
        "class": "Classe (str)",
        "who": "Qui",
        "adult_male": "Homme Adulte",
        "embark_town": "Ville Embarquement",
        "alive": "Vivant",
        "alone": "Seul",
    }
    display_df = display_df.rename(columns=column_renames)

    # Barre de recherche
    search = st.text_input("Rechercher un passager (nom, sexe, classe...)", placeholder="Tapez ici...")
    if search:
        mask = display_df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]
        st.markdown(f"**Resultats trouves :** {len(display_df):,}")

    # Selection du nombre de lignes par page
    rows_per_page = st.selectbox("Lignes par page", options=[10, 25, 50, 100], index=1)

    # Pagination
    total_pages = max(1, (len(display_df) + rows_per_page - 1) // rows_per_page)
    page_number = st.number_input(
        "Page", min_value=1, max_value=total_pages, value=1, step=1
    )

    start_idx = (page_number - 1) * rows_per_page
    end_idx = start_idx + rows_per_page
    page_df = display_df.iloc[start_idx:end_idx]

    st.dataframe(page_df, use_container_width=True, hide_index=True, height=400)

    st.markdown(f"Affichage {start_idx + 1}-{min(end_idx, len(display_df))} sur {len(display_df)} lignes")

    # Export CSV
    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Exporter en CSV",
        data=csv,
        file_name="titanic_data.csv",
        mime="text/csv",
        type="primary",
    )

    log_interaction("raw_data", f"Export/consultation donnees brutes ({len(display_df)} lignes)")


# ---------------------------------------------------------------------------
# Fonction principale
# ---------------------------------------------------------------------------
def main():
    """Point d'entree de l'application Streamlit."""

    # Configuration de la page
    st.set_page_config(
        page_title="Titanic Dashboard",
        page_icon="🚢",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Titre principal
    st.title("🚢 Titanic Dashboard - Analyse Exploratoire")
    st.markdown(
        "Dashboard interactif pour l'analyse du dataset Titanic (891 passagers). "
        "Explorez les donnees, appliquez des filtres et decouvrez les facteurs de survie."
    )
    st.markdown("---")

    # Chargement des donnees
    try:
        df = get_data()
    except Exception as e:
        st.error(f"Erreur lors du chargement des donnees : {e}")
        st.stop()

    # Sidebar avec filtres globaux
    st.sidebar.title("Navigation & Filtres")

    page = st.sidebar.radio(
        "Pages",
        ["Vue Generale", "Analyse de Survie", "Filtres Interactifs", "Donnees Brutes"],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filtres Globaux")

    all_classes = sorted(df["pclass"].unique())
    global_classes = st.sidebar.multiselect(
        "Classe (global)", options=all_classes, default=all_classes,
        format_func=lambda x: f"Classe {x}", key="global_class"
    )

    all_sexes = sorted(df["sex"].unique())
    global_sexes = st.sidebar.multiselect(
        "Sexe (global)", options=all_sexes, default=all_sexes, key="global_sex"
    )

    all_age_labels = get_age_bins(df)
    global_ages = st.sidebar.multiselect(
        "Tranche d'age (global)", options=all_age_labels, default=all_age_labels,
        key="global_age"
    )

    # Appliquer les filtres globaux
    df_filtered = df.copy()

    if global_classes:
        df_filtered = df_filtered[df_filtered["pclass"].isin(global_classes)]

    if global_sexes:
        df_filtered = df_filtered[df_filtered["sex"].isin(global_sexes)]

    if global_ages:
        age_bins = [0, 12, 18, 35, 60, 100]
        age_labels_clean = ["0-12", "13-18", "19-35", "36-60", "61+"]
        mapping = dict(zip(all_age_labels, age_labels_clean))
        selected_clean = [mapping[a] for a in global_ages if a in mapping]
        if selected_clean:
            df_filtered["age_group"] = pd.cut(
                df_filtered["age"], bins=age_bins, labels=age_labels_clean, right=True
            )
            df_filtered = df_filtered[df_filtered["age_group"].isin(selected_clean)]
            df_filtered = df_filtered.drop(columns=["age_group"], errors="ignore")

    # Construction du dict des filtres pour le log
    current_filters = {
        "classes": [str(c) for c in global_classes],
        "sexes": global_sexes,
        "age_groups": global_ages,
    }

    # Log de la page visitee
    log_interaction(page.lower().replace(" ", "_"), f"Page visitee: {page}", current_filters)

    # Rendu de la page selectionnee
    if page == "Vue Generale":
        render_overview(df_filtered, current_filters)
    elif page == "Analyse de Survie":
        render_survival_analysis(df_filtered, current_filters)
    elif page == "Filtres Interactifs":
        render_interactive_filters(df_filtered, current_filters)
    elif page == "Donnees Brutes":
        render_raw_data(df_filtered, current_filters)

    # Footer
    st.markdown("---")
    st.caption(
        "Titanic Dashboard | Projet DevOps Data/IA | "
        "Donnees : seaborn.load_dataset('titanic') | "
        f"Passagers affiches : {len(df_filtered):,}"
    )


if __name__ == "__main__":
    main()
