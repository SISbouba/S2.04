import oracledb
import random
from faker import Faker
from faker_food import FoodProvider
from datetime import datetime
import csv
from time import time
from os import mkdir, path

fake = Faker(['fr_FR'])
fakef = FoodProvider(fake)

HOST = ""
PASSWORD = ""
USER = ""

# --- CONFIGURATION ---
NB_TENRACS = 10
NB_REPAS = 100
NB_MACHINES = 600
NB_TERRITOIRE = 10
NB_ORGANISME_ASSOCIE = 100
NB_ADRESSE = 2
NB_PARTICIPE = 10

def generate_data() -> tuple:
    grades = [
        ('Affilie', 1), ('Sympathisant', 2), ('Adhérent', 3), 
        ('Chevalier', 4), ('Grand Chevalier', 5), ('Commandeur', 6), ('Grand croix', 7)
    ]
    rangs = [('Novice', 1), ('Compagnon', 2)]
    titres = [('Philanthrope', 1), ('Protecteur', 2), ('Honorable', 3)]
    dignites = [('Maître', 1), ('Grand Chancelier', 2), ('Grand Maître', 3)]
    
    modeles = [('Traditionnel', 'Mensuel'), ('Combiné 5-en-1', 'Annuel'), ('Bas de gamme', 'Journalier')]
    types_entretien = [('Nettoyage Résistance', '6'), ('Vérification Électrique', '12'), ('Décapage', '3')]

    entretiens = [(i, type_entretien[0], type_entretien[1]) for i, type_entretien in enumerate(types_entretien, start=1)]

    # 1. Tables de Référence (Petites)
    
    # 2. Organismes et Territoires
    territoires = [(i, fake.region().replace("'", ' ')) for i in range(1, NB_TERRITOIRE + 1)]
    organismes = [(fake.siret().replace("'", ' '), fake.company().replace("'", ' ')) for _ in range(NB_ORGANISME_ASSOCIE)]
    adresses = [(i, fake.address().replace('\n', ' ')) for i in range(1, NB_ADRESSE + 1)]

    # 3. Organisations, Ordre et Clubs
    organisations = []
    for i in range(1, 5):
        organisations.append((i, f"L Ordre du Tenrac {fake.name().replace("'", ' ')}", "Ordre", random.randint(1, NB_TERRITOIRE)))
    for i in range(6, 201):
        organisations.append((i, f"Club Tenrac {fake.city().replace("'", ' ')}", "Club", random.randint(1, NB_TERRITOIRE)))

    ordres = [(element[0],) for element in organisations if element[2] == "Ordre"]
    club = [(element[0], random.randrange(1, 5)) for element in organisations if element[2] == "Club"]

    uniques = set()
    while len(uniques) < 15:
        id_o = random.choice(ordres)[0]
        id_a = random.choice(adresses)[0]
        uniques.add((id_o, id_a))
    adresses_partenaire = [(uniques[0], uniques[1]) for uniques in uniques]

    # 4. Tenracs (Le gros volume)
    tenracs = []
    chevaliers_ids = []
    maitres_ids = []
    
    for i in range(1, NB_TENRACS + 1):
        grade = random.choice(grades)[0]
        dignite = random.choice(dignites)[0] if random.random() > 0.8 else None
        
        # Logique métier : code personnel RFID
        siret = random.choice(organismes)[0]
        idO = random.randint(1, 200)

        tenracs.append((
            i, fake.name().replace("'", ' '), fake.email().replace("'", ' '), fake.phone_number().replace("'", ' '), 
            fake.street_address().replace("'", ' '),
            None,
            dignite,
            random.choice(rangs)[0] if random.random() > 0.5 else None,
            grade,
            random.choice(titres)[0] if random.random() > 0.3 else None,
            siret,
            random.choice(organisations)[0] if random.random() > 0.8 else None
        ))
        
        if grade in ['Chevalier', 'Grand Chevalier']:
            chevaliers_ids.append(i)
        if dignite == 'Maître':
            maitres_ids.append(i)
    # 5. Repas
    repas = []
    for i in range(1, NB_REPAS + 1):
        repas.append((
            i,
            f"R-{i}, Festin {fake.word().replace("'", ' ')}", 
            fake.date_time_between(start_date='-2y', end_date='now'),
            random.choice(adresses)[0]
        ))

    est_createur = [(random.choice(chevaliers_ids), element[0]) for element in repas]

    participe = list(set([(random.choice(tenracs)[0], random.choice(repas)[0]) for _ in range(NB_PARTICIPE)]))

    # 6. Machines et Entretiens
    machines = [(i, f"Machine-{fake.word().replace("'", ' ')}-{i}") for i in range(1, NB_MACHINES + 1)]
    
    historique_entretiens = []
    for _ in range(NB_MACHINES * 2):
        historique_entretiens.append((
            random.choice(machines)[0],
            random.choice(organisations)[0],
            fake.date_time_between(start_date='-1y', end_date='now'),
            random.choice(maitres_ids) if maitres_ids else 1
        ))

    est_associe = [(idm[0], nom_modele[0]) for idm in machines for nom_modele in modeles]

    utilise = [(idr[0], idm[0]) for idr in repas for idm in machines]

    associe = [(nom_mod[0], iden[0]) for nom_mod in modeles for iden in entretiens]

    # 7 generation plats, sauces, ingredients, et leurs associations
    unique_plat = set()
    for _ in range(1000):
        unique_plat.add(fakef.dish().replace("'", ' '))
        if len(unique_plat) >= 40:
            break
    plats = [(plat,) for plat in unique_plat]


    ingredients_data = [
        # Légumes
        ("Pomme de terre", 1), ("Oignon", 1), ("Cornichon", 1), ("Tomate", 1), ("Salade", 1),
        ("Poivron", 1), ("Champignon", 1), ("Chou rouge", 1), ("Maïs", 1), ("Coleslaw", 1),

        # Viandes / Protéines
        ("Poulet frit", 0), ("Blanc de poulet", 0), ("Cuisse de poulet", 0), ("Aile de poulet", 0),
        ("Lardons", 0), ("Jambon", 0), ("Bacon", 0), ("Nuggets", 0), ("Filet de poulet", 0),

        # Fromages (raclette)
        ("Fromage à raclette", 0), ("Gruyère", 0), ("Emmental", 0), ("Comté", 0),
        ("Mozzarella", 0), ("Cheddar", 0), ("Reblochon", 0),

        # Féculents / Autres
        ("Pain brioché", 0), ("Frites", 0), ("Crème fraîche", 0), ("Beurre", 0),
        ("Huile de friture", 0), ("Chapelure", 0), ("Farine", 0), ("Œuf", 0),
    ]

    ingredients = [
        (i, name, is_legume)
        for i, (name, is_legume) in enumerate(ingredients_data, start=1)
    ]

    sauces_list = [
        "Béchamel", "Hollandaise", "Vinaigrette", "Pesto", "Marinara",
        "Alfredo", "Teriyaki", "BBQ", "Sriracha", "Tahini",
        "Chimichurri", "Tzatziki", "Aioli", "Mornay", "Velouté"
    ]

    unique_sauces = set(sauces_list)
    sauces = [(i, name) for i, name in enumerate(unique_sauces, start=1)]

    contient = [(idr[0], nom_plat[0]) for idr in repas for nom_plat in plats if random.random() > 0.5]

    combineis = [(idi[0], ids[0]) for idi in ingredients for ids in sauces if random.random() > 0.5]

    combinesp = [(nom_plat[0], idi[0]) for idi in sauces for nom_plat in plats]

    combineip = [(nom_plat[0], idi[0]) for idi in ingredients for nom_plat in plats if random.random() > 0.5]

    return (territoires, organismes, adresses, organisations, dignites, rangs, grades, titres, tenracs, repas, machines, historique_entretiens, modeles, ordres, club, plats, ingredients, sauces, est_associe, utilise, entretiens, associe, est_createur, participe, adresses_partenaire, contient, combineis, combinesp, combineip)


def drop_tables():
    intention = open("intention.sql", "r")
    intentionSQL = intention.read()
    intentionSQL = intentionSQL.split(";")

    with oracledb.connect(user="SYSTEM", password=PASSWORD, host=HOST) as connection:

        with connection.cursor() as cursor:
                cursor.executemany("BEGIN EXECUTE IMMEDIATE 'DROP TABLE ' || (:1); EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;", 
                                   [
                                        ("UTILISE",),
                                        ("CONTIENT",),
                                        ("COMBINESP",),
                                        ("COMBINEIP",),
                                        ("COMBINEIS",),
                                        ("PARTICIPE",),
                                        ("EST_CREATEUR",),
                                        ("ADRESSE_PARTENAIRE",),
                                        ("HISTORIQUE_ENTRETIEN",),
                                        ("ASSOCIE",),
                                        ("EST_ASSOCIE",),
                                        ("SAUCE",),
                                        ("INGREDIENT",),
                                        ("PLAT",),
                                        ("MODELE",),
                                        ("ENTRETIEN",),
                                        ("MACHINE",),
                                        ("REPAS",),
                                        ("ADRESSE",),
                                        ("CLUB_TENRAC",),
                                        ("ORDRE_DES_TENRACS",), 
                                        ("TENRAC",),
                                        ("ORGANISME_ASSOCIE",),
                                        ("ORGANISATION",),
                                        ("TERRITOIRE",),
                                        ("TITRE",),
                                        ("GRADE",),
                                        ("RANG",),
                                        ("DIGNITE",)
                                    ])
                for table in intentionSQL[0:len(intentionSQL)-1]:
                    cursor.execute(table)

def insert(insert, data):
        insert(data[0], "Territoire", "insert into Territoire values (:1, :2)")
        insert(data[1], "Organisme Associe", "insert into Organisme_associe values (:1, :2)")
        insert(data[2], "Adresse", "insert into Adresse values (:1, :2)")
        insert(data[3], "Organisation", "insert into Organisation values (:1, :2, :3, :4)")
        insert(data[4], "Dignite", "insert into Dignite values (:1, :2)")
        insert(data[5], "Rang", "insert into Rang values (:1, :2)")
        insert(data[6], "Grade", "insert into Grade values (:1, :2)")
        insert(data[7], "Titre", "insert into Titre values (:1, :2)")
        insert(data[8], "Tenracs", "insert into Tenrac values (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)")
        insert(data[9], "Repas", "insert into Repas values (:1, :2, :3, :4)")
        insert(data[10], "Machine", "insert into Machine values (:1, :2)")
        insert(data[11], "Historique Entretien", "insert into Historique_Entretien values (:1, :2, :3, :4)")
        insert(data[12], "Modele", "insert into Modele values (:1, :2)")
        insert(data[13], "Ordre des Tenracs", "insert into Ordre_des_tenracs values (:1)")
        insert(data[14], "Club des Tenracs", "insert into Club_Tenrac values (:1, :2)")
        insert(data[15], "Plat", "insert into Plat values (:1)")
        insert(data[16], "Ingredient", "insert into Ingredient values (:1, :2, :3)")
        insert(data[17], "Sauce", "insert into Sauce values (:1, :2)")
        insert(data[18], "Est_Associe", "insert into Est_Associe values (:1, :2)")
        insert(data[19], "Utilise", "insert into Utilise values (:1, :2)")
        insert(data[20], "Entretien", "insert into Entretien values (:1, :2, :3)")
        insert(data[21], "Associe", "insert into Associe values (:1, :2)")
        insert(data[22], "Est_Createur", "insert into Est_Createur values (:1, :2)")
        insert(data[23], "Participe", "insert into Participe values (:1, :2)")
        insert(data[24], "Adresse_Partenaire", "insert into Adresse_Partenaire values (:1, :2)")
        insert(data[25], "Contient", "insert into Contient values (:1, :2)")
        insert(data[26], "CombineIS", "insert into CombineIS values (:1, :2)")
        insert(data[27], "CombineSP", "insert into CombineSP values (:1, :2)")
        insert(data[28], "CombineIP", "insert into CombineIP values (:1, :2)")


def insert_oracle(data, table, sql):
    with oracledb.connect(user=USER, password=PASSWORD, host=HOST) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(sql, 
                        data)
        connection.commit()
        print("Finished " + table)

def insert_csv(data, table, sql):
    with open("csv/"+table+".csv", "w") as file:
        wr = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        wr.writerows(data)
    print("Finished", table)

def insert_sql(data, table, sql):
    insert = sql.split('(')[0]
    result = ""
    for element in data:
        result+=insert + '('
        for i in range(len(element)):
            if isinstance(element[i], str) or isinstance(element[i], datetime):
                result += "'"+ element[i].__str__() + "'"
            else:
                result += str(element[i])
            if i != len(element)-1:
                result+=", "
        result+=')\n'
    with open("sql/" +table + ".sql", "w") as file:
        file.write(result)
    print("Finished", table)

if __name__ == "__main__":

    if not path.exists("csv"):
        mkdir("csv")

    if not path.exists("sql"):
        mkdir('sql')

    NB_TENRACS = eval(input("Number of tenrac: "))
    NB_MACHINES = eval(input("Number of machine: "))
    NB_REPAS = eval(input("Number of repas: "))
    NB_TERRITOIRE = eval(input("Number of territoires: "))
    NB_ORGANISME_ASSOCIE = eval(input("Number of organisme associe: "))
    NB_ADRESSE = eval(input("Number of adresse: "))
    NB_PARTICIPE = eval(input("Number of participe: "))

    a = time()
    print("--- GENERATION DATA STARTED ---")
    data = generate_data()
    print("--- GENERATION DATA FINISHED IN", round(time() - a),"SECONDS ---")
    oracle = str(input("Do you have a oracle db ? (y/N) ")).lower()
    
    if oracle == 'y':
        HOST = str(input("host of database: "))
        USER = str(input("user of database: "))
        PASSWORD = str(input("password of database: "))
        b = time()
        print("--- DROP ALL TABLES AND RECREATE DATABASE ---")
        drop_tables()
        print("--- DROP ALL TABLES AND RECREATE DATABASE FINISHED IN", round(time() - b) ,"SECONDS ")
        print("--- GENERATION ORACLE STARTED ---")
        b = time()
        insert(insert_oracle, data)
        print("--- GENERATION ORACLE FINISHED IN", round(time() - b),"SECONDS ---")

    print("--- GENERATION SQL STARTED ---")
    b = time()
    insert(insert_sql, data)
    print("--- GENERATION SQL FINISHED IN", round(time() - b) ,"SECONDS ---")
    print("--- GENERATION CSV STARTED ---")
    b = time()
    insert(insert_csv, data)
    print("--- GENERATION CSV FINISHED IN", round(time() - b) ,"SECONDS ---")
    print("--- GENERATION FINISHED IN", round(time() - a) ,"SECONDS ---")