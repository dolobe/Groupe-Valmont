from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.neighbors import KNeighborsClassifier
# TACHE 5 : PREDICTION DES ANNULATIONS (Q5) ET OVERBOOKING (Q6)
cols_knn = ["delai_reservation_j", "nb_personnes", "nb_nuits", "prix_nuit_eur",
            "nuitees_cumulees_client", "weekend_num"]
X_ann, y_ann = df[cols_knn], df["annule_num"]
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
meilleur_k, meilleur_score = 1, 0
for k in [3, 5, 7, 11, 15, 21, 31]:
    pipe = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
    score = cross_val_score(pipe, X_ann, y_ann, cv=cv).mean()
    if score > meilleur_score:
        meilleur_score, meilleur_k = score, k
modele_knn = make_pipeline(StandardScaler(), 
KNeighborsClassifier(n_neighbors=meilleur_k)).fit(X_ann, y_ann)
hotels = df[["hotel_id", "ville", "categorie", "chambres"]].drop_duplicates().copy()
hotels["overbooking_max"] = (hotels["chambres"] * 0.08).astype(int)
print(hotels.head(5))