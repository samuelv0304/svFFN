#!/usr/bin/python3
#
#    Analyze and extract the information from the FFN web site
#    Copyright (C) 2015  samuelv0304@gmail.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import sys

# 11 not exist
regions = { 1 : "Alsace",  2 : "Aquitaine", 3 : "Auvergne", 4 : "Bourgogne", 5 : "Bretagne", 
6 : "Centre", 7 : "ChampagneArdenne", 8 : "Corse", 9 : "CotedAzur", 12 : "FrancheComte",
 13 : "IledeFrance", 14 : "LanguedocRoussillon", 15 : "Limousin", 16 : "Lorraine", 
 18 : "NordpasdeCalais", 19 : "Normandie", 20 : "PaysdelaLoire", 21 : "Picardie", 
 22 : "PoitouCharentes", 23 : "Provence", 24 : "MidiPyrenees", 25 : "NouvelleCaledonie", 
 26 : "Guadeloupe", 27 : "Martinique", 28 : "Guyane", 29 : "LaReunion"}
 

regions_orphelines = { 10 : "Dauphine", 17 : "Lyonnais" }

# 20 not exist
departements = { 2 : "aisne", 6 : "alpesmaritimes", 8 : "ardennes", 9 : "ariege", 10 : "aube", 11 :
"aude", 12 : "aveyron", 14 : "calvados", 16 : "charente", 17 : "charentemaritime", 18 : "cher", 19 :
"correze", 21 : "cotedor", 23 : "Creuse", 25 : "Doubs", 26 : "Drome", 27 : "Eure", 29 : "Finistere", 30
: "Gard", 31 : "Hautegaronne", 32 : "Gers", 33 : "Gironde", 34 : "Herault", 35 : "IlleetVilaine", 36 :
"Indre", 37 : "IndreetLoire", 38 : "Isere", 40 : "Landes", 41 : "LoiretCher", 43 : "HauteLoire", 44 :
"LoireAtlantique", 45 : "Loiret", 46 : "Lot", 49 : "MaineEtLoire", 50 : "Manche", 51 : "Marne", 52 :
"HauteMarne", 53 : "Mayenne", 54 : "MeurtheEtMoselle", 55 : "Meuse", 56 : "Morbihan", 57 : "Moselle", 58
: "Nievre", 60 : "Oise", 61 : "Orne", 62 : "PasDeCalais", 63 : "PuyDeDome", 65 : "HautesPyrenees", 66 :
"PyreneesOrientales", 67 : "BasRhin", 68 : "HautRhin", 71 : "SaoneEtLoire", 72 : "Sarthe", 75 : "Paris",
76 : "SeineMaritime", 77 : "SeineEtMarne", 78 : "Yvelines", 79 : "DeuxSevres", 80 : "Somme", 81 :
"Tarn", 83 : "Var", 85 : "Vendee", 86 : "Vienne", 87 : "HauteVienne", 88 : "Vosges", 89 : "Yonne", 91 :
"Essonne", 92 : "HautsDeSeine", 93 : "SeineSaintDenis", 94 : "ValDeMarne", 95 : "ValdOise"}

departements_orphelins = { 1 : "ain", 3 : "allier", 4 : "alpesDeProvence", 5 : "hautesAlpes", 7 : "ardeche", 
13 : "bouchesDuRhone", 15 : "cantal", '2A' : "corseDuSud", '2B' : "corseDuNord", 22 : "cotesdArmor", 
24 : "Dordogne", 28 : "eureEtLoir", 39 : "jura", 42 : "Loire", 47 : "lotEtGaronne", 48 : "lozere", 
59 : "Nord", 64 : "pyreneesAtlantique", 69 : "Rhone", 70 : "Saone", 73 : "Savoie", 74 : "HauteSavoie", 
82 : "TarnEtGaronne", 84 : "vaucluse", 90 : "TerritoireDeBelfort"}

def current_season():
    """
    Retourne la saison courante
    """
    now = datetime.date.today()
    season = now.year
    if now.month >= 9:
        season += 1
        
    return season

# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1:.1f}% {2}".format( "="*block + " "*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()
