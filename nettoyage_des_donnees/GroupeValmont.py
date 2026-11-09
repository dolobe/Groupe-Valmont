import pandas as pd

# 1. Charger les fichiers d'origine

reservations = pd.read_csv('Valmont_reservations.csv')
hotels = pd.read_csv('Valmont_hotels.csv')

print("Fichiers chargés !")
print("Nombre de réservations :", len(reservations))
print("Nombre d'hôtels :", len(hotels))


# 2. Fusionner les deux tables

df = pd.merge(reservations, hotels, on='hotel_id', how='left')

print("Les deux fichiers ont été fusionnés.")
print("Nombre de lignes après la fusion :", len(df))


# 3. Supprimer les doublons

print("Nombre de doublons trouvés :", df.duplicated(subset=['reservation_id']).sum())

df = df.drop_duplicates(subset=['reservation_id'])

print("Doublons supprimés !")
print("Nombre de lignes restantes :", len(df))


# 4. Gérer les valeurs manquantes

print("Valeurs manquantes avant le remplacement :")
print(df[['nb_personnes', 'petit_dejeuner']].isna().sum())

df['nb_personnes'] = df['nb_personnes'].fillna(df['nb_personnes'].median())

df['petit_dejeuner'] = df['petit_dejeuner'].fillna(df['petit_dejeuner'].mode()[0])

print("Valeurs manquantes après le remplacement :")
print(df[['nb_personnes', 'petit_dejeuner']].isna().sum())


# 5. Supprimer les valeurs aberrantes

df_clean = df[(df['prix_nuit_eur'] > 0) & (df['nb_nuits'] <= 30)].copy()

print("Nombre de réservations écartées :", len(df) - len(df_clean))
print("Nombre de réservations gardées :", len(df_clean))


# 6. Convertir les colonnes de comptage en entiers propres

df_clean['nb_personnes'] = df_clean['nb_personnes'].astype(int)

df_clean['delai_reservation_j'] = df_clean['delai_reservation_j'].astype(int)

df_clean['nuitees_cumulees_client'] = df_clean['nuitees_cumulees_client'].astype(int)

print("Conversion des colonnes terminée !")
print(df_clean[['nb_personnes', 'delai_reservation_j', 'nuitees_cumulees_client']].dtypes)


# 7. Sauvegarder le fichier propre

df_clean.to_csv('Valmont_cleaned.csv', index=False)

print("Le fichier propre a bien été enregistré !")
print(f"Nettoyage terminé ! Il reste {len(df_clean)} réservations.")