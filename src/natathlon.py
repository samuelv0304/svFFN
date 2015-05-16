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

from svFFN import AnalyzeWebFFN, SwimmingDb
import sqlite3 as lite

import argparse
import sys
import datetime

import csv

def createNatathlonView(con, gender):
    cur = con.cursor()

    eprs = [32, 33, 12, 13, 22, 23, 2, 3, 42, 5]
    
    # From the python FAQ: What is the most efficient way to concatenate many strings together?
    # http://docs.python.org/py3k/faq/programming.html#what-is-the-most-efficient-way-to-concatenate-many-strings-together
    chunks = []
    chunks.append("CREATE VIEW IF NOT EXISTS Natathlon{} AS ".format(gender.upper()))
    chunks.append("SELECT n.LastName, n.FirstName, n.Structure, ")
    chunks.append("SUM(t.Point) Total ")
    for epr in eprs:
        if gender == 'h':
            epr += 50
        cur.execute("SELECT Length, Swim FROM Trials WHERE Id = ?", (epr,))
        row = cur.fetchone()
        if row == None:
            continue
        chunks.append(", sum(case when t.idTrial = {} then t.Time else '' end) Time{}{} ".format(epr, row[0], row[1]))
        chunks.append(", sum(case when t.idTrial = {} then t.Point else 0 end) Point{}{} ".format(epr, row[0], row[1]))
    chunks.append("FROM Swimmers n JOIN Times t ON t.idSwimmer=n.Id WHERE n.Gender='{}' ".format(gender))
    chunks.append("GROUP BY n.LastName, n.FirstName, n.Structure ")
    chunks.append("ORDER BY Total DESC LIMIT 200")
    request = ''.join(chunks)
    cur.execute(request)
    
    cur.close()
    
    return;

# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def _update_progress(progress):
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

def _insertCompetition(connection, idcpt, update=False):
    """
    Intègre dans la base de données une compétition
    
    :param connection: connexion à la base de données
    :param idcpt: identifiant de la compétition
    :apram update: 
    :type idcpt: int
    :type update: boolean
    """

    print("Competition : {0}".format(idcpt))
    # Vérifie si la compétition a déjà été insérée
    if not update and SwimmingDb.existsIdCompetition(connection, idcpt):
        print("Déjà intégrée")
        return

    #SwimmingDb.insertCompetition(connection, idcpt, date, colonnes[-3], args.bassin)
    ideprs = AnalyzeWebFFN.findIdEprForCompetition(idcpt)

    progress = 0.;
    _update_progress(progress)
    for idepr in ideprs:
        SwimmingDb.insertTrialInCompetition(connection, idcpt, idepr)
        results = AnalyzeWebFFN.getSiteResultsOfTrial(AnalyzeWebFFN.departements[93], idcpt, idepr)
        #results = AnalyzeWebFFN.getResultsOfTrial(idcpt, idepr)
        if idepr > 50:
            gender = 'h' 
        else:
            gender = 'f'
        for result in results:
            idSwimmer = SwimmingDb.insertSwimmer(connection, result[0], result[1], result[2], result[4], gender, result[3])
            SwimmingDb.insertBestPerformance(connection, idSwimmer, idcpt, idepr, result[5], result[6])
        progress += 1
        _update_progress(progress/len(ideprs))

def _princDepartement(connection, season, dep, desc, update=False):
    print("Département: {}".format(AnalyzeWebFFN.departements[dep]))

    idcpts = AnalyzeWebFFN.findSiteIdCptByName(AnalyzeWebFFN.departements[dep], season, desc)
    for idcpt in idcpts:
        _insertCompetition(connection, idcpt, update)
    
def _princRegion(connection, season, reg, desc, update=False):
    print("Régions: {}".format(AnalyzeWebFFN.regions[reg]))

    idcpts = AnalyzeWebFFN.findSiteIdCptByName(AnalyzeWebFFN.regions[reg], season, desc)
    for idcpt in idcpts:
        _insertCompetition(connection, idcpt, update)
        
def _princFichier(connection, filename, update=False):
    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file, dialect='excel')
        for row in csv_reader:
            for idcpt in row:
                _insertCompetition(connection, (int)(idcpt), update)

def _currentSeason():
    """
    Retourne la saison courante
    """
    now = datetime.date.today()
    season = now.year
    if now.month >= 9:
        season += 1
        
    return season
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=
    "Récupère les performances des nageurs lors des épreuves du Natathlon à " \
    "partir du site de FFN pour les stocker dans une base de données. Exporte " \
    "le classement du Natathlon au format CSV. Attention la méthode de nommage " \
    "des natathlon de 2007 à aujourd'hui n'est pas constant.")
    parser.add_argument('-s', '--saison', required=False, type=int, help='supèrieur à 2001, et au plus égal à la saison courante. Par défaut saison courante.')
    parser.add_argument('-d', '--departement', required=False, nargs='?', const=0, type=int, help='numéro du département. Sans paramètre, tous les départements sont insérés.')
    parser.add_argument('-r', '--region', required=False, nargs='?', const=0, type=int, help='numéro de la région. Sans paramètre, toutes les régions sont insérées.')
    parser.add_argument('-i', '--idcpt', required=False, type=int, help='identifiant de la compétition à intégrer.')
    parser.add_argument('-f', '--fichier', required=False, type=str, help='nom du fichier contenant les identifiants des compétitions à insérer. Un identifiant par ligne.')
    parser.add_argument('-b', '--base', required=False, type=str, help='nom de la base de donnée.')
    parser.add_argument('-u', '--update', required=False, action='store_true', help='insére uniquement les performances des compétitions non encore insérées')
    
    args = parser.parse_args()
    
    season = _currentSeason()
    if args.saison == None:
        args.saison = season
    elif args.saison < 2002 or args.saison > season:
    	print('Le paramètre saison doit être supèrieur à 2001, et au plus égal à la saison courante ', season) 
    	sys.exit(1)

    dbName = 'natathlon-{}.sqlite'.format(args.saison)
    if args.base != None:
        dbName = args.base
    connection = None
    try:
        connection = lite.connect(dbName)
        connection.text_factory = str
    
        SwimmingDb.createDatabase(connection)
        createNatathlonView(connection, 'f')
        createNatathlonView(connection, 'h')

        desc = '^natathlon.*(12-13).*'
        if args.departement == 0:
            for dep in AnalyzeWebFFN.departements:
                _princDepartement(connection, args.saison, dep, desc, args.update)
        elif args.departement and args.departement > 0:
             _princDepartement(connection, args.saison, args.departement, desc, args.update)
        if args.region == 0:
            for reg in AnalyzeWebFFN.regions:
                _princRegion(connection, args.saison, reg, desc, args.update)
        elif args.region and args.region > 0:
            _princRegion(connection, args.saison, args.region, desc, args.update)
        if args.idcpt and args.idcpt > 0:
            _insertCompetition(connection, args.idcpt, args.update)
        if args.fichier:
            _princFichier(connection, args.fichier, args.update)
            
        SwimmingDb.exportTableInCSV(connection, 'NatathlonF')
        SwimmingDb.exportTableInCSV(connection, 'NatathlonH')
    
    except lite.Error as e:

        print("Error:", e.args[0])
        sys.exit(1)

    finally:

        if connection:
            connection.close()
