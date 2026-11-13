# Groupe-Valmont

### Tache:


##Tâche 1 : Nettoyage des fichiers, gestion des valeurs bizarres et Q9 (les réservations anormales à bloquer)

Cette tâche consiste à nettoyer et préparer les données de réservation et les informations hôtelières du projet Valmont afin de disposer d'un jeu de données fiable pour les prochaines étapes du projet.

Le traitement est réalisé en Python avec la bibliothèque Pandas.

## 1. Explication du code de nettoyage (`GroupeValmont.py`)

Le script réalise un pipeline complet de préparation des données en plusieurs étapes clés :

* **Fusion des tables :** Les fichiers `Valmont_reservations.csv` (940 lignes) et `Valmont_hotels.csv` (32 lignes) sont fusionnés via la clé commune `hotel_id`.
* **Suppression des doublons :** 140 lignes dupliquées (basées sur `reservation_id`) sont supprimées, ramenant le jeu de données à 800 lignes.
* **Imputation des valeurs manquantes :** 
  * Pour la colonne numérique `nb_personnes` (20 valeurs manquantes), les trous sont comblés par la **médiane**.
  * Pour la colonne qualitative `petit_dejeuner` (20 valeurs manquantes), les trous sont comblés par le **mode** (valeur la plus fréquente).
* **Traitement des anomalies (Q9) et filtrage final :** Les réservations aberrantes sont identifiées, comptabilisées, puis écartées (**6 dossiers supprimés**).
* **Exportation :** Le fichier final propre et validé est enregistré sous le nom de **`Valmont_cleaned.csv`** (contenant exactement **794 lignes**).


## 2. Réponse à la Question 9

### A. Faut-il les bloquer avant confirmation ?
**Oui, de manière impérative.** Il faut mettre en place des filtres automatiques sur le système de réservation en amont pour empêcher la validation de tarifs nuls/négatifs ou de séjours supérieurs à 30 nuits, évitant ainsi les erreurs de planning et les pertes financières.

### B. Nombre de dossiers anormaux par mois
Le script a identifié un total de **6 dossiers anormaux**, dont la répartition mensuelle affichée dans le terminal est la suivante :
* **Mois 1 :** 1 dossier
* **Mois 2 :** 1 dossier
* **Mois 3 :** 2 dossiers
* **Mois 5 :** 1 dossier
* **Mois 6 :** 1 dossier

*(Aucune anomalie sur les autres mois).* Cela montre qu'il s'agit d'erreurs humaines de saisie ponctuelles et non d'un problème saisonnier.









Tâche 2 : Analyse des annulations et des délais (Q1 et Q2)

Tâche 3 : Segmentation des clients pour remplacer l'ancien système (Q7 et une partie de la Q8)

Tâche 4 : Modèle de prix et test de robustesse en haute saison (Q3 et Q4)

Tâche 5 : Prédiction des annulations et calcul de l'overbooking (Q5 et Q6)

Tâche 6 : Politique tarifaire, services inclus et chiffrage des gains sur les chambres vides (fin de la Q8)
