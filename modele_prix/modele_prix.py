import pandas as pd
import numpy as np

# Chargement du fichier Valmont_cleaned.csv et la table des hotels
df_clean = pd.read_csv("./data/Valmont_cleaned.csv")
df_hot = pd.read_csv("./data/Valmont_hotels.csv")

print(f"Lignes chargées depuis Valmont_cleaned.csv : {len(df_clean)}")
print("Colonnes disponibles :", df_clean.columns.tolist())

#Jointure avec Valmont_hotels.csv
if "categorie" not in df_clean.columns:
    df = pd.merge(df_clean, df_hot, on="hotel_id", how="left")
else:
    df = df_clean.copy()

print(f"Hôtels non reconnus après jointure : {df['ville'].isna().sum()}")

# Verification d'abscence de doublons, des prix a 0eur, et des sejours aberrants
df = df.drop_duplicates()
df = df[(df["prix_nuit_eur"] > 0) & (df["nb_nuits"] < 365)].copy()

# Gestion des valeurs manquantes restantes.
if df["nb_personnes"].isna().sum() > 0:
    df["nb_personnes"] = df["nb_personnes"].fillna(
        df.groupby("segment_declare")["nb_personnes"].transform("median")
    )
if df["petit_dejeuner"].isna().sum() > 0:
    df["petit_dejeuner"] = df["petit_dejeuner"].fillna("non")

print(f"Réservations valides retenues pour le modèle de prix : {len(df)}")

# Affichage de l'indicateur de haute saison
df["haute_saison"] = df["mois_sejour"].isin([6, 7, 8, 12]).astype(int)

#Analyse exploratoire des tarifs par categorie et par mois
print("\n--- Résumé statistique des variables clés ---")
print(df[["prix_nuit_eur", "nb_nuits", "delai_reservation_j", "distance_gare_km"]].describe().round(2))

print("\n--- Prix moyen par catégorie d'hôtel ---")
print(df.groupby("categorie")["prix_nuit_eur"].agg(["count", "mean", "median", "std"]).round(2))

print("\n--- Prix moyen par mois de séjour ---")
print(df.groupby("mois_sejour")["prix_nuit_eur"].agg(["count", "mean", "median"]).round(2))


