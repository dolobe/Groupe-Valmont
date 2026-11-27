import pandas as pd

# Chargement des données nettoyées par la tâche 1
df = pd.read_csv("nettoyage_des_donnees/Valmont_cleaned.csv")

print(df.shape)
print(df.columns)