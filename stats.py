import pandas as pd
import matplotlib.pyplot as plt

couleurs = plt.cm.Set3.colors

grades = pd.read_csv("csv/Grade.csv", header=None).rename(columns={0: "nom_grade"})
tenracs = pd.read_csv("csv/Tenracs.csv", header=None).rename(columns={8: "nom_grade", 11: "idO", 0: "idT"})
organisation = pd.read_csv("csv/Organisation.csv", header=None).rename(columns={0: "idO", 2: "type_organisation", 1: "nom_organisation"})
contient = pd.read_csv("csv/Contient.csv", header=None).rename(columns={0: "idR", 1: "nom_plat"})
combineIP = pd.read_csv("csv/CombineIP.csv", header=None).rename(columns={0: "nom_plat", 1: "idI"})
ingredient = pd.read_csv("csv/Ingredient.csv", header=None).rename(columns={0: "idI", 2: "est_legume"})
repas = pd.read_csv("csv/Repas.csv", header=None).rename(columns={0: "idR", 2: "Date"})
participe = pd.read_csv("csv/Participe.csv", header=None).rename(columns={0: "idT", 1: "idR"})

tenracs_grades = tenracs.merge(grades, on="nom_grade").groupby("nom_grade")

values = tenracs_grades.size() / len(tenracs)

contient_combineip_ingredient = contient.merge(combineIP, on="nom_plat").merge(ingredient, on="idI")
contient_combineip_ingredient_legume = contient_combineip_ingredient.loc[contient_combineip_ingredient["est_legume"] == 1]
repas_legume = repas.merge(contient_combineip_ingredient_legume, on="idR")

dates = pd.to_datetime(repas_legume["Date"]).dt.month
repas_month = repas_legume.groupby(dates).size()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), sharey=True)

ax1.plot(repas_month.index, repas_month.values, 
         color='#2A9D8F',
         linewidth=3,
         marker='s', 
         markersize=8,
         label='Total Repas Légumiers')

ax1.set_title("Évolution Mensuelle des Repas avec des légumes", 
          fontsize=13, fontweight='bold', color='#333333', pad=20)
ax1.set_xlabel("Mois", fontsize=12, color='#555555', labelpad=10)
ax1.set_ylabel("Nombre de Repas", fontsize=12, color='#555555', labelpad=10)


contient_combineip_ingredient_sans_legume = contient_combineip_ingredient.loc[contient_combineip_ingredient["est_legume"] == 0]
repas_sans_legume = repas.merge(contient_combineip_ingredient_sans_legume, on="idR")

dates = pd.to_datetime(repas_sans_legume["Date"]).dt.month
repas_month = repas_sans_legume.groupby(dates).size()

ax2.plot(repas_month.index, repas_month.values, 
         color='#2A9D8F',
         linewidth=3,
         marker='s', 
         markersize=8,
         label='Total Repas Légumiers')

ax2.set_title("Évolution Mensuelle des Repas sans légumes", 
          fontsize=13, fontweight='bold', color='#333333', pad=20)
ax2.set_xlabel("Mois", fontsize=12, color='#555555', labelpad=10)
ax2.set_ylabel("Nombre de Repas", fontsize=12, color='#555555', labelpad=10)

plt.show()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

ax1.pie(values, 
        labels=grades["nom_grade"], 
        colors=couleurs,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.80,
        textprops={'fontsize': 11, 'weight': 'bold', 'color': '#333333'},
        wedgeprops={'edgecolor': 'white', 'linewidth': 2})

ax1.set_title("Répartition des Tenracs par Grade", fontsize=16, fontweight='bold', pad=20)

tenracs_organisations = tenracs.merge(organisation, on="idO")
tenracs_organisations_club = tenracs_organisations.loc[tenracs_organisations["type_organisation"] == "Club"].groupby("nom_organisation").count()

ax2.bar(tenracs_organisations_club.index, 
        tenracs_organisations_club["idT"], 
        color='#4C72B0',
        edgecolor='black',
        alpha=0.8)

ax2.set_title("Nombre de Tenracs par Club", fontsize=16, fontweight='bold', pad=15)
ax2.set_xlabel("Clubs", fontsize=12)
ax2.set_ylabel("Nombre d'inscrits", fontsize=12)

ax2.set_xticks(ax2.get_xticks())

ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()

fig, ax = plt.subplots(figsize=(12, 7), facecolor='#FAFAFA')

stats_plats = contient.groupby("nom_plat")["idR"].nunique().reset_index()
stats_plats = stats_plats.rename(columns={"idR": "nb_apparitions"})

top_10_plats = stats_plats.sort_values(by="nb_apparitions", ascending=False).head(10)

top_10_plats = top_10_plats.sort_values(by="nb_apparitions", ascending=True)

barres = ax.barh(top_10_plats["nom_plat"].astype(str), 
                 top_10_plats["nb_apparitions"], 
                 color="#8E44AD",
                 height=0.65,
                 zorder=3)

ax.bar_label(barres, padding=8, fontsize=11, fontweight='bold', color='#333333')
plt.title("Top 10 des plats les plus fréquents", fontsize=18, fontweight='bold', color='#2C3E50', pad=20, loc='left')

plt.xlabel("Nombre d'apparitions", fontsize=12, color='#7F8C8D', labelpad=10)
plt.show()

fig, ax = plt.subplots(figsize=(10, 7), facecolor='#FAFAFA')
ax.set_facecolor('#FAFAFA')

stats_complexite = contient_combineip_ingredient.groupby("nom_plat").agg(
    nb_ingredients=('idI', 'nunique'),
    a_un_legume=('est_legume', 'max')
).reset_index()

stats_complexite["categorie"] = stats_complexite["a_un_legume"].apply(
    lambda x: "Avec légume(s)" if x == 1 else "Sans légume"
)

donnees_avec_legumes = stats_complexite[stats_complexite["categorie"] == "Avec légume(s)"]["nb_ingredients"].tolist()
donnees_sans_legumes = stats_complexite[stats_complexite["categorie"] == "Sans légume"]["nb_ingredients"].tolist()

valeurs_a_tracer = [donnees_sans_legumes, donnees_avec_legumes]
etiquettes = ["Plats sans légume", "Plats avec légume(s)"]

box = ax.boxplot(valeurs_a_tracer, 
                 labels=etiquettes, 
                 patch_artist=True, 
                 widths=0.5,
                 zorder=3,
                 medianprops={'color': '#2C3E50', 'linewidth': 2},
                 whiskerprops={'color': '#7F8C8D', 'linewidth': 1.5},
                 capprops={'color': '#7F8C8D', 'linewidth': 1.5},
                 flierprops={'marker': 'o', 'markerfacecolor': '#E74C3C', 'markersize': 6, 'markeredgecolor': 'none'})

couleurs_box = ['#BDC3C7', '#2ECC71']
for patch, color in zip(box['boxes'], couleurs_box):
    patch.set_facecolor(color)
    patch.set_edgecolor('#7F8C8D')
    patch.set_linewidth(1.5)

plt.title("Complexité des plats : Avec vs Sans Légumes", fontsize=16, fontweight='bold', color='#2C3E50', pad=20)
plt.ylabel("Nombre total d'ingrédients par plat", fontsize=12, color='#7F8C8D', labelpad=10)

plt.xticks(fontsize=12, fontweight='bold', color='#34495E')

plt.tight_layout()
plt.show()