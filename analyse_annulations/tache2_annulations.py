"""
TÂCHE 2 : analyse des annulations et des délais (Q1 et Q2)

Q1: qu'est-ce qui distingue une réservation annulée d'une réservation honorée?
Q2: un client qui réserve tôt est-il un client sûr?

Entrée: Valmont_cleaned.csv (sortie de la tâche 1), dans le même dossier.
Sorties: résultats dans le terminal + graph1_canal_segment.png + graph2_delai.png
Lancer: python tache2_annulations.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # on enregistre les images sans les afficher
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

DOSSIER = Path(__file__).resolve().parent
df = pd.read_csv(DOSSIER / "Valmont_cleaned.csv")
df["y"] = (df["a_annule"] == "oui").astype(int)  # 1 = annulée, 0 = honorée
taux_global = df.y.mean()
print(f"Taux global d'annulation : {taux_global:.1%} (n = {len(df)})")

# ---------------------------------------------------------------------
# Q1) Variables qualitatives: khi-deux d'indépendance avec l'annulation
# (p < 0,05 = lien significatif)
# ---------------------------------------------------------------------
print("\n--- Variables qualitatives (khi-deux) ---")
for c in ["canal", "segment_declare", "weekend", "petit_dejeuner", "categorie", "mois_sejour"]:
    p = stats.chi2_contingency(pd.crosstab(df[c], df.y))[1]
    print(f"{c:16s} p = {p:.3f}")
print("\nTaux d'annulation par canal :\n", df.groupby("canal").y.mean().round(3))
print("\nTaux d'annulation par segment :\n", df.groupby("segment_declare").y.mean().round(3))

# ---------------------------------------------------------------------
# Q1) Variables quantitatives: Mann-Whitney (annulées vs honorées)
# Test non paramétrique, car délai et prix sont très asymétriques.
# ---------------------------------------------------------------------
print("\n--- Variables quantitatives (Mann-Whitney) ---")
for c in ["delai_reservation_j", "prix_nuit_eur", "nb_personnes", "nuitees_cumulees_client"]:
    annulees, honorees = df[df.y == 1][c], df[df.y == 0][c]
    p = stats.mannwhitneyu(annulees, honorees).pvalue
    print(f"{c:25s} médiane annulées = {annulees.median():6.1f}   honorées = {honorees.median():6.1f}   p = {p:.2g}")

# ---------------------------------------------------------------------
# Q1) Loisir ou plateformes ? Régression logistique
# Le loisir annule plus, mais réserve aussi beaucoup plus tôt. La régression
# sépare l'effet du segment de l'effet du délai ("toutes choses égales par ailleurs").
# odds_ratio > 1 : augmente le risque d'annulation et < 1 : le diminue.
# ---------------------------------------------------------------------
print("\nDélai médian par segment :\n", df.groupby("segment_declare").delai_reservation_j.median())

X = pd.get_dummies(df[["canal", "segment_declare"]]).drop(columns=["canal_direct", "segment_declare_loisir"])
X.insert(0, "delai_10j", df.delai_reservation_j / 10)  # effet d'une tranche de 10 jours
X = X.astype(float)

modele = LogisticRegression(C=1e9, max_iter=5000).fit(X, df.y)  # C grand = sans régularisation

# p-values (test de Wald), car sklearn ne les fournit pas
Xc = np.column_stack([np.ones(len(X)), X])
coef = np.r_[modele.intercept_, modele.coef_[0]]
proba = 1 / (1 + np.exp(-Xc @ coef))
ecart_type = np.sqrt(np.diag(np.linalg.inv(Xc.T @ (Xc * (proba * (1 - proba))[:, None]))))
resultat = pd.DataFrame({"odds_ratio": np.exp(coef), "p_value": 2 * stats.norm.sf(abs(coef / ecart_type))},
                        index=["constante"] + list(X.columns)).round(4)
print("\nRégression logistique (références : canal direct, segment loisir) :\n", resultat)
print("AUC du modèle :", round(roc_auc_score(df.y, proba), 3))

# ---------------------------------------------------------------------
# Q2) Délai de réservation et annulation
# ---------------------------------------------------------------------
tranches = pd.cut(df.delai_reservation_j, [-1, 7, 14, 30, 60, 90, 400],
                  labels=["0-7 j", "8-14 j", "15-30 j", "31-60 j", "61-90 j", ">90 j"])
par_delai = df.groupby(tranches, observed=True).y.agg(taux="mean", effectif="count")
print("\nTaux d'annulation par tranche de délai :\n", par_delai.round(3))

rho, p = stats.spearmanr(df.delai_reservation_j, df.y)  # lien monotone, sans supposer qu'il est linéaire
print(f"Spearman délai/annulation : rho = {rho:.2f}, p = {p:.2g}")

# ---------------------------------------------------------------------
# Graphiques (ligne rouge = taux moyen)
# ---------------------------------------------------------------------
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})


def barres(ax, etiquettes, valeurs, couleurs="#4C72B0", textes=None):
    ax.bar(etiquettes, valeurs, color=couleurs)
    ax.axhline(taux_global * 100, color="red", ls="--", lw=1)
    for i, v in enumerate(valeurs):
        ax.text(i, v + 0.8, textes[i] if textes else f"{v:.0f} %", ha="center", fontsize=9)


# Graphique 1: canal et segment
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for ax, col, titre in zip(axes, ["canal", "segment_declare"], ["Par canal de vente", "Par segment déclaré"]):
    s = df.groupby(col).y.mean().sort_values() * 100
    barres(ax, s.index, s.values)
    ax.set_title(titre)
axes[0].set_ylabel("Taux d'annulation (%)")
plt.tight_layout()
plt.savefig(DOSSIER / "graph1_canal_segment.png", dpi=150)
plt.close()

# Graphique 2: délai de réservation
fig, ax = plt.subplots(figsize=(7.5, 4.2))
v = par_delai.taux.values * 100
barres(ax, par_delai.index.astype(str), v, ["#4C72B0"] * 2 + ["#DD8452"] * 2 + ["#C44E52"] * 2,
       [f"{x:.0f} %\n(n={n})" for x, n in zip(v, par_delai.effectif)])
ax.set_ylim(0, 60)
ax.set_xlabel("Délai entre réservation et séjour")
ax.set_ylabel("Taux d'annulation (%)")
ax.set_title("Plus on réserve tôt, plus on annule")
plt.tight_layout()
plt.savefig(DOSSIER / "graph2_delai.png", dpi=150)
plt.close()
print("\nGraphiques enregistrés.")