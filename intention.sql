CREATE TABLE Grade(
                      nom_grade VARCHAR2(50) ,
                      niveau_hierarchique NUMBER(10),
                      PRIMARY KEY(nom_grade)
);

CREATE TABLE Rang(
                     nom_rang VARCHAR2(50) ,
                     niveau_hierarchique NUMBER(10),
                     PRIMARY KEY(nom_rang)
);

CREATE TABLE Titre(
                      nom_titre VARCHAR2(50) ,
                      niveau_hierarchique NUMBER(10),
                      PRIMARY KEY(nom_titre)
);

CREATE TABLE Dignite(
                        nom_dignite VARCHAR2(50) ,
                        niveau_hierarchique NUMBER(10),
                        PRIMARY KEY(nom_dignite)
);

CREATE TABLE Organisme_associe(
                                  siret VARCHAR2(50) ,
                                  nom VARCHAR2(50)  NOT NULL,
                                  PRIMARY KEY(siret)
);

CREATE TABLE Plat(
                     nom_plat VARCHAR2(50) ,
                     PRIMARY KEY(nom_plat)
);

CREATE TABLE Ingredient(
                           idI NUMBER(10),
                           nom_ingredient VARCHAR2(50)  NOT NULL,
                           est_legume NUMBER(1) NOT NULL,
                           PRIMARY KEY(idI)
);

CREATE TABLE Sauce(
                      idS NUMBER(10),
                      nom VARCHAR2(50) ,
                      PRIMARY KEY(idS)
);

CREATE TABLE Machine(
                        idM NUMBER(10),
                        nom_machine VARCHAR2(50)  NOT NULL,
                        PRIMARY KEY(idM)
);

CREATE TABLE Territoire(
                           idT NUMBER(10),
                           nom_territoire VARCHAR2(50)  NOT NULL,
                           PRIMARY KEY(idT)
);

CREATE TABLE Modele(
                       nom_modele VARCHAR2(50) ,
                       periode VARCHAR2(50) ,
                       PRIMARY KEY(nom_modele)
);

CREATE TABLE Entretien(
                          idEN NUMBER(10),
                          periodicite_en_mois VARCHAR2(50)  NOT NULL,
                          type_entretien VARCHAR2(50)  NOT NULL,
                          PRIMARY KEY(idEN)
);

CREATE TABLE Adresse(
                        idAdr NUMBER(10),
                        adresse VARCHAR2(50) ,
                        PRIMARY KEY(idAdr)
);

CREATE TABLE Repas(
                      idR VARCHAR2(50) ,
                      intitule VARCHAR2(50)  NOT NULL,
                      date_repas TIMESTAMP NOT NULL,
                      idAdr NUMBER(10) NOT NULL,
                      PRIMARY KEY(idR),
                      FOREIGN KEY(idAdr) REFERENCES Adresse(idAdr)
);

CREATE TABLE Organisation(
                             idO NUMBER(10),
                             nom_organisation VARCHAR2(50)  NOT NULL,
                             type VARCHAR2(50)  NOT NULL,
                             idT NUMBER(10),
                             PRIMARY KEY(idO),
                             FOREIGN KEY(idT) REFERENCES Territoire(idT)
);

CREATE TABLE Tenrac(
                       idT NUMBER(10),
                       nom VARCHAR2(50),
                       courriel VARCHAR2(50),
                       numero_de_telephone VARCHAR2(50),
                       adresse_postale VARCHAR2(50),
                       code_personnel VARCHAR2(50) ,
                       nom_dignite VARCHAR2(50) ,
                       nom_rang VARCHAR2(50),
                       nom_grade VARCHAR2(50),
                       nom_titre VARCHAR2(50) ,
                       siret VARCHAR2(50) ,
                       idO NUMBER(10),
                       PRIMARY KEY(idT),
                       FOREIGN KEY(nom_dignite) REFERENCES Dignite(nom_dignite),
                       FOREIGN KEY(nom_rang) REFERENCES Rang(nom_rang),
                       FOREIGN KEY(nom_grade) REFERENCES Grade(nom_grade),
                       FOREIGN KEY(nom_titre) REFERENCES Titre(nom_titre),
                       FOREIGN KEY(siret) REFERENCES Organisme_associe(siret),
                       FOREIGN KEY(idO) REFERENCES Organisation(idO)
);

CREATE TABLE Ordre_des_tenracs(
                                  idO NUMBER(10),
                                  PRIMARY KEY(idO),
                                  FOREIGN KEY(idO) REFERENCES Organisation(idO)
);

CREATE TABLE Club_Tenrac(
                            idO_1 NUMBER(10),
                            idO NUMBER(10) NOT NULL,
                            PRIMARY KEY(idO_1),
                            FOREIGN KEY(idO_1) REFERENCES Organisation(idO),
                            FOREIGN KEY(idO) REFERENCES Ordre_des_tenracs(idO)
);

CREATE TABLE Est_createur(
                             idT NUMBER(10),
                             idR VARCHAR2(50) ,
                             PRIMARY KEY(idT, idR),
                             FOREIGN KEY(idT) REFERENCES Tenrac(idT),
                             FOREIGN KEY(idR) REFERENCES Repas(idR)
);

CREATE TABLE Participe(
                          idT NUMBER(10),
                          idR VARCHAR2(50) ,
                          PRIMARY KEY(idT, idR),
                          FOREIGN KEY(idT) REFERENCES Tenrac(idT),
                          FOREIGN KEY(idR) REFERENCES Repas(idR)
);

CREATE TABLE CombineIS(
                          idI NUMBER(10),
                          idS NUMBER(10),
                          PRIMARY KEY(idI, idS),
                          FOREIGN KEY(idI) REFERENCES Ingredient(idI),
                          FOREIGN KEY(idS) REFERENCES Sauce(idS)
);

CREATE TABLE Contient(
                         idR VARCHAR2(50) ,
                         nom_plat VARCHAR2(50) ,
                         PRIMARY KEY(idR, nom_plat),
                         FOREIGN KEY(idR) REFERENCES Repas(idR),
                         FOREIGN KEY(nom_plat) REFERENCES Plat(nom_plat)
);

CREATE TABLE Est_associe(
                            idM NUMBER(10),
                            nom_modele VARCHAR2(50) ,
                            PRIMARY KEY(idM, nom_modele),
                            FOREIGN KEY(idM) REFERENCES Machine(idM),
                            FOREIGN KEY(nom_modele) REFERENCES Modele(nom_modele)
);

CREATE TABLE Utilise(
                        idR VARCHAR2(50) ,
                        idM NUMBER(10),
                        PRIMARY KEY(idR, idM),
                        FOREIGN KEY(idR) REFERENCES Repas(idR),
                        FOREIGN KEY(idM) REFERENCES Machine(idM)
);

CREATE TABLE Associe(
                        nom_modele VARCHAR2(50) ,
                        idEN NUMBER(10),
                        PRIMARY KEY(nom_modele, idEN),
                        FOREIGN KEY(nom_modele) REFERENCES Modele(nom_modele),
                        FOREIGN KEY(idEN) REFERENCES Entretien(idEN)
);

CREATE TABLE Historique_Entretien(
                                     idM NUMBER(10),
                                     idO NUMBER(10),
                                     date_entretien TIMESTAMP,
                                     idT NUMBER(10) NOT NULL,
                                     PRIMARY KEY(idM, idO, date_entretien),
                                     FOREIGN KEY(idM) REFERENCES Machine(idM),
                                     FOREIGN KEY(idO) REFERENCES Organisation(idO),
                                     FOREIGN KEY(idT) REFERENCES Tenrac(idT)
);

CREATE TABLE CombineSP(
                          nom_plat VARCHAR2(50) ,
                          idS NUMBER(10),
                          PRIMARY KEY(nom_plat, idS),
                          FOREIGN KEY(nom_plat) REFERENCES Plat(nom_plat),
                          FOREIGN KEY(idS) REFERENCES Sauce(idS)
);

CREATE TABLE CombineIP(
                          nom_plat VARCHAR2(50) ,
                          idI NUMBER(10),
                          PRIMARY KEY(nom_plat, idI),
                          FOREIGN KEY(nom_plat) REFERENCES Plat(nom_plat),
                          FOREIGN KEY(idI) REFERENCES Ingredient(idI)
);

CREATE TABLE Adresse_Partenaire(
                                   idO NUMBER(10),
                                   idAdr NUMBER(10),
                                   PRIMARY KEY(idO, idAdr),
                                   FOREIGN KEY(idO) REFERENCES Ordre_des_tenracs(idO),
                                   FOREIGN KEY(idAdr) REFERENCES Adresse(idAdr)
);