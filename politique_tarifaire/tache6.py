import pandas as pd

# Chargement des données nettoyées par la tâche 1
df = pd.read_csv("nettoyage_des_donnees/Valmont_cleaned.csv")

print(df.shape)
print(df.columns)

# Question A : le petit-déjeuner fait-il monter le prix ?
# On compare à catégorie égale, car un 5 étoiles est toujours plus cher qu'un 3 étoiles
prix = df.groupby(["categorie", "petit_dejeuner"])["prix_nuit_eur"].median()
print(prix.unstack())


# Question B : le petit-déjeuner change-t-il le taux d'annulation ?
taux = df.groupby("petit_dejeuner")["a_annule"].apply(lambda x: (x == "oui").mean())
print(taux)

# Question C : combien d'argent perd-on à cause des annulations ?
annulees = df[df["a_annule"] == "oui"]
perte = (annulees["nb_nuits"] * annulees["prix_nuit_eur"]).sum()
print("Nombre d'annulations :", len(annulees))
print("Chiffre d'affaires perdu :", round(perte), "€")

# Question D : les pertes selon le délai de réservation
# On découpe le délai en tranches pour voir où on perd le plus
tranches = [0, 14, 30, 90, 1000]
noms = ["0-14 j", "15-30 j", "31-90 j", "plus de 90 j"]
df["tranche_delai"] = pd.cut(df["delai_reservation_j"], bins=tranches, labels=noms, include_lowest=True)

df["montant"] = df["nb_nuits"] * df["prix_nuit_eur"]
df["annule"] = df["a_annule"] == "oui"

resume = df.groupby("tranche_delai", observed=True).agg(
    reservations=("annule", "size"),
    taux_annulation=("annule", "mean"),
)
resume["perte_eur"] = df[df["annule"]].groupby("tranche_delai", observed=True)["montant"].sum().round()
print(resume)