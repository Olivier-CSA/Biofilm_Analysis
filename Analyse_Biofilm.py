import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import glob
import tkinter as tk
from tkinter import filedialog

def main() :
    global cheminMonoculture
    cheminMonoculture = "***YOUR-PATH***"
    global cheminPolyespece
    cheminPolyespece = "***YOUR-PATH***"

    ouvrirFenetreChoixDossier("Dossier Monoculture")
    dfMonoculture = importDonnees(cheminMonoculture + "/*.csv")
    dfPolyespece = importDonnees(cheminPolyespece + "/*.csv")

    surface = 'Surface (micron^2)'
    volume = 'Volume (micron^3)'

    dfMonoculture = retireTropPetit(dfMonoculture, volume, 10)
    dfPolyespece = retireTropPetit(dfPolyespece, volume, 10)

    print("Nombre de données pour le biofilm en monoculture : " + str(dfMonoculture.shape[0]))
    print("Nombre de données pour le biofilm en polyespèce : " + str(dfPolyespece.shape[0]))


    #boiteEtMoustaches(dfMonoculture[volume], dfMonoculture[surface], dfPolyespece[volume], dfPolyespece[surface], "Analyse des agrégats","Taille des agrégats" )
    diagrammeViolon(dfMonoculture[volume].sort_values(), dfMonoculture[surface].sort_values(), dfPolyespece[volume].sort_values(), dfPolyespece[surface].sort_values(), "Analyse des agrégats","Taille des agrégats" )


def importDonnees(chemin) :
    fichiers = glob.glob(chemin)
    print("Chemin effectivement utilisé : " + chemin)
    fichierCombine = []

    for fichier in fichiers :
        df = pd.read_csv(fichier)
        fichierCombine.append(df)
    dfComplet = pd.concat(fichierCombine, axis=0, ignore_index=True)
    return dfComplet

def boiteEtMoustaches(volumeMonoculture, surfaceMonoculture, volumePolyespece, surfacePolyespece, titre="Titre", etiquette="Étiquette") :
    boites = plt.boxplot([volumeMonoculture,surfaceMonoculture, volumePolyespece, surfacePolyespece], patch_artist=True)
    plt.title(titre)
    plt.ylabel(etiquette)

    #Spécifique (à généraliser si je veux réutiliser cette fonction)
    couleurs = ['lightblue', 'lightblue', 'lightgreen', 'lightgreen']
    for i, patch in enumerate(boites['boxes']):
        patch.set_facecolor(couleurs[i])

    legend_elements = [Patch(facecolor='lightblue', edgecolor='black', label='Monoculture'), Patch(facecolor='lightgreen', edgecolor='black', label='Polyespèce')]
    plt.legend(handles=legend_elements)

    plt.ylim(0,100)
    plt.xticks([1, 2, 3, 4], ['Volume (micron^3)', 'Surface (micron^2)', 'Volume (micron^3)', 'Surface (micron^2)'])

    plt.show()

def MoustachesMinMax(listeTriee, quartile1, quartile3):
    distanceInterQuartiles = quartile3 - quartile1
    moustacheMax = None
    moustacheMin = None
    
    valeurMax = quartile3 + distanceInterQuartiles * 1.5
    listeTriee.reset_index(inplace=True, drop=True)
    derniereValeur = listeTriee[0]
    for valeur in listeTriee :
        if valeur < valeurMax :
            derniereValeur = valeur
        elif valeur == valeurMax :
            moustacheMax = valeur
            break
        else :
            moustacheMax = derniereValeur
            break
    if moustacheMax is None :
        moustacheMax = derniereValeur

    valeurMin = quartile1 - distanceInterQuartiles * 1.5
    derniereValeur = listeTriee[0]
    for valeur in listeTriee :
        if valeur > valeurMin :
            derniereValeur = valeur
        elif valeur == valeurMin :
            moustacheMin = valeur
            break
        else :
            moustacheMin = derniereValeur
            break
    if moustacheMin is None :
        moustacheMin = listeTriee[0]
    
    return moustacheMin, moustacheMax


def statistiques(donnees) :
    listeQuartile1 = []
    listeMediane = []
    listeQuartile3 = []
    
    for liste in donnees :
        listeQuartile1.append(np.percentile(liste,25))
        listeMediane.append(np.percentile(liste,50))
        listeQuartile3.append(np.percentile(liste,75))

    return listeQuartile1, listeMediane, listeQuartile3


def diagrammeViolon(volumeMonoculture, surfaceMonoculture, volumePolyespece, surfacePolyespece, titre="Titre", etiquette="Étiquette") :

    donnees = [volumeMonoculture,surfaceMonoculture,volumePolyespece,surfacePolyespece]
    figure, (panneau) = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))

    violons = panneau.violinplot(donnees, showmeans=False, showmedians=False, showextrema=False)
    plt.title(titre)
    plt.xlabel(etiquette)
    plt.ylabel('Valeurs')

    couleurs = ['#3ad48c', '#3ad48c', '#D43F3A', '#D43F3A']
    for i, patch in enumerate(violons['bodies']):
        patch.set_facecolor(couleurs[i])
        patch.set_edgecolor('black')

    legend_elements = [Patch(facecolor='#3ad48c', edgecolor='black', label='Monoculture'), Patch(facecolor='#D43F3A', edgecolor='black', label='Polyespèce')]
    plt.legend(handles=legend_elements)

    quartile1, medianes, quartile3 = statistiques(donnees)
    quartile1 = np.ndarray(shape=(4,), dtype=float, buffer=np.array(quartile1))
    medianes = np.ndarray(shape=(4,), dtype=float, buffer=np.array(medianes)) 
    quartile3 = np.ndarray(shape=(4,), dtype=float, buffer=np.array(quartile3)) 

    moustaches = np.array([
        MoustachesMinMax(donneeTriee, q1, q3)
        for donneeTriee, q1, q3 in zip(donnees, quartile1, quartile3)
        ])
    moustaches_min, moustaches_max = moustaches[:, 0], moustaches[:, 1]

    inds = np.arange(1, len(medianes) + 1)
    panneau.scatter(inds, medianes, marker='o', color='white', s=30, zorder=3)
    panneau.vlines(inds, quartile1, quartile3, color='k', linestyle='-', lw=5)
    panneau.vlines(inds, moustaches_min, moustaches_max, color='k', linestyle='-', lw=1)

    plt.show()


def parcourirDossierMonoculture() : 
    dossier = filedialog.askdirectory()
    if dossier:
        global cheminMonoculture
        cheminMonoculture = dossier
        labelMonoculture.config(text=("Monoculture - Dossier sélectionné : " + cheminMonoculture))
        print("Dossier sélectionné Monoculture : ", cheminMonoculture)

def parcourirDossierPolyespece() : 
    dossier = filedialog.askdirectory()
    if dossier:
        global cheminPolyespece
        cheminPolyespece = dossier
        labelPolyespece.config(text=("Polyespece - Dossier sélectionné : " + cheminPolyespece))

def enregistrerChemin() :
    fenetre.destroy()

def ouvrirFenetreChoixDossier(message="Sélectionner un dossier") :
    global fenetre
    fenetre = tk.Tk()
    fenetre.title(message)
    fenetre.geometry("1000x400")

    global labelMonoculture
    labelMonoculture = tk.Label(fenetre, text="")
    labelMonoculture.pack(pady=20)

    global labelPolyespece
    labelPolyespece = tk.Label(fenetre, text="")
    labelPolyespece.pack(pady=20)

    boutonMonoculture = tk.Button(fenetre, text="Dossier monoculture", command=parcourirDossierMonoculture)
    boutonMonoculture.pack(pady=20)

    boutonPolyespece = tk.Button(fenetre, text="Dossier polyespece", command=parcourirDossierPolyespece)
    boutonPolyespece.pack(pady=20)

    boutonConfirmation = tk.Button(fenetre, text="Confirmer", command=enregistrerChemin)
    boutonConfirmation.pack(pady=20)

    fenetre.mainloop()

def retireTropPetit(df, critere, tailleMin) :
    tmpDf = df[df[critere] > tailleMin] 
    return tmpDf

main()


