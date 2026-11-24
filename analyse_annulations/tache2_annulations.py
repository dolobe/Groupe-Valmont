"""
TÂCHE 2: Analyse des annulations et des délais (Q1 et Q2)

Objectif
    Q1: qu'est-ce qui distingue une réservation annulée d'une réservation honorée ?
         (le revenue manager accuse les plateformes, les directeurs accusent le loisir)
    Q2: un client qui réserve tôt est-il un client sûr ?

Entrée
    Valmont_cleaned.csv: fichier nettoyé produit par la Tâche 1 (794 réservations),
    placé dans le même dossier que ce script.

Sorties
    - Résultats statistiques affichés dans le terminal
    - graph1_canal_segment.png  (taux d'annulation par canal et par segment)
    - graph2_delai.png         (taux d'annulation selon le délai de réservation)

Utilisation
    python tache2_annulations.py
"""

from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")                 # pas d'affichage à l'écran car on enregistre juste les images
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import roc_auc_score

# Dossier du script: le code fonctionne même s'il est lancé depuis un autre dossier
DOSSIER = Path(__file__).resolve().parent


# ---------------------------------------------------------------------
# CHARGEMENT DES DONNÉES
# ---------------------------------------------------------------------
df = pd.read_csv(DOSSIER / "Valmont_cleaned.csv")
df["y"] = (df["a_annule"] == "oui").astype(int)          # variable cible: 1 = annulée, 0 = honorée
print("Taux global d'annulation :", round(df.y.mean(), 3), "| n =", len(df))


# ---------------------------------------------------------------------
# ÉTAPE 1 (Q1): variables qualitatives -> taux d'annulation + test du khi-deux
# ---------------------------------------------------------------------
# On compare une variable catégorielle (canal, segment...) à une variable binaire
# (annulée oui/non): le test adapté est le test d'indépendance du khi-deux.
#   - p < 0,05  -> il existe un lien statistiquement significatif avec l'annulation
#   - V de Cramér = intensité du lien (0 = aucun, 1 = parfait)

resultats_q = []
for c in ["canal", "segment_declare", "weekend", "petit_dejeuner", "categorie", "mois_sejour", "nb_nuits"]:
    ct = pd.crosstab(df[c], df.y)                         # tableau croisé variable x annulation
    chi, p, _, _ = stats.chi2_contingency(ct)
    v = np.sqrt(chi / (len(df) * (min(ct.shape) - 1)))    # V de Cramér
    resultats_q.append((c, round(chi, 1), round(p, 4), round(v, 2)))
    print(f"\n{c}: khi2={chi:.1f}  p={p:.4f}  V={v:.2f}")
    print(df.groupby(c).y.agg(taux="mean", effectif="count").round(3).T)
print(pd.DataFrame(resultats_q, columns=["variable", "khi2", "p", "V_Cramer"]))


# ---------------------------------------------------------------------
# ÉTAPE 2 (Q1): variables quantitatives -> annulées vs honorées
# ---------------------------------------------------------------------
# Test de Mann-Whitney: les distributions (délai, prix) sont très asymétriques,
# on évite donc le test t qui suppose une distribution normale.
print("\n--- Variables quantitatives ---")
for c in ["delai_reservation_j", "prix_nuit_eur", "nb_personnes",
          "nuitees_cumulees_client", "chambres", "distance_gare_km"]:
    a, b = df[df.y == 1][c], df[df.y == 0][c]             # a = annulées, b = honorées
    p = stats.mannwhitneyu(a, b).pvalue
    print(f"{c:25s} médiane annulées={a.median():6.1f}  honorées={b.median():6.1f}  p={p:.2g}")


# ---------------------------------------------------------------------
# ÉTAPE 3 (Q1): plateformes vs loisir -> le piège du facteur de confusion
# ---------------------------------------------------------------------
# Le segment loisir annule plus, mais il réserve aussi beaucoup plus tôt.
# Est-ce le segment ou le délai qui joue ? On regarde d'abord le délai par segment
print("\nDélai médian par segment :\n", df.groupby("segment_declare").delai_reservation_j.median())

# Puis on fait une régression logistique multivariée qui mesure l'effet de
# chaque variable "toutes choses égales par ailleurs".
# Lecture: odds_ratio > 1 = augmente le risque d'annulation, < 1 = le diminue.
X = pd.DataFrame({
    "delai_10j": df.delai_reservation_j / 10,              # effet d'une tranche de 10 jours de délai
    "nb_pers": df.nb_personnes, "prix_10eur": df.prix_nuit_eur / 10,
    "nb_nuits": df.nb_nuits, "weekend": (df.weekend == "oui") * 1,
    "OTA": (df.canal == "OTA") * 1, "agence": (df.canal == "agence") * 1,
    "entreprise": (df.canal == "entreprise") * 1,          # référence = direct
    "affaires": (df.segment_declare == "affaires") * 1,
    "groupe": (df.segment_declare == "groupe") * 1,        # référence = loisir
}).astype(float)

# C très grand = quasiment aucune régularisation (régression logistique "classique")
lr = LogisticRegression(C=1e9, max_iter=5000).fit(X, df.y)

# sklearn ne fournit pas les p-values, on les calcule à la main (test de Wald).
Xc = np.column_stack([np.ones(len(X)), X.values])          # ajout de la constante
b = np.r_[lr.intercept_, lr.coef_[0]]                      # coefficients
pr = 1 / (1 + np.exp(-Xc @ b))                             # probabilités prédites
cov = np.linalg.inv(Xc.T @ (Xc * (pr * (1 - pr))[:, None]))  # matrice de covariance des coefficients
z = b / np.sqrt(np.diag(cov))                              # statistique de Wald
res = pd.DataFrame({"odds_ratio": np.exp(b), "p_value": 2 * (1 - stats.norm.cdf(abs(z)))},
                   index=["const"] + list(X.columns)).round(4)
print("\nRégression logistique :\n", res)


# ---------------------------------------------------------------------
# ÉTAPE 4 (Q2) : délai de réservation et annulation
# ---------------------------------------------------------------------
# Découpage du délai en tranches pour lire le taux d'annulation tranche par tranche
tr = pd.cut(df.delai_reservation_j, [-1, 7, 14, 30, 60, 90, 400],
            labels=["0-7 j", "8-14 j", "15-30 j", "31-60 j", "61-90 j", ">90 j"])
tab = df.groupby(tr, observed=True).y.agg(taux="mean", effectif="count")
print("\nTaux d'annulation par tranche de délai :\n", tab.round(3))

# Corrélation de Spearman: lien délai/annulation sans supposer qu'il est linéaire
rho = stats.spearmanr(df.delai_reservation_j, df.y)
print("Spearman délai/annulation : rho=%.2f p=%.2g" % (rho.statistic, rho.pvalue))

# Arbre de décision: cherche automatiquement les seuils de délai utilisables en pratique
# (profondeur limitée à 3 et 40 réservations minimum par feuille pour rester lisible)
Xt = pd.get_dummies(df[["delai_reservation_j", "nb_personnes", "prix_nuit_eur", "nb_nuits", "canal",
                        "segment_declare", "weekend", "petit_dejeuner", "nuitees_cumulees_client"]])
arbre = DecisionTreeClassifier(max_depth=3, min_samples_leaf=40, random_state=0).fit(Xt, df.y)
print(export_text(arbre, feature_names=list(Xt.columns)))
# AUC: 0,5 = hasard, 1 = prédiction parfaite
print("AUC arbre :", round(roc_auc_score(df.y, arbre.predict_proba(Xt)[:, 1]), 3))


# ---------------------------------------------------------------------
# GRAPHIQUES
# ---------------------------------------------------------------------
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
glob = df.y.mean() * 100                                   # taux moyen, tracé en pointillés rouges

# Graphique 1 : canal / segment (le "match" revenue manager vs directeurs)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for a, c, t in zip(ax, ["canal", "segment_declare"], ["Par canal de vente", "Par segment déclaré"]):
    s = df.groupby(c).y.mean().sort_values() * 100
    a.bar(s.index, s.values, color="#4C72B0"); a.axhline(glob, color="red", ls="--", lw=1)
    for i, v in enumerate(s.values): a.text(i, v + .6, f"{v:.0f} %", ha="center")
    a.set_title(t)
ax[0].set_ylabel("Taux d'annulation (%)"); ax[1].text(2.45, glob + .6, "moyenne", color="red", ha="right", fontsize=9)
plt.tight_layout(); plt.savefig(DOSSIER / "graph1_canal_segment.png", dpi=150); plt.close()

# Graphique 2: délai de réservation (bleu = peu risqué, orange = moyen, rouge = très risqué)
fig, ax = plt.subplots(figsize=(7.5, 4.2))
v = tab.taux.values * 100
ax.bar(tab.index.astype(str), v, color=["#4C72B0"] * 2 + ["#DD8452"] * 2 + ["#C44E52"] * 2)
ax.axhline(glob, color="red", ls="--", lw=1)
for i, (x, n) in enumerate(zip(v, tab.effectif)): ax.text(i, x + .8, f"{x:.0f} %\n(n={n})", ha="center", fontsize=9)
ax.set_ylim(0, 60); ax.set_xlabel("Délai entre réservation et séjour"); ax.set_ylabel("Taux d'annulation (%)")
ax.set_title("Plus on réserve tôt, plus on annule")
plt.tight_layout(); plt.savefig(DOSSIER / "graph2_delai.png", dpi=150); plt.close()
print("\nGraphiques enregistrés.")
