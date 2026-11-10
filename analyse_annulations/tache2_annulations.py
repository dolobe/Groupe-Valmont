
# TÂCHE 2:  Analyse des annulations et des délais (Q1 et Q2)
# Entrée: Valmont_cleaned.csv (produit par la Tâche 1)

import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import roc_auc_score

df = pd.read_csv("Valmont_cleaned.csv")
df["y"] = (df["a_annule"] == "oui").astype(int)          # 1 = annulée
print("Taux global d'annulation :", round(df.y.mean(), 3), "| n =", len(df))


# ÉTAPE 1 (Q1)  Variables qualitatives: taux d'annulation + le test du khi-deux
# Car on compare une variable catégorielle (canal, segment...) à une
# variable binaire (annulée oui/non) et c'est donc le test d'indépendance du khi-deux.
# V de Cramér = intensité du lien (0 = aucun, 1 = parfait).

resultats_q = []
for c in ["canal", "segment_declare", "weekend", "petit_dejeuner", "categorie", "mois_sejour", "nb_nuits"]:
    ct = pd.crosstab(df[c], df.y)
    chi, p, _, _ = stats.chi2_contingency(ct)
    v = np.sqrt(chi / (len(df) * (min(ct.shape) - 1)))
    resultats_q.append((c, round(chi, 1), round(p, 4), round(v, 2)))
    print(f"\n{c}: khi2={chi:.1f}  p={p:.4f}  V={v:.2f}")
    print(df.groupby(c).y.agg(taux="mean", effectif="count").round(3).T)
print(pd.DataFrame(resultats_q, columns=["variable", "khi2", "p", "V_Cramer"]))

# ÉTAPE 2 (Q1): Variables quantitatives (annulées vs honorées)
# on utilise le test deMann-Whitney car distributions asymétriques (délai, prix), on évite
# l'hypothèse de normalité du test t.
print("\n--- Variables quantitatives ---")
for c in ["delai_reservation_j", "prix_nuit_eur", "nb_personnes",
          "nuitees_cumulees_client", "chambres", "distance_gare_km"]:
    a, b = df[df.y == 1][c], df[df.y == 0][c]
    p = stats.mannwhitneyu(a, b).pvalue
    print(f"{c:25s} médiane annulées={a.median():6.1f}  honorées={b.median():6.1f}  p={p:.2g}")


# ÉTAPE 3 (Q1): Plateformes vs loisir (le piège du facteur de confusion)
# Le délai est-il lié au segment ? (loisir/groupe réservent bien plus tôt)
print("\nDélai médian par segment :\n", df.groupby("segment_declare").delai_reservation_j.median())

# Régression logistique multivariée: effet de chaque variable "toutes choses égales"
X = pd.DataFrame({
    "delai_10j": df.delai_reservation_j / 10,
    "nb_pers": df.nb_personnes, "prix_10eur": df.prix_nuit_eur / 10,
    "nb_nuits": df.nb_nuits, "weekend": (df.weekend == "oui") * 1,
    "OTA": (df.canal == "OTA") * 1, "agence": (df.canal == "agence") * 1,
    "entreprise": (df.canal == "entreprise") * 1,      # référence = direct
    "affaires": (df.segment_declare == "affaires") * 1,
    "groupe": (df.segment_declare == "groupe") * 1,    # référence = loisir
}).astype(float)
lr = LogisticRegression(C=1e9, max_iter=5000).fit(X, df.y)
Xc = np.column_stack([np.ones(len(X)), X.values])
b = np.r_[lr.intercept_, lr.coef_[0]]
pr = 1 / (1 + np.exp(-Xc @ b))
cov = np.linalg.inv(Xc.T @ (Xc * (pr * (1 - pr))[:, None]))
z = b / np.sqrt(np.diag(cov))
res = pd.DataFrame({"odds_ratio": np.exp(b), "p_value": 2 * (1 - stats.norm.cdf(abs(z)))},
                   index=["const"] + list(X.columns)).round(4)
print("\nRégression logistique :\n", res)


# ÉTAPE 4 (Q2): Délai de réservation et annulation
tr = pd.cut(df.delai_reservation_j, [-1, 7, 14, 30, 60, 90, 400],
            labels=["0-7 j", "8-14 j", "15-30 j", "31-60 j", "61-90 j", ">90 j"])
tab = df.groupby(tr, observed=True).y.agg(taux="mean", effectif="count")
print("\nTaux d'annulation par tranche de délai :\n", tab.round(3))
rho = stats.spearmanr(df.delai_reservation_j, df.y)
print("Spearman délai/annulation : rho=%.2f p=%.2g" % (rho.statistic, rho.pvalue))

# Arbre de décision, on cherche automatiquement les seuils de délai
Xt = pd.get_dummies(df[["delai_reservation_j", "nb_personnes", "prix_nuit_eur", "nb_nuits", "canal",
                        "segment_declare", "weekend", "petit_dejeuner", "nuitees_cumulees_client"]])
arbre = DecisionTreeClassifier(max_depth=3, min_samples_leaf=40, random_state=0).fit(Xt, df.y)
print(export_text(arbre, feature_names=list(Xt.columns)))
print("AUC arbre :", round(roc_auc_score(df.y, arbre.predict_proba(Xt)[:, 1]), 3))

# ---------------------------------------------------------------------
# GRAPHIQUES
# ---------------------------------------------------------------------
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
glob = df.y.mean() * 100

# Graphique 1 canal / segment (le "match" revenue manager vs directeurs)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for a, c, t in zip(ax, ["canal", "segment_declare"], ["Par canal de vente", "Par segment déclaré"]):
    s = df.groupby(c).y.mean().sort_values() * 100
    a.bar(s.index, s.values, color="#4C72B0"); a.axhline(glob, color="red", ls="--", lw=1)
    for i, v in enumerate(s.values): a.text(i, v + .6, f"{v:.0f} %", ha="center")
    a.set_title(t)
ax[0].set_ylabel("Taux d'annulation (%)"); ax[1].text(2.45, glob + .6, "moyenne", color="red", ha="right", fontsize=9)
plt.tight_layout(); plt.savefig("graph1_canal_segment.png", dpi=150); plt.close()
# Graphique 2 (délai)
fig, ax = plt.subplots(figsize=(7.5, 4.2))
v = tab.taux.values * 100
ax.bar(tab.index.astype(str), v, color=["#4C72B0"] * 2 + ["#DD8452"] * 2 + ["#C44E52"] * 2)
ax.axhline(glob, color="red", ls="--", lw=1)
for i, (x, n) in enumerate(zip(v, tab.effectif)): ax.text(i, x + .8, f"{x:.0f} %\n(n={n})", ha="center", fontsize=9)
ax.set_ylim(0, 60); ax.set_xlabel("Délai entre réservation et séjour"); ax.set_ylabel("Taux d'annulation (%)")
ax.set_title("Plus on réserve tôt, plus on annule")
plt.tight_layout(); plt.savefig("graph2_delai.png", dpi=150); plt.close()
print("\nGraphiques enregistrés.")