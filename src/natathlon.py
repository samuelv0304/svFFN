#!/usr/bin/env python3
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

from svFFN import AnalyzeWebFFN, SwimmingDb, miscFFN
import sqlite3 as lite

import argparse

import csv
import ezodf
import sys

def saveRanking(connection, filename):
        """
        Enregistre dans un fichier au format ODS les performances des nageurs, et 
        crée des onglets avec le classement actuel et prévisionnel.
    
        :param connection:
        :param filename: nom du fichier à enregistrer
        :type filename: str
        """

        ods=ezodf.newdoc(doctype="ods", filename=filename)
        ods.inject_style("""<style:style style:name="Titre" style:family="table-cell"><style:table-cell-properties style:text-align-source="fix" style:repeat-content="false" fo:wrap-option="wrap" style:vertical-align="middle" style:vertical-justify="auto"/><style:paragraph-properties fo:text-align="center" fo:margin-left="0mm"/><style:text-properties style:font-name="Titre" fo:font-family="Titre" fo:font-weight="bold" style:font-name-asian="Arial Unicode MS" style:font-family-asian="'Arial Unicode MS'" style:font-family-generic-asian="system" style:font-pitch-asian="variable" style:font-weight-asian="bold" style:font-name-complex="Arial Unicode MS" style:font-family-complex="'Arial Unicode MS'" style:font-family-generic-complex="system" style:font-pitch-complex="variable" style:font-weight-complex="bold"/></style:style>""")
        #ods.inject_style("""<style:style style:name="Titre" style:family="table-cell"><style:table-cell-properties style:text-align-source="fix" style:repeat-content="false" fo:wrap-option="wrap" style:vertical-align="middle" loext:vertical-justify="auto"/><style:paragraph-properties fo:text-align="center" fo:margin-left="0mm"/><style:text-properties style:font-name="Titre" fo:font-family="Titre" fo:font-weight="bold" style:font-name-asian="Arial Unicode MS" style:font-family-asian="'Arial Unicode MS'" style:font-family-generic-asian="system" style:font-pitch-asian="variable" style:font-weight-asian="bold" style:font-name-complex="Arial Unicode MS" style:font-family-complex="'Arial Unicode MS'" style:font-family-generic-complex="system" style:font-pitch-complex="variable" style:font-weight-complex="bold"/></style:style>""")

        sheet = createSheetfromTable(connection, 'NatathlonF')
        ods.sheets.append(sheet)
        sheet = createRankingSheet('ClassementF', 'NatathlonF', sheet.nrows())
        ods.sheets.insert(0, sheet)

        sheet = createSheetfromTable(connection, 'NatathlonH')
        ods.sheets.append(sheet)
        sheet = createRankingSheet('ClassementH', 'NatathlonH', sheet.nrows())
        ods.sheets.insert(1, sheet)
        
        sheet = createSheetFromRequest(connection, "Competitions", "SELECT c.Id, c.Date, p.Location FROM Competitions c, Pools p WHERE p.Id = c.IdPool")
        ods.sheets.append(sheet)
        
        ods.save()

def createSheetFromRequest(connection, name, request):
    """
    """
    cursor = connection.cursor()

    cursor.execute(request)

    sheet = ezodf.Table(name, (10, len(cursor.description)))

    line = 0
    for (i,tc) in zip(cursor.description, sheet.row(line)):
            tc.set_value(i[0])
            
    line += 1
    for row in cursor:
            for (val, tc) in zip(row, sheet.row(line)):
                    tc.set_value(val)
            line += 1
            
            if line == sheet.nrows():
                sheet.append_rows(10)
            
    cursor.close()

    return sheet

def createSheetfromTable(connection, tablename):
        """
        """
        request = "SELECT * FROM {}".format(tablename)
        return createSheetFromRequest(connection, tablename, request)

headers = ['Nom', 'Prénom', 'Structure', 'Nb de points', 'Nb de course', 'Prévision nb de points']
contents = ['={}.A{}', '={}.B{}', '={}.C{}'] # name, first name, structure
contents2 = ['=SUM(sheet.F2;sheet.H2;sheet.J2;sheet.L2;sheet.N2;sheet.P2;sheet.R2;sheet.T2;sheet.V2;sheet.X2)',
             '=COUNTIF((sheet.F2~sheet.H2~sheet.J2~sheet.L2~sheet.N2~sheet.P2~sheet.R2~sheet.T2~sheet.V2~sheet.X2);">0")',
             '=IF(AND(E2<10;E2>5);ROUNDDOWN(D2+D2/E2*(10-E2));D2)']

def createRankingSheet(sheetname, datasheetname, nrows = 10):
    sheet = ezodf.Table(sheetname) #6, nrows

    for (h, c) in zip(headers, sheet.row(0)):
        c.set_value(h)
        c.style_name = 'Titre'

    for row in range(2, nrows):
        if row >= sheet.nrows():
            sheet.append_rows(10)

        iterator = sheet.row(row-1).__iter__()
        for c in contents:
            tc = next(iterator)
            formula = c.format(datasheetname, row)
            tc.formula = formula

        for c in contents2:
            tc = next(iterator)
            formula = c.replace('2', str(row)).replace('sheet', datasheetname)
            tc.formula = formula           

    return sheet;

def createNatathlonView(con, gender):
    cur = con.cursor()

    eprs = [32, 33, 12, 13, 22, 23, 2, 3, 42, 5]
    if gender == 'h':
        test = '>'
    else:
        test = '<'
    
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
    chunks.append("FROM Swimmers n JOIN Times t ON t.idSwimmer=n.Id WHERE n.Gender='{}' AND t.idTrial{}50 ".format(gender, test))
    chunks.append("GROUP BY n.LastName, n.FirstName, n.Structure ")
    chunks.append("ORDER BY Total DESC LIMIT 200")
    request = ''.join(chunks)
    cur.execute(request)
    
    cur.close()
    
    return;

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

    # Do not insert a competition, if there are no race
    ideprs = AnalyzeWebFFN.findIdEprForCompetition(idcpt)
    if len(ideprs) == 0:
        print("Compétition non remontée sur le serveur")
        return

    competition = AnalyzeWebFFN.getDescForCompetition(idcpt)
    SwimmingDb.insertCompetition(connection, competition['date'], competition['location'], competition['length'], idcpt)
    
    #ideprs = AnalyzeWebFFN.findIdEprForCompetition(idcpt)

    progress = 0.;
    for idepr in ideprs:
        SwimmingDb.insertTrialInCompetition(connection, idcpt, idepr)
        results = AnalyzeWebFFN.getSiteResultsOfTrial(miscFFN.departements[93], idcpt, idepr)
        #results = AnalyzeWebFFN.getResultsOfTrial(idcpt, idepr)
        if idepr > 50:
            gender = 'h' 
        else:
            gender = 'f'
        for result in results:
            idSwimmer = SwimmingDb.insertSwimmer(connection, result[0], result[1], result[2], result[4], gender, result[3])
            SwimmingDb.insertBestPerformance(connection, idSwimmer, idcpt, idepr, result[5], result[6])
        progress += 1
        miscFFN.update_progress(progress/len(ideprs))

def _princDepartement(connection, season, dep, desc, update=False):
    print("Département: {}".format(miscFFN.departements[dep]))

    idcpts = AnalyzeWebFFN.findSiteIdCptByType(miscFFN.departements[dep], season, desc)
    for idcpt in idcpts:
        _insertCompetition(connection, idcpt, update)
    
def _princRegion(connection, season, reg, desc, update=False):
    print("Régions: {}".format(miscFFN.regions[reg]))

    idcpts = AnalyzeWebFFN.findSiteIdCptByType(miscFFN.regions[reg], season, desc)
    for idcpt in idcpts:
        _insertCompetition(connection, idcpt, update)
        
def _princFichier(connection, filename, update=False):
    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file, dialect='excel')
        for row in csv_reader:
            print("Zone: {}".format(row[0]))
            row.pop(0)
            for idcpt in row:
                _insertCompetition(connection, (int)(idcpt), update)

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
    parser.add_argument('-c', '--competitions', required=False, type=str, help='nom du fichier contenant les identifiants des compétitions à insérer. Un identifiant par ligne.')
    parser.add_argument('-b', '--base', required=False, type=str, help='nom de la base de donnée.')
    parser.add_argument('-u', '--update', required=False, action='store_true', help='insére uniquement les performances des compétitions non encore insérées')
    parser.add_argument('-f', '--fichier', required=False, type=str, help='nom du fichier ou enregistrer les classements.')    
    
    args = parser.parse_args()
    
    season = miscFFN.current_season()
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

        #desc = '^type : natathlon.*(12-13).*'
        desc = 'natathlon.*(12-13).*'
        if args.departement == 0:
            for dep in miscFFN.departements:
                _princDepartement(connection, args.saison, dep, desc, args.update)
        elif args.departement and args.departement > 0:
             _princDepartement(connection, args.saison, args.departement, desc, args.update)
        if args.region == 0:
            for reg in miscFFN.regions:
                _princRegion(connection, args.saison, reg, desc, args.update)
        elif args.region and args.region > 0:
            _princRegion(connection, args.saison, args.region, desc, args.update)
        if args.idcpt and args.idcpt > 0:
            _insertCompetition(connection, args.idcpt, args.update)
        if args.competitions:
            _princFichier(connection, args.competitions, args.update)

        if args.fichier == None:
                args.fichier = 'natathlon-{}.ods'.format(args.saison)
        saveRanking(connection, args.fichier)
    
    except lite.Error as e:

        print("Error:", e.args[0])
        sys.exit(1)

    finally:

        if connection:
            connection.close()
