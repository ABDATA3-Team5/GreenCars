#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Imprort des librairies nécessaires
import pandas as pd
import numpy as np


# In[2]:


#Preparation des jeux de données autobus:

#1)Nom de colonnes 
col_names_temp = ["Emissions","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018"]
col_names_ap_2010_temp = ["Emissions","2010","2011","2012","2013","2014","2015","2016","2017","2018"]
col_names_av_2010_temp = ["Emissions","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009"]
col_names_benz = ["Emissions","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018"]

#2)Lecture du fichier
emissions_poll_csv = 'emissions_polluantes.csv'
emissions_poll = pd.read_csv(emissions_poll_csv, sep=";",  quotechar='"', encoding="utf-8",header = None)

#3) Formatage Dataset
#Suppression des lignes vides
emissions_poll.dropna(axis=0,how='all',inplace=True)
#Suppression d'une ligne note inutile :
row_note = emissions_poll[emissions_poll[0] == "Note : somme des HAP tels que définis par la CEE-NU : benzo(a)pyrène, benzo(b)fluoranthène, benzo(k)fluoranthène et indeno(1,2,3-cd)pyrène"].index[0]
emissions_poll=emissions_poll.drop([row_note])
#Reset de l'index des lignes
emissions_poll.reset_index(drop=True,inplace=True)

#Cas du benzene : re-organisation des colonnes
emission_poll_benz=emissions_poll[460:]
cols_to_drop=[20, 21,22,23,24,25,26,27,28,29]
emission_poll_benz=emission_poll_benz.drop(cols_to_drop, axis=1)
emission_poll_benz.columns=col_names_benz
emission_poll_benz ["1990"] = "0"
emission_poll_benz ["1991"] = "0"
emission_poll_benz ["1992"] = "0"
emission_poll_benz ["1993"] = "0"
emission_poll_benz ["1994"] = "0"
emission_poll_benz ["1995"] = "0"
emission_poll_benz ["1996"] = "0"
emission_poll_benz ["1997"] = "0"
emission_poll_benz ["1998"] = "0"
emission_poll_benz ["1999"] = "0"
emission_poll_benz = emission_poll_benz[col_names_temp]

#Re-fusionage du benzene avec le reste du dataset
emissions_poll.columns =col_names_temp
emissions_poll=pd.concat([emissions_poll[:460],emission_poll_benz])

#4) Division du dataset en 2 (av et ap 2010)
emissions_poll_av_2010 = emissions_poll[col_names_av_2010_temp]
emissions_poll_ap_2010 = emissions_poll[col_names_ap_2010_temp]


# In[6]:


#Recupère un dictionnaire des tableaux par emissions poulluante
def recup_tab_par_emissions(dataset):
    tab={}
    for row in range(len(dataset)):
        cell=dataset['Emissions'][row]
        if "D2.2-b" in str(cell):
            emission=cell.split()[3]
            #print(emission)
            deb=row+3
            #print(deb)
        if "Source" in str(cell):
            fin=row
            #print(fin)    
            tab[emission]=dataset[deb:fin]
            tab[emission].reset_index(drop=True,inplace=True)
            tab[emission]=tab[emission].replace({',': '.'}, regex=True)
            continue
    return(tab)


# In[7]:


#Recuperation des tableaux par type d'emissions
emissions_poll_ap_2010_em=recup_tab_par_emissions(emissions_poll_ap_2010)
emissions_poll_av_2010_em=recup_tab_par_emissions(emissions_poll_av_2010)


# In[10]:


# Pour un tableau émission donné, récupère un dictionnaire des sous tableaux par catégorie de véhicule

def recup_sub_tab_par_cat_vehicule(tab_em,tab_colnames,emission):
    cat_vehicule= ["Voitures particulières","Véhicules utilitaires","Poids lourds","Deux roues","Ensemble des véhicules"]
    
    ###Etape 1 : recuperation des ss-tableaux de catégorie de véhicule dans un dico
   
    #Récuperation des lignes de séparation entre chaque ss-tableaux 
    sep=[l for l in range(len(tab_em)) if str(tab_em['Emissions'][l]) in cat_vehicule]
    sep.append(len(tab_em))
    #return(sep)

    #Récuperation des ss-tableaux
    sub_tab=dict()
    for s in range(len(sep)-1) :
        sub_tab[cat_vehicule[s]]=tab_em[sep[s]+1:sep[s+1]] 
    #return (sub_tab)
    
    #Etape 2 : pivot de chaque ss-tableau
    sub_tab_transfo=dict()
    
    for cat in sub_tab:
        sub_tab_transfo[cat]=sub_tab[cat].transpose()
        sub_tab_transfo[cat].reset_index(inplace=True)
        sub_tab_transfo[cat]["index"][0]="Année"
        sub_tab_transfo[cat].columns = sub_tab_transfo[cat].iloc[0]
        sub_tab_transfo[cat]=sub_tab_transfo[cat][1:]
        sub_tab_transfo[cat]["Emissions"]=emission
    return (sub_tab_transfo)


# In[11]:


emissions_poll_ap_2010_em_veh={}
for em in emissions_poll_ap_2010_em:
    emissions_poll_ap_2010_em_veh[em]=recup_sub_tab_par_cat_vehicule(emissions_poll_ap_2010_em[em],col_names_ap_2010_temp,em)

emissions_poll_av_2010_em_veh={}
for em in emissions_poll_av_2010_em:
    emissions_poll_av_2010_em_veh[em]=recup_sub_tab_par_cat_vehicule(emissions_poll_av_2010_em[em],col_names_av_2010_temp,em)


# In[14]:


#Concatene toutes les émissions par catégorie de véhicule 
def concat_tab_em_veh (tab_em_veh):
    cat_vehicule= ["Voitures particulières","Véhicules utilitaires","Poids lourds","Deux roues","Ensemble des véhicules"]
    tab_concat=dict()
    for cat in cat_vehicule:
        tab_to_concat=list()
        for em in tab_em_veh:
            tab_to_concat.append(tab_em_veh[em][cat])
        tab_concat[cat]=pd.concat(tab_to_concat)
        tab_concat[cat].reset_index(drop=True, inplace=True)
    return(tab_concat)


# In[15]:


emissions_poll_ap_2010_merged= concat_tab_em_veh(emissions_poll_ap_2010_em_veh)
emissions_poll_av_2010_merged= concat_tab_em_veh(emissions_poll_av_2010_em_veh)


# In[17]:


def ecriture_fichiers_transfo (tab_merged,years) :
    cat_vehicule= ["Voitures particulières","Véhicules utilitaires","Poids lourds","Deux roues","Ensemble des véhicules"]
    for cat in cat_vehicule:
        cat_str=cat.lower()
        cat_str=cat_str.replace("é","e")
        cat_str=cat_str.replace("è","e")
        cat_str="_".join(cat_str.split())
        name_csv= cat_str+years+".csv"
        tab_merged[cat].to_csv(name_csv,sep=';', index = False)


# In[18]:


ecriture_fichiers_transfo(emissions_poll_ap_2010_merged,"_ap_2010")
ecriture_fichiers_transfo(emissions_poll_av_2010_merged,"_av_2010")

