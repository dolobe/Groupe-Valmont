import pandas as pd

# Chargement des données nettoyées par la tâche 1
df = pd.read_csv("nettoyage_des_donnees/Valmont_cleaned.csv")

print(df.shape)
print(df.columns)
# Question A : le petit-déjeuner fait-il monter le prix ?
# On compare à catégorie égale, car un 5 étoiles est toujours plus cher qu'un 3 étoiles
prix = df.groupby(["categorie", "petit_dejeuner"])["prix_nuit_eur"].median()
print(prix.unstack())

# Question A : le petit-déjeuner fait-il monter le prix ?
# On compare à catégorie égale, car un 5 étoiles est toujours plus cher qu'un 3 étoiles
prix = df.groupby(["categorie", "petit_dejeuner"])["prix_nuit_eur"].median()
print(prix.unstack())