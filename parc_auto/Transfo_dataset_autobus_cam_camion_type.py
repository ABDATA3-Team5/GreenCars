#!/usr/bin/env python
# coding: utf-8

#!pip install pandas
#!pip install numpy

# In[1]:


#Imprort des librairies nécessaires
import pandas as pd
import numpy as np


# In[2]:


#Preparation des jeux de données autobus:

#1)Lecture du fichier
excel_autobus = pd.read_excel("https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-04/2019-parc-vehicules-routiers-3pf2.xls", header = None)

#2)Division du jeu de do en 2
excel_autobus_ap_2010= excel_autobus[:66]
excel_autobus_av_2010= excel_autobus[66:]

#3)Nom de colonnes :
col_names_ap_2010_temp=["Classes de places assises","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019"]
col_names_av_2010_temp=["Classes de places assises","2001","2002","2003","2004","2005","2006","2007","2008","2009"]

###4.1) Formatage dataset - Après 2010: 
excel_autobus_ap_2010.columns = col_names_ap_2010_temp
#Supp ds 3 premières lignes et de la derniere (afin de garder un ligne vide avant et après)
excel_autobus_ap_2010=excel_autobus_ap_2010[3:]
excel_autobus_ap_2010=excel_autobus_ap_2010[:-1]
excel_autobus_ap_2010=excel_autobus_ap_2010.reset_index(drop=True)

###4.2) Formatage dataset - Avant 2010:
#Suppression de la dernière colonne et attribution de noms de colonnes
excel_autobus_av_2010=excel_autobus_av_2010.iloc[:, :-1]
excel_autobus_av_2010.columns=col_names_av_2010_temp

#Supp de la première ligne et rajout d'une derniere ligne (afin de garder un ligne vide avant et après)
excel_autobus_av_2010.loc[len(excel_autobus_av_2010)] = np.nan
excel_autobus_av_2010=excel_autobus_av_2010[1:]
excel_autobus_av_2010=excel_autobus_av_2010.reset_index(drop=True)


# In[3]:


#Preparation des jeux de données cam_camionette:

#1)Lecture du fichier
excel_cam = pd.read_excel("https://www.statistiques.developpement-durable.gouv.fr/sites/default/files/2019-04/2019-parc-vehicules-routiers-5pf2.xls", header = None)

#2)Nom de colonnes :
col_names_cam=["Classes de PTAC","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019"]

#3) Formatage Dataset
#Attribution des noms de colonnes
excel_cam.columns = col_names_cam
#Supp ds 2 premières lignes et de la derniere (afin de garder un ligne vide avant et après)
excel_cam=excel_cam[2:]
excel_cam=excel_cam[:-1]
excel_cam=excel_cam.reset_index(drop=True)
excel_cam.iloc[0]=np.nan # On set toute la première ligne à null


# In[4]:


def recup_tab_energie (dataset, tab_colnames):
    col_categorie=tab_colnames[0]
    #Récuperation des lignes de séparation entre chaque tableau
    sep=[l for l in range(len(dataset)) if dataset.iloc[l].isna().all()]

    #Récuperation des tableaux par energie
    tab=dict()
    for s in range(len(sep)-1) :
        #print(sep[s]+1, dataset['Classes de places assises'][sep[s]+1])
        tab[dataset[col_categorie][sep[s]+1]]=dataset.iloc[sep[s]+3:sep[s+1]-1]
        #sep[s]+3 afin d'enlever la ligne vide + la ligne du type denergie + la ligne des titres de colonnes
        #sep[s+1]-1 afin d'enlever la ligne Total
    return (tab)
    


# In[5]:


def pivot_and_merge (tab, tab_colnames):
    col_categorie=tab_colnames[0]
    #Pivot de chaque tableau et récupération sous forme de liste
    tab_transfo=list()
    for energie in tab:
        #tab[energie]=pd.melt(tab[energie],id_vars=[col_categorie], value_vars=["2010","2011","2012","2013","2014","2015","2016","2017","2018","2019"],var_name="Année", value_name=str(energie))
        #tab_transfo=list(tab.values())
        tab_transfo.append(pd.melt(tab[energie],id_vars=[col_categorie], value_vars=tab_colnames[1:],var_name="Année", value_name=str(energie)))

    # Merging des tableaux
    tab_transfo_merged=tab_transfo[0]
    del tab_transfo[0]
    for tab in tab_transfo:
        tab_transfo_merged = pd.merge(tab_transfo_merged, tab,on=[col_categorie,'Année'],how='outer')

    #Remplacement des valeurs nulles
    tab_transfo_merged.iloc[:,2:]=tab_transfo_merged.iloc[:,2:].fillna(0).astype(int)
    #tab_transfo_merged.isnull().sum()
    
    return(tab_transfo_merged)
   


# In[6]:


autobus_ap_2010_transfo=pivot_and_merge(recup_tab_energie(excel_autobus_ap_2010,col_names_ap_2010_temp),col_names_ap_2010_temp)

autobus_ap_2010_transfo.to_csv("/home/fitec/Greencars/parc_auto/autobus_ap_2010_par_type.csv",sep=';', index = False)

autobus_av_2010_transfo=pivot_and_merge(recup_tab_energie(excel_autobus_av_2010,col_names_av_2010_temp),col_names_av_2010_temp)

autobus_av_2010_transfo.to_csv("/home/fitec/Greencars/parc_auto/autobus_av_2010_par_type.csv",sep=';', index = False)


# In[7]:


tab_cam=recup_tab_energie(excel_cam,col_names_cam) 

tab_camionnette=dict()
tab_camion=dict()

#Recupération des tableau camion d'un coté et camionettes de l'autre
for energie in tab_cam:
    tab_cam[energie]=tab_cam[energie].reset_index(drop=True)
    
    #sep_cam_camion[energie]= [l for l in range(len(tab_cam[energie])) if "Total" in tab_cam[energie]["Classes de PTAC"][l]]
    
    tab_camionnette[energie]=tab_cam[energie][0:4]
    tab_camion[energie]=tab_cam[energie][5:12]

tab_camion_transfo=pivot_and_merge(tab_camion, col_names_cam)

tab_camion_transfo.to_csv("/home/fitec/Greencars/parc_auto/camion_par_type.csv",sep=';', index = False)

tab_camionnette_transfo=pivot_and_merge(tab_camionnette, col_names_cam)

tab_camionnette_transfo.to_csv("/home/fitec/Greencars/parc_auto/camionnette_par_type.csv",sep=';', index = False)

