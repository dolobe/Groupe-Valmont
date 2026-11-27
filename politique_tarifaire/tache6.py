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

# Question E : gain estimé de la politique d'annulation
# Pertes sur les réservations faites plus de 30 jours avant
perte_30j = df[df["annule"] & (df["delai_reservation_j"] > 30)]["montant"].sum()
print("Perte sur les réservations à plus de 30 jours :", round(perte_30j), "€")

# Hypothèses : part de cette perte récupérée grâce au tarif non remboursable
for nom, part in [("prudent", 0.2), ("moyen", 0.35), ("optimiste", 0.5)]:
    print(nom, ":", round(perte_30j * part), "€ récupérés")

    # Question F : coût de la remise de 10 % et gain net
# Réservations à plus de 30 jours qui n'ont PAS été annulées
# (elles auraient payé quand même, donc la remise est une perte pour l'hôtel)
ca_30j_honore = df[~df["annule"] & (df["delai_reservation_j"] > 30)]["montant"].sum()
remise = 0.10

for nom, part in [("prudent", 0.2), ("moyen", 0.35), ("optimiste", 0.5)]:
    # Hypothèse : la même part de clients choisit le tarif non remboursable
    cout_remise = ca_30j_honore * part * remise
    gain_net = perte_30j * part - cout_remise
    print(nom, ": gain net =", round(gain_net), "€ (coût de la remise :", round(cout_remise), "€)")

    # Question G : portrait de chaque type de séjour (segments de la tâche 3, djene)
seg = pd.read_csv("segmentation_clients/Valmont_with_clusters.csv")
seg["annule"] = seg["a_annule"] == "oui"
seg["montant"] = seg["nb_nuits"] * seg["prix_nuit_eur"]
seg["plus_30j"] = seg["delai_reservation_j"] > 30

portrait = seg.groupby("nom_segment").agg(
    reservations=("annule", "size"),
    taux_annulation=("annule", "mean"),
    prix_median=("prix_nuit_eur", "median"),
    part_plus_30j=("plus_30j", "mean"),
)
portrait["perte_eur"] = seg[seg["annule"]].groupby("nom_segment")["montant"].sum().round()
print(portrait.round(2).sort_values("perte_eur", ascending=False))

# Question H : gain net par type de séjour (scénario moyen)
# On durcit les conditions seulement pour les types à risque ;
# Voyageurs Économiques et Clients Fidèles gardent l'annulation gratuite
types_concernes = ["Planificateurs Anticipés", "Clientèle Premium",
                   "Groupes & Séminaires", "Longs Séjours"]
part = 0.35     # hypothèse du scénario moyen
remise = 0.10   # remise du tarif non remboursable

resultats = []
for nom in seg["nom_segment"].unique():
    s = seg[(seg["nom_segment"] == nom) & seg["plus_30j"]]
    if nom in types_concernes:
        recupere = s[s["annule"]]["montant"].sum() * part
        cout = s[~s["annule"]]["montant"].sum() * part * remise
    else:
        recupere, cout = 0, 0
    resultats.append([nom, round(recupere), round(cout), round(recupere - cout)])

gains = pd.DataFrame(resultats, columns=["type", "recupere", "cout_remise", "gain_net"])
print(gains.sort_values("gain_net", ascending=False))
print("Gain net total :", gains["gain_net"].sum(), "€")