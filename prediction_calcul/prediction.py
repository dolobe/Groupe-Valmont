# Tache 5: 

import os
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import binom 
from sklearn.linear_model import Logistic_regression
from sklearn.metrics import roc_auc_score
from sklearn.tree import DecisionTreeClassifier, export_text    

os.makedirs("./images", exist_ok=True)

# 1. Charger les données nettoyées
df = pd.read_csv("./data/Valmont_cleaned.csv")
df["y"] = (df["a_annule"] == "oui").astype(int)  # 1 = annulée, 0 = honorée

### Q5
variables = [
    "delai_reservation_j",
    "nb_personnes",
    "nb_nuits",
    "prix_nuit_eur",
    "nuitees_cumulees_client",
    "segment_declare",
    "canal",
    "weekend",
    "categorie",
]
X = pd.get_dummies(df[variables], drop_first=True)
y = df["y"]

# Régression logistique
modele_log = LogisticRegression(max_iter=1000).fit(X, y)
proba_log = modele_log.predict_proba(X)[:, 1]
print("AUC Régression logistique :", round(roc_auc_score(y, proba_log), 3))

# Arbre de décision
arbre = DecisionTreeClassifier(max_depth=3, min_samples_leaf=30, random_state=42).fit(X, y)
proba_arbre = arbre.predict_proba(X)[:, 1]
print("AUC Arbre de décision     :", round(roc_auc_score(y, proba_arbre), 3))
print("\nRègles de l'arbre :")
print(export_text(arbre, feature_names=list(X.columns)))

### Q6:
taux_annul = df["y"].mean()
taux_venue = 1 - taux_annul
print(f"\nTaux d'annulation moyen : {taux_annul:.1%} | Taux de venue : {taux_venue:.1%}")

hotels = df[["hotel_id", "ville", "chambres"]].drop_duplicates().sort_values("chambres")

marge_1pct = []
for cap in hotels["chambres"]:
    k_ok = 0
    for k in range(1, int(cap * 0.6) + 1):
        risque_refus = binom.sf(cap, cap + k, taux_venue)
        if risque_refus <= 0.01:
            k_ok = k
    marge_1pct.append(k_ok)

hotels["surresa_max_1pct"] = marge_1pct
print("\nSurréservation max par hôtel (risque refus client <= 1%) :")
print(hotels.to_string(index=False))

# Graphique sur les 8 premiers hôtels
top8 = hotels.head(8)
plt.figure(figsize=(8, 4))
plt.bar(top8["hotel_id"], top8["surresa_max_1pct"])
plt.xlabel("Hôtel")
plt.ylabel("Chambres en trop max (+k)")
plt.title("Surréservation autorisée (risque de refus <= 1%)")
plt.tight_layout()
plt.savefig("./images/graph5_surreservation.png", dpi=150)
plt.close()
print("\nGraphique enregistré dans ./images/graph5_surreservation.png")