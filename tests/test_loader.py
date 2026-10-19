"""
Tests unitaires pour le module data/loader.py
==============================================
Verifie le chargement, le nettoyage et la structure des donnees Titanic.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Ajout du repertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.loader import load_titanic_data, clean_data, get_age_bins


class TestLoadTitanicData:
    """Tests pour la fonction load_titanic_data."""

    def test_load_returns_dataframe(self):
        """Verifie que load_titanic_data retourne un DataFrame pandas."""
        df = load_titanic_data()
        assert isinstance(df, pd.DataFrame)

    def test_load_not_empty(self):
        """Verifie que le DataFrame n'est pas vide."""
        df = load_titanic_data()
        assert len(df) > 0, "Le DataFrame ne doit pas etre vide"

    def test_load_has_minimum_rows(self):
        """Verifie que le dataset contient au moins 800 lignes (891 attendues)."""
        df = load_titanic_data()
        assert len(df) >= 800, f"Attendu >= 800 lignes, obtenu {len(df)}"

    def test_expected_columns_exist(self):
        """Verifie la presence des colonnes obligatoires."""
        df = load_titanic_data()
        expected_columns = [
            "survived", "pclass", "sex", "age", "sibsp",
            "parch", "fare", "embarked", "class", "who",
            "adult_male", "embark_town", "alive", "alone",
        ]
        for col in expected_columns:
            assert col in df.columns, f"Colonne '{col}' manquante"

    def test_deck_column_removed(self):
        """Verifie que la colonne 'deck' a ete supprimee lors du nettoyage."""
        df = load_titanic_data()
        assert "deck" not in df.columns, "La colonne 'deck' devrait etre supprimee"


class TestCleanData:
    """Tests pour la fonction clean_data."""

    def test_clean_returns_dataframe(self):
        """Verifie que clean_data retourne un DataFrame."""
        df = pd.DataFrame({"a": [1, 2, 3]})
        result = clean_data(df)
        assert isinstance(result, pd.DataFrame)

    def test_no_null_age(self):
        """Verifie qu'il n'y a plus de valeurs nulles dans 'age'."""
        df = load_titanic_data()
        assert df["age"].isnull().sum() == 0, "La colonne 'age' ne doit pas contenir de valeurs nulles"

    def test_no_null_embarked(self):
        """Verifie qu'il n'y a plus de valeurs nulles dans 'embarked'."""
        df = load_titanic_data()
        assert df["embarked"].isnull().sum() == 0, "La colonne 'embarked' ne doit pas contenir de valeurs nulles"

    def test_no_null_fare(self):
        """Verifie qu'il n'y a plus de valeurs nulles dans 'fare'."""
        df = load_titanic_data()
        assert df["fare"].isnull().sum() == 0, "La colonne 'fare' ne doit pas contenir de valeurs nulles"

    def test_no_duplicates(self):
        """Verifie qu'il n'y a pas de lignes en double."""
        df = load_titanic_data()
        assert df.duplicated().sum() == 0, "Le DataFrame ne doit pas contenir de doublons"

    def test_age_is_numeric(self):
        """Verifie que la colonne 'age' est numerique."""
        df = load_titanic_data()
        assert pd.api.types.is_numeric_dtype(df["age"]), "La colonne 'age' doit etre numerique"

    def test_survived_is_binary(self):
        """Verifie que la colonne 'survived' contient uniquement 0 et 1."""
        df = load_titanic_data()
        unique_vals = set(df["survived"].unique())
        assert unique_vals.issubset({0, 1}), f"'survived' doit contenir uniquement 0 et 1, obtenu {unique_vals}"

    def test_pclass_is_valid(self):
        """Verifie que la colonne 'pclass' contient uniquement 1, 2 et 3."""
        df = load_titanic_data()
        unique_vals = set(df["pclass"].unique())
        assert unique_vals.issubset({1, 2, 3}), f"'pclass' doit contenir uniquement 1, 2, 3, obtenu {unique_vals}"

    def test_index_is_reset(self):
        """Verifie que l'index est reinitialise apres nettoyage."""
        df = load_titanic_data()
        assert df.index.tolist() == list(range(len(df))), "L'index doit etre reinitialise de 0 a n-1"


class TestGetAgeBins:
    """Tests pour la fonction get_age_bins."""

    def test_returns_list(self):
        """Verifie que get_age_bins retourne une liste."""
        df = load_titanic_data()
        result = get_age_bins(df)
        assert isinstance(result, list)

    def test_returns_5_bins(self):
        """Verifie que get_age_bins retourne exactement 5 tranches."""
        df = load_titanic_data()
        result = get_age_bins(df)
        assert len(result) == 5, f"Attendu 5 tranches, obtenu {len(result)}"

    def test_bins_are_strings(self):
        """Verifie que les tranches sont des chaines de caracteres."""
        df = load_titanic_data()
        result = get_age_bins(df)
        for label in result:
            assert isinstance(label, str), f"Chaque tranche doit etre une chaine, obtenu {type(label)}"


class TestDataQuality:
    """Tests de qualite des donnees."""

    def test_survival_rate_reasonable(self):
        """Verifie que le taux de survie global est entre 20% et 50%."""
        df = load_titanic_data()
        rate = df["survived"].mean() * 100
        assert 20 <= rate <= 50, f"Taux de survie {rate:.1f}% hors plage attendue [20, 50]"

    def test_age_range_reasonable(self):
        """Verifie que les ages sont dans une plage raisonnable (0-100)."""
        df = load_titanic_data()
        assert df["age"].min() >= 0, "L'age minimum doit etre >= 0"
        assert df["age"].max() <= 100, "L'age maximum doit etre <= 100"

    def test_fare_positive(self):
        """Verifie que tous les prix de billet sont positifs."""
        df = load_titanic_data()
        assert (df["fare"] >= 0).all(), "Tous les prix de billet doivent etre positifs"

    def test_sex_values(self):
        """Verifie que la colonne 'sex' contient uniquement 'male' et 'female'."""
        df = load_titanic_data()
        unique_sexes = set(df["sex"].unique())
        assert unique_sexes.issubset({"male", "female"}), f"Valeurs de 'sex' inattendues : {unique_sexes}"
