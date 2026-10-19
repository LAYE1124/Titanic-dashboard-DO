"""
Titanic Dataset Loader Module
==============================
Charge le dataset Titanic depuis seaborn, nettoie les donnees
et retourne un DataFrame pret pour l'analyse.
"""

import pandas as pd
import seaborn as sns
import logging

logger = logging.getLogger(__name__)


def load_titanic_data() -> pd.DataFrame:
    """
    Charge le dataset Titanic depuis seaborn.
    
    Le dataset est charge via sns.load_dataset('titanic') qui retourne
    891 passagers avec 15 variables incluant :
    - survived : survie (0=Non, 1=Oui)
    - pclass   : classe du ticket (1, 2, 3)
    - sex      : sexe (male, female)
    - age      : age en annees
    - sibsp    : nombre de freres/soeurs/epoux a bord
    - parch    : nombre de parents/enfants a bord
    - fare     : prix du ticket
    - embarked : port d'embarquement (C=Cherbourg, Q=Queenstown, S=Southampton)
    - class    : classe en chaine (First, Second, Third)
    - who      : homme, femme ou enfant
    - adult_male : booleen indiquant un homme adulte
    - deck     : pont du navire
    - embark_town : ville d'embarquement
    - alive    : survie en chaine (yes, no)
    - alone    : voyage seul
    
    Returns:
        pd.DataFrame: DataFrame nettoyé du dataset Titanic.
        
    Raises:
        Exception: Si le chargement depuis seaborn echoue.
    """
    logger.info("Chargement du dataset Titanic depuis seaborn...")
    
    try:
        df = sns.load_dataset('titanic')
        logger.info(f"Dataset charge avec succes : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    except Exception as e:
        logger.error(f"Erreur lors du chargement du dataset : {e}")
        raise Exception(f"Impossible de charger le dataset Titanic : {e}")
    
    df = clean_data(df)
    logger.info("Donnees nettoyees avec succes")
    
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie le DataFrame Titanic.
    
    Operations effectuees :
    - Suppression des lignes en double
    - Remplacement des valeurs nulles de 'age' par la mediane
    - Remplacement des valeurs nulles de 'embarked' par le mode
    - Remplacement des valeurs nulles de 'embark_town' par le mode
    - Suppression de la colonne 'deck' (trop de valeurs manquantes >75%)
    - Conversion de 'age' en type numerique arrondi
    
    Args:
        df (pd.DataFrame): DataFrame brut du Titanic.
        
    Returns:
        pd.DataFrame: DataFrame nettoye.
    """
    initial_rows = len(df)
    
    # Suppression des doublons
    df = df.drop_duplicates()
    
    # Remplacement des valeurs nulles pour 'age' par la mediane
    if 'age' in df.columns and df['age'].isnull().any():
        median_age = df['age'].median()
        df['age'] = df['age'].fillna(median_age)
        df['age'] = df['age'].round(1)
        logger.info(f"Valeurs nulles de 'age' remplacees par la mediane ({median_age})")
    
    # Remplacement des valeurs nulles pour 'embarked' par le mode
    if 'embarked' in df.columns and df['embarked'].isnull().any():
        mode_embarked = df['embarked'].mode()[0]
        df['embarked'] = df['embarked'].fillna(mode_embarked)
        logger.info(f"Valeurs nulles de 'embarked' remplacees par le mode ({mode_embarked})")
    
    # Remplacement des valeurs nulles pour 'embark_town' par le mode
    if 'embark_town' in df.columns and df['embark_town'].isnull().any():
        mode_town = df['embark_town'].mode()[0]
        df['embark_town'] = df['embark_town'].fillna(mode_town)
        logger.info(f"Valeurs nulles de 'embark_town' remplacees par le mode ({mode_town})")
    
    # Remplacement des valeurs nulles pour 'fare' par la mediane
    if 'fare' in df.columns and df['fare'].isnull().any():
        median_fare = df['fare'].median()
        df['fare'] = df['fare'].fillna(median_fare)
        logger.info(f"Valeurs nulles de 'fare' remplacees par la mediane ({median_fare})")
    
    # Suppression de la colonne 'deck' (trop de valeurs manquantes)
    if 'deck' in df.columns:
        missing_pct = df['deck'].isnull().mean() * 100
        df = df.drop(columns=['deck'])
        logger.info(f"Colonne 'deck' supprimee ({missing_pct:.1f}% de valeurs manquantes)")
    
    # Conversion de 'age' en numerique
    if 'age' in df.columns:
        df['age'] = pd.to_numeric(df['age'], errors='coerce').round(1)
    
    rows_removed = initial_rows - len(df)
    if rows_removed > 0:
        logger.info(f"{rows_removed} lignes en double supprimees")
    
    return df.reset_index(drop=True)


def get_age_bins(df: pd.DataFrame) -> list:
    """
    Retourne les tranches d'age pour le filtrage.
    
    Returns:
        list: Liste de chaines representant les tranches d'age.
    """
    bins = [0, 12, 18, 35, 60, 100]
    labels = ['0-12 (Enfant)', '13-18 (Adolescent)', '19-35 (Jeune adulte)',
              '36-60 (Adulte)', '61+ (Senior)']
    return labels
