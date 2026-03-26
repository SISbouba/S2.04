import pandas as pd
from matplotlib import pyplot as plt

# =====================================================================
# 1. CHARGEMENT DES DONNÉES
# =====================================================================
organisation = pd.read_csv("csv/Organisation.csv", header=None)
club = pd.read_csv("csv/Club des Tenracs.csv", header=None)
tenracs = pd.read_csv("csv/Tenracs.csv", header=None)
repas = pd.read_csv("csv/Repas.csv", header=None)
participe = pd.read_csv("csv/Participe.csv", header=None)

# Nouveaux CSV nécessaires pour la requête sur les légumes
contient = pd.read_csv("csv/Contient.csv", header=None)
plat = pd.read_csv("csv/Plat.csv", header=None)
combineip = pd.read_csv("csv/CombineIP.csv", header=None)
ingredient = pd.read_csv("csv/Ingredient.csv", header=None)

# =====================================================================
# 2. RENOMMAGE DES COLONNES
# =====================================================================
tenracs = tenracs.rename(columns={0: "idT", 11: "IDO", 8: "nom_grade"})
organisation = organisation.rename(columns={0: "IDO", 1: "NOM_ORGANISATION"})
club = club.rename(columns={0: "IDO_1"})
repas = repas.rename(columns={0: "idR", 2: "date_repas", 1: "intitule"})
participe = participe.rename(columns={0: "idT", 1: "idR"})

# --- Renommage validé selon le schéma SQL fourni ---
contient = contient.rename(columns={0: "idR", 1: "NOM_PLAT"})
plat = plat.rename(columns={0: "NOM_PLAT"})
combineip = combineip.rename(columns={0: "NOM_PLAT", 1: "IDI"})
ingredient = ingredient.rename(columns={0: "IDI", 2: "EST_LEGUME"}) # EST_LEGUME est la colonne 2

# =====================================================================
# PRÉPARATION FIGURE 1 (2 graphiques)
# =====================================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# --- GRAPHIQUE 1 : Nombre de Tenracs distincts par Organisation ---
df = tenracs.merge(organisation, on="IDO")
df = df.merge(club, left_on="IDO", right_on="IDO_1")
result = df.groupby("IDO_1")["idT"].nunique().reset_index()
result = result.rename(columns={"idT": "NB_TENRACS_DISTINCTS"})

ax1.bar(result["IDO_1"], result["NB_TENRACS_DISTINCTS"], color="#4C72B0", edgecolor="black")
ax1.set_title("Nombre de Tenracs distincts par Organisation", fontsize=14, fontweight="bold")
ax1.set_xlabel("Organisation", fontsize=12)
ax1.set_ylabel("Nombre de Tenracs", fontsize=12)

# --- GRAPHIQUE 2 : Nombre de repas avec légumes par mois (Nouvelle Requête SQL) ---
# SQL Équivalent : select count(distinct INTITULE), TO_CHAR(DATE_REPAS, 'YYYY-MM') ...

# a) Jointures (MERGE) en chaîne
df_legumes = repas.merge(contient, on="idR")
df_legumes = df_legumes.merge(plat, on="NOM_PLAT")
df_legumes = df_legumes.merge(combineip, on="NOM_PLAT")
df_legumes = df_legumes.merge(ingredient, on="IDI")

# b) Clause WHERE : EST_LEGUME = 1
# On s'assure que la comparaison se fait bien avec un entier ou un string selon tes données
df_legumes = df_legumes[df_legumes["EST_LEGUME"].astype(str) == "1"]

# c) TO_CHAR(DATE_REPAS, 'YYYY-MM')
df_legumes["MOIS_ANNEE"] = pd.to_datetime(df_legumes["date_repas"]).dt.strftime('%Y-%m')

# d) GROUP BY + COUNT DISTINCT
result_legumes = df_legumes.groupby("MOIS_ANNEE")["intitule"].nunique().reset_index()
result_legumes = result_legumes.rename(columns={"intitule": "NB_REPAS_LEGUMES"})

# e) ORDER BY TO_CHAR(DATE_REPAS, 'YYYY-MM')
result_legumes = result_legumes.sort_values(by="MOIS_ANNEE")

# Création du graphique (Ligne avec des points pour bien voir la chronologie mensuelle)
ax2.plot(result_legumes["MOIS_ANNEE"], result_legumes["NB_REPAS_LEGUMES"], 
         color="#2CA02C", marker='o', linestyle='-', linewidth=2, markersize=8, zorder=3)

# Ajout d'une grille pour mieux lire les valeurs
ax2.grid(True, linestyle="--", alpha=0.6, zorder=0)

ax2.set_title("Repas distincts contenant des légumes par Mois", fontsize=14, fontweight="bold")
ax2.set_xlabel("Mois (AAAA-MM)", fontsize=12)
ax2.set_ylabel("Nombre de Repas distincts", fontsize=12)

# Inclinaison des labels de l'axe X pour éviter qu'ils ne se chevauchent (car YYYY-MM est long)
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()

# =====================================================================
# PRÉPARATION FIGURE 2 (Statistiques des grades et affluences)
# =====================================================================
stats_grades = tenracs.groupby("nom_grade")["idT"].nunique().reset_index()
stats_grades = stats_grades.rename(columns={"idT": "NB_TENRACS"})
stats_grades = stats_grades.dropna(subset=["nom_grade"])

df_participants = participe.merge(repas, on="idR")
df_participants["ANNEE"] = pd.to_datetime(df_participants["date_repas"]).dt.year
stats_repas = df_participants.groupby(["ANNEE", "idR"])["idT"].nunique().reset_index()
stats_repas = stats_repas.rename(columns={"idT": "NB_PARTICIPANTS"})

fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(15, 6))

# --- Graphique 1 (Fig 2) : Diagramme en camembert des Grades ---
ax3.pie(
    stats_grades["NB_TENRACS"],
    labels=stats_grades["nom_grade"],
    autopct='%1.1f%%',
    startangle=90
)
ax3.set_title("Répartition des Tenracs par Grade", fontsize=14, fontweight="bold")

# --- Graphique 2 (Fig 2) : Top 10 des Plats les plus servis ---
# Analyse : Identifier les plats les plus populaires dans l'historique des repas

# 1. Compter dans combien de repas distincts chaque plat apparaît (à partir de la table Contient)
stats_plats = contient.groupby("NOM_PLAT")["idR"].nunique().reset_index()
stats_plats = stats_plats.rename(columns={"idR": "NB_APPARITIONS"})

# 2. Trier par popularité décroissante et garder les 10 premiers
top_10_plats = stats_plats.sort_values(by="NB_APPARITIONS", ascending=False).head(10)

# 3. Inverser l'ordre pour que le graphique affiche le 1er tout en haut (logique barh)
top_10_plats = top_10_plats.sort_values(by="NB_APPARITIONS", ascending=True)

# 4. Vérification et tracé du graphique en barres horizontales
if not top_10_plats.empty:
    ax4.barh(top_10_plats["NOM_PLAT"].astype(str), top_10_plats["NB_APPARITIONS"], 
             color="#9467BD", edgecolor="black", alpha=0.8, zorder=3)

ax4.grid(True, axis='x', linestyle="--", alpha=0.6, zorder=0)
ax4.set_title("Top 10 des Plats les plus souvent servis", fontsize=14, fontweight="bold")
ax4.set_xlabel("Nombre d'apparitions dans les repas", fontsize=12)
ax4.set_ylabel("Nom du Plat", fontsize=12)

plt.tight_layout()
plt.show()