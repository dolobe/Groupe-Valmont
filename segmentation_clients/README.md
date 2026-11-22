# Segmentation de la Clientèle (K-Means)


## Objectif et Réponse à la Question 7
L'objectif est d'optimiser la gestion opérationnelle et tarifaire du Groupe Valmont en remplaçant les intuitions par une analyse empirique des données de réservation.

**Réponse à la Question 7 :** Notre analyse met en évidence 6 profils comportementaux. Les scores de Silhouette obtenus (autour de 0,28) indiquent que ces clusters représentent des **tendances comportementales plutôt que des blocs étanches**. Cette étude montre que le motif déclaré à la réservation (segment_declare) ne suffit pas à caractériser les comportements réels (par exemple, des clients déclarant voyager sous le motif "affaires" adoptent des comportements très hétérogènes en termes de durée de séjour, d'anticipation ou de gamme d'hôtel).


## Méthodologie et Choix des Algorithmes

1. **Cadre de l'Apprentissage Non Supervisé :**
   * En l'absence de variable cible prédéfinie (pas d'étiquette à prédire), la tâche s'inscrit dans le cadre de l'apprentissage non supervisé.
   * **Pourquoi K-Means plutôt que DBSCAN :** DBSCAN est un algorithme basé sur la densité, particulièrement adapté à la détection de formes complexes et à l'élimination du bruit. Cependant, DBSCAN classe les points isolés en tant que "bruit" (outliers non assignés). Dans un contexte métier de segmentation client, nous souhaitons que chaque réservation reçoive un profil opérationnel exploitable. K-Means est donc plus adapté car il partitionne l'ensemble des données en clusters convexes autour de centroïdes (profils moyens) directement interprétables. (Nous précisons que DBSCAN n'a pas été implémenté dans le notebook pour cette raison).

2. **Sélection et Standardisation des Variables :**
   * Variables retenues : nb_nuits, nb_personnes, delai_reservation_j, prix_nuit_eur, nuitees_cumulees_client.
   * **Imputation et .dropna() :** L'instruction .dropna() est conservée dans le code par précaution méthodologique, mais n'élimine aucune réservation (794 réservations analysées) car les valeurs manquantes ont été imputées lors du nettoyage préalable. Nous notons la limite métier de cette imputation amont (ex. réservations identifiées "groupe" imputées avec 1 seule personne).
   * **Standardisation :** L'utilisation de StandardScaler() est indispensable pour éviter que les variables à forte amplitude (délai de réservation, prix) ne masquent l'effet de variables à plus faible échelle.

3. **Justification de l'arbitrage k = 6 (vs k = 5) :**
   * **Méthode du Coude :** Le gain d'inertie reste très marqué entre k=5 et k=6 (229,64), puis chute à environ 95 dès k=7 (95,22).
   * **Score de Silhouette :** Le score de Silhouette s'élève à 0,278 pour k=5 et s'établit à 0,275 pour k=6.
   * **Justification métier décisive (Taux d'annulation) :** Si k=5 et k=6 isolent tous deux l'hôtellerie 5 étoiles dans un groupe dédié (à 100 %), le passage à k = 6 fait apparaître un segment critique à très haut risque d'annulation : les Planificateurs Anticipés (47,1 % d'annulation). À k=5, le taux d'annulation maximal observé n'était que de 36,3 %. Cette observation dans les données justifie le choix de 6 groupes.

4. **Captation du Segment Déclaré :**
   * Le croisement en colonne montre que le Groupe 2 regroupe **79,3 % de la totalité des réservations déclarées "groupe"** (119 sur 150).
   * En revanche, le Groupe 1 concentre 68,9 % de réservations déclarées "affaires" très courtes, et le Groupe 3 (100 % 5 étoiles) se partage entre affaires (50,7 %) et loisir (45,8 %).


## Synthèse des 6 Segments Clientèle (Question 8)

| Groupe | Nom Commercial | Effectif | Annulation | Week-end | Hôtels 5 Étoiles | Caractéristiques Clés | Action Marketing Recommandée |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **0** | **Longs Séjours** | 137 | 28,5 % | 25,5 % | 5,1 % | Séjours les plus longs (moyenne 5,0 nuits, min 4 nuits, max 9 nuits), tarif d'environ 145 €/nuit. **1er volume hors week-end (516 nuits, annulées incluses)**. | Tarification dégressive à partir de 4 nuits réservées (seuil directement étayé par les données du groupe, dont le minimum est à 4 nuits). |
| **1** | **Voyageurs Économiques** | 238 | 18,5 % | 31,9 % | 0,0 % | Séjours courts (2,2 nuits), réservation rapide (20,7 j.), prix bas (140 €/nuit). 68,9 % déclarés "affaires". | Offres promotionnelles de dernière minute et packages étapes business. |
| **2** | **Groupes & Séminaires** | 119 | 31,9 % | 24,4 % | 29,4 % | Très grands groupes (11,9 personnes en moyenne), **74,0 % de leurs nuitées effectuées hors week-end (annulées incluses)**. Englobe 79,3 % des déclarations "groupe". | Offres professionnelles (salles de réunion, devis sur-mesure). |
| **3** | **Clientèle Premium** | 144 | 22,2 % | 38,2 % | **100,0 %** | Prix nuitée le plus élevé (366 € / nuit). Ce groupe ne contient que des réservations en hôtels 5 étoiles. | Services VIP, accueil sur-mesure et privilèges de surclassement. |
| **4** | **Clients Fidèles** | 71 | 19,7 % | 31,0 % | 18,3 % | Historique de fidélité le plus élevé (29,1 nuits au total). | Programme de fidélisation ciblé et attentions particulières en chambre. |
| **5** | **Planificateurs Anticipés** | 85 | **47,1 %** | 37,6 % | 28,2 % | Réservations très en avance (123,8 j.) avec un **taux d'annulation record (47,1 %)**. | Acomptes obligatoires et tarifs Early Bird non remboursables pour sécuriser le chiffre d'affaires. |


## Observations sur les Services, Canaux et Borne Haute de CA Annulé

* **Canaux de réservation et Petit-Déjeuner :**
  * Le petit-déjeuner présente un écart allant de 35,0 % (Longs Séjours) à 50,4 % (Groupes & Séminaires). Le canal de réservation se répartit également sans rupture majeure d'un cluster à l'autre (OTA entre 37,8 % et 47,4 %).
  * Ces écarts restent modérés, trop faibles pour fonder une politique tarifaire ou marketing différenciée sur ces seuls critères. Nous notons également que 20 valeurs de petit-déjeuner ont été imputées lors du nettoyage.
* **Borne Haute du Chiffre d'Affaires Annulé (Planificateurs) :**
  * Pour le Groupe 5 (Planificateurs Anticipés), nous avons évalué la borne haute du chiffre d'affaires annulé sur l'échantillon avec la formule : nb_nuits * prix_nuit_eur pour les réservations avec a_annule = oui.
  * Ce groupe génère un chiffre d'affaires annulé de **22 599 €**, soit **19,6 % de la totalité du CA annulé dans l'échantillon (115 279 €)**, alors qu'il ne représente que 10,7 % des réservations (85 sur 794). Il s'agit d'une borne haute car elle suppose qu'aucune chambre annulée n'a pu être revendue. La modélisation exacte des opportunités de surréservation et du gain financier net est confiée à Lina (Tâche 6).


## Remplissage des Hôtels "Hors Week-end" (Question 8)

En analysant la variable weekend = non (réservations hors week-end), le résultat varie selon la métrique retenue :

**Base de calcul :** ces chiffres portent sur toutes les réservations du fichier, **annulées incluses**. Une réservation annulée ne remplit pas réellement une chambre : ces valeurs sont donc des bornes hautes.

* **En volume total de nuitées hors week-end :** Le segment **Longs Séjours** (Groupe 0) est le principal moteur avec **516 nuitées** hors week-end (soit environ 32 % du total des nuitées réalisées hors week-end).
* **En part relative au sein du groupe :** Le segment **Groupes & Séminaires** (Groupe 2) réalise **74,0 % de l'ensemble de ses nuitées** hors week-end.

**Recommandation :** pour remplir les hôtels en semaine, nous ciblons en priorité les **Longs Séjours** (Groupe 0). Ils représentent le plus gros volume de nuitées hors week-end (516, soit environ 32 % du total). Point de vigilance : leur taux d'annulation est de 28,5 %, contre 18,5 % pour les Voyageurs Économiques.

**Limite méthodologique :** La donnée nb_nuits mesure la durée de la réservation mais ne compte pas le nombre de chambres occupées. Un groupe de 12 personnes occupant plusieurs chambres est donc sous-représenté si l'on raisonne uniquement en nombre de lignes de réservation.