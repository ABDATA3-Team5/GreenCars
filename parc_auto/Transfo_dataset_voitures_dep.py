#!/usr/bin/env python
# coding: utf-8

#!pip install pandas
#!pip install numpy

# In[1]:


#Imprort des librairies nécessaires
import pandas as pd
import numpy as np


# In[2]:


# Fichier 2019-parc-vehicules-routiers-2pr2.xls :
# Parc par département, région, source d'énergie (2011 à 2019)
# Comprends deux groupes de sheets au format légèrement distincts : avant et apres la fusion des regions en 2016

#Nom des colonnes
col_names_temp_2011=["Regions","Departements", "Ess-SuperE<6", "Ess-SuperE6-7", "Ess-SuperE>7", "Elec-Ess<6","Elec-Ess>6", "Gazole<6", "Gazole>6", "Ess-GPL>6", "Ess-GPL<6",
"Electricite","Autres+Non_detecte","Total"]
col_names_temp=["Regions","Departements", "Ess-SuperE<6", "Ess-SuperE6-7", "Ess-SuperE>7", "Elec-Ess<6","Elec-Ess>6", "Gazole<6", "Gazole>6", "Ess-GPL>6", "Ess-GPL<6",
"Electricite","Gazole-électricité","Autres+Non_detecte","Total"]

col_names= ["Année","Regions","Departements", "Essence+Superéthanol","Electricite-Essence","Gazole", "Essence-GPL",
"Electricite","Gazole-électricité","Autres+Non_detecte","Total"]


#Dico des regions et des departements :
regions = {"Auvergne-Rhône-Alpes":["Ain","Allier","Ardèche","Cantal","Drôme","Haute-Loire","Haute-Savoie","Isère","Loire","Puy-de-Dôme","Rhône","Savoie"],
           "Bourgogne-Franche-Comté":["Côte-d'Or","Doubs","Haute-Saône","Jura","Nièvre","Saône-et-Loire","Territoire de Belfort","Yonne"],
           "Bretagne":["Côtes-d'Armor","Finistère","Ille-et-Vilaine","Morbihan"],
           "Centre-Val de Loire":["Cher","Eure-et-Loir","Indre","Indre-et-Loire","Loiret","Loir-et-Cher"],
           "Corse":["Corse-du-Sud","Haute-Corse"],
           "Grand Est":["Ardennes","Aube","Bas-Rhin","Haute-Marne","Haut-Rhin","Marne","Meurthe-et-Moselle","Meuse","Moselle","Vosges"],
           "Hauts-de-France":["Aisne","Nord","Oise","Pas-de-Calais","Somme"],
           "Île-de-France":["Essonne","Hauts-de-Seine","Paris","Seine-et-Marne","Seine-Saint-Denis","Val-de-Marne","Val-d'Oise","Yvelines"],
           "Normandie":["Calvados","Eure","Manche","Orne","Seine-Maritime"], 
           "Nouvelle-Aquitaine":["Charente","Charente-Maritime","Corrèze","Creuse","Deux-Sèvres","Dordogne","Gironde","Haute-Vienne","Landes","Lot-et-Garonne","Pyrénées-Atlantiques","Vienne"],
           "Occitanie":["Ariège","Aude","Aveyron","Gard","Gers","Haute-Garonne","Hautes-Pyrénées","Hérault","Lot","Lozère","Pyrénées-Orientales","Tarn","Tarn-et-Garonne"],
           "Pays de la Loire":["Loire-Atlantique","Maine-et-Loire","Mayenne","Sarthe","Vendée"],
           "Provence-Alpes-Côte d'Azur":["Alpes-de-Haute-Provence","Alpes-Maritimes","Bouches-du-Rhône","Hautes-Alpes","Var","Vaucluse"]}
           


# In[3]:


#Recuperation de chaque sheet dans un dico :

sheets=["1-1-2011","1-1-2012","1-1-2013","1-1-2014","1-1-2015","1-1-2016", "1-1-2017","1-1-2018","1-1-2019"]


excel_voit_part=dict()

for year in sheets:
    if year == '1-1-2011':
         excel_voit_part[year] = pd.read_excel("https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-04/2019-parc-vehicules-routiers-2pr2.xls", header = None, names=col_names_temp_2011, sheet_name=str(year))
    else:
        excel_voit_part[year] = pd.read_excel("https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-04/2019-parc-vehicules-routiers-2pr2.xls", header = None, names=col_names_temp, sheet_name=str(year))


# In[5]:


def get_reg(row):
    for reg, dep_list in regions.items():
         if str(row['Departements']) in dep_list:
             return reg
        
excel_voit_part_transfo = dict()

for year in excel_voit_part :
    sh = excel_voit_part[year]
    
    if year =="1-1-2018" or year=="1-1-2019" :
        #Supp des 4 premières lignes
        sh=sh[4:]
        #Supp des lignes Total :
        sh = sh[sh.Departements != "Total"]
    else:
        #Supp des 3 premières lignes
        sh=sh[3:]
        #Supp des lignes Total :
        sh = sh[sh['Departements'] != "Total :"]
 
    #Supp 4 dernières lignes
    sh=sh[:-4]

    #Suppression des lignes vides (lignes de séparation entre les regions)
    sh=sh.dropna(axis=0,how='all')

    #Recurération des regions 
    sh['Regions']=sh.apply(lambda row: get_reg(row), axis=1)
    
    #Rajout d'une columne "Gazole-électricité" dans le cas de l'année 2011
    if year =="1-1-2011" :
        sh["Gazole-électricité"] = np.nan
        
    #Remplacement des valeurs nulles par 0 (il ny en a que dans la colonnes galzole-elec)
    sh["Gazole-électricité"]=sh["Gazole-électricité"].fillna(0).astype(int)
    

    #Regroupement des colonnes Essence+Superéthanol,Electricite-Essence, Gazole, Essence-GPL :
    sh["Essence+Superéthanol"]= sh["Ess-SuperE<6"]+sh["Ess-SuperE6-7"]+sh["Ess-SuperE>7"]
    sh["Electricite-Essence"]= sh["Elec-Ess<6"]+sh["Elec-Ess>6"]
    sh["Gazole"]=sh["Gazole<6"]+sh["Gazole>6"]
    sh["Essence-GPL"]=sh["Ess-GPL>6"]+sh["Ess-GPL<6"]

    ### Test pour vérifier que les calculs son corrects
    sh["Total_test"] = sh["Essence+Superéthanol"]+sh["Electricite-Essence"]+sh["Gazole"]+sh["Essence-GPL"]+sh["Electricite"]+sh["Gazole-électricité"]+sh["Autres+Non_detecte"]
        
    #Rajout d'une colonne année :
    sh["Année"]=str(year[4:])
    
    #Suppression des colonnes temp et re-arrangement dans le bon ordre
    sh=sh[col_names]

    
    #Sorting alphabetically
    sh=sh.sort_values('Departements')
    sh=sh.sort_values('Regions')
    
    #Reset de l'index
    sh=sh.reset_index(drop=True)
    
    excel_voit_part_transfo[year]=sh
    
    #Concatenation des années
    concat_excel_voit_part_transfo=pd.concat(excel_voit_part_transfo)
    #Renommage des colonnes parce que j'ai fait n'importe auoi au debut
    concat_excel_voit_part_transfo = concat_excel_voit_part_transfo.rename(columns={"Regions":"Régions","Departements" : "Départements" ,"Electricite-Essence":"Electricité-Essence","Electricite":"Electricité","Autres+Non_detecte":"Autres et non détectés"})
    #Ecriture du fichier
    concat_excel_voit_part_transfo.to_csv("/home/fitec/Greencars/parc_auto/voiture_par_dep.csv",sep=';', index = False)


