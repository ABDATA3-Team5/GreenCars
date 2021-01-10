#!/usr/bin/env python
# coding: utf-8

#!pip install pandas
#!pip install numpy


# In[1]:


#Imprort des librairies nécessaires
import pandas as pd
import numpy as np


# In[2]:


# Fichier 2019-parc-vehicules-routiers-5pr3.xls :
# Parc par département, région, source d'énergie (2011 à 2019)
# Comprends deux groupes de sheets au format légèrement distincts : avant et apres la fusion des regions en 2016


col_names_temp_av_2017="Départements","Gazole","Essence","Essence-GPL","Electricité","Autres et non déterminées","Total"

col_names_temp_ap_2017=["Régions","Départements","Gazole","Essence","Essence-GPL","Electricité","Autres et non déterminées", "Total"]

col_names=["Année","Régions","Départements","Gazole","Essence","Essence-GPL","Electricité","Autres et non déterminées", "Total"]

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

sheets=["1-1-2010","1-1-2011","1-1-2012","1-1-2013","1-1-2014","1-1-2015","1-1-2016", "1-1-2017","1-1-2018","1-1-2019"]
sheets_av_2017 =["1-1-2010","1-1-2011","1-1-2012","1-1-2013","1-1-2014","1-1-2015","1-1-2016"]

excel_cam=dict()

for year in sheets:
    if year in sheets_av_2017:
         excel_cam[year] = pd.read_excel("https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-07/2019-parc-vehicules-routiers-5pr3.xls", header = None, names=col_names_temp_av_2017, sheet_name=str(year))
    else:
        excel_cam[year] = pd.read_excel("https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-07/2019-parc-vehicules-routiers-5pr3.xls", header = None, names=col_names_temp_ap_2017, sheet_name=str(year))


# In[6]:


def get_reg(row):
    for reg, dep_list in regions.items():
         if str(row['Départements']) in dep_list:
             return reg
        
excel_cam_transfo = dict()

for year in excel_cam :
    sh = excel_cam[year]
    
    #Supp des 4 premières lignes
    sh=sh[4:]
    
    if year=="1-1-2019" :
        #Supp 3 dernières lignes
        sh=sh[:-3]
    else : 
        #Supp 2 dernières lignes
        sh=sh[:-2]
    
   
    if year not in sheets_av_2017:
        #Supp des lignes Total :
        sh = sh[sh['Départements'] != "Total :"]

        #Suppression des lignes vides (lignes de séparation entre les regions)
        sh=sh.dropna(axis=0,how='all')
    
    #Recurération des regions 
    sh['Régions']=sh.apply(lambda row: get_reg(row), axis=1)
    
    if year in sheets_av_2017:
        #Suppression des lignes 
        sh=sh[sh['Régions'].notna()]
        
    
    #Rajout d'une colonne année :
    sh["Année"]=str(year[4:])
    
    #Rérrangement colonnes dans le bon ordre
    sh=sh[col_names]

    
    #Sorting alphabetically
    sh=sh.sort_values('Départements')
    sh=sh.sort_values('Régions')
    
    #Reset de l'index
    sh=sh.reset_index(drop=True)
    
    excel_cam_transfo[year]=sh
    
    #Concatenation des années
    concat_excel_cam_transfo=pd.concat(excel_cam_transfo)
    #Ecriture du fichier
    concat_excel_cam_transfo.to_csv("/home/fitec/Greencars/parc_auto/camion_camionnette_par_dep.csv",sep=';', index = False)
    
