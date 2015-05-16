#!/usr/bin/python3
#
#    <one line to give the program's name and a brief idea of what it does.>
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

import csv

# TODO use UIF for Swimmer and structure

def createDatabase(con):
    """
    Crée la structure de la base pour conserver les résultats.
    
    """
    
    cur = con.cursor()

    # Table des nageurs
    cur.execute("CREATE TABLE IF NOT EXISTS Swimmers(Id INTEGER PRIMARY KEY AUTOINCREMENT, LastName TEXT, FirstName TEXT, Country TEXT DEFAULT 'FRA', Year INTEGER, Gender CHAR, Structure TEXT)")
    #cur.execute("CREATE TABLE IF NOT EXISTS Swimmers(Id INTEGER PRIMARY KEY AUTOINCREMENT, LastName TEXT, FirstName TEXT, Nation TEXT DEFAULT 'FRA', BirthDate DATE, Gender CHAR, IdClub INTEGER)")

    # Table des résultats des courses par nageurs
#    cur.execute("CREATE TABLE IF NOT EXISTS Temps(Id INTEGER PRIMARY KEY AUTOINCREMENT, IdSwimmer INTEGER, IdTrial INTEGER, Time TEXT, Point INTEGER, Relay BOOLEAN DEFAULT False, Date DATE, Location TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS Times(Id INTEGER PRIMARY KEY AUTOINCREMENT, IdSwimmer INTEGER, IdCompetition INTEGER, IdTrial INTEGER, Time FLOAT, Point INTEGER, Relay BOOLEAN DEFAULT False)")
    # Table des épreuves existantes, renseignée à la création de la base
    cur.execute("CREATE TABLE IF NOT EXISTS Trials(Id INTEGER PRIMARY KEY, Length Integer, Swim TEXT, Gender CHAR)")
    # Table de la compétition. Manque le lien vers les épreuves réalisée dans cette compétition
    #cur.execute("CREATE TABLE IF NOT EXISTS Competitions(Id INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Date DATE,  IdPool INTEGER NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS Competitions(Id INTEGER PRIMARY KEY, Name TEXT, Date DATE,  IdPool INTEGER NOT NULL)")
    cur.execute("CREATE TABLE IF NOT EXISTS CompetitionsTrials(Id INTEGER PRIMARY KEY AUTOINCREMENT, IdCompetition INTEGER, IdTrial INTEGER)")
    # Table des piscine. Possibilité d'ajouter l'adresse
    cur.execute("CREATE TABLE IF NOT EXISTS Pools(Id INTEGER PRIMARY KEY AUTOINCREMENT, Location TEXT, Length INTEGER)")
    
    # Table des clubs. Possibilité  d'ajouter l'adresse
    #cur.execute("CREATE TABLE IF NOT EXISTS Pools(Id INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT)
    
    ###
    cur.execute("CREATE VIEW IF NOT EXISTS Points AS SELECT Swimmers.LastName, Swimmers.FirstName, Swimmers.Structure, SUM(Times.Point) AS Total, COUNT(Times.Point) FROM Times,Swimmers WHERE Swimmers.Id=Times.IdSwimmer GROUP BY Swimmers.Id ORDER BY SUM(Times.Point) DESC")

    cur.execute("INSERT OR REPLACE INTO Trials VALUES"
        "(1, 50, 'NL', 'f'),        (51, 50, 'NL', 'h'),"
        "(2, 100, 'NL', 'f'),       (52, 100, 'NL', 'h'),"
        "(3, 200, 'NL', 'f'),       (53, 200, 'NL', 'h'),"
        "(4, 400, 'NL', 'f'),       (54, 400, 'NL', 'h'),"
        "(5, 800, 'NL', 'f'),       (55, 800, 'NL', 'h'),"
        "(6, 1500, 'NL', 'f'),      (56, 1500, 'NL', 'h'),"
        "(11, 50, 'dos', 'f'),      (61, 50, 'dos', 'h'),"
        "(12, 100, 'dos', 'f'),     (62, 100, 'dos', 'h'),"
        "(13, 200, 'dos', 'f'),     (63, 200, 'dos', 'h'),"
        "(21, 50, 'brasse', 'f'),   (71, 50, 'brasse', 'h'),"
        "(22, 100, 'brasse', 'f'),  (72, 100, 'brasse', 'h'),"
        "(23, 200, 'brasse', 'f'),  (73, 200, 'brasse', 'h')," 
        "(31, 50, 'pap', 'f'),      (81, 50, 'pap', 'h'),"
        "(32, 100, 'pap', 'f'),     (82, 100, 'pap', 'h'),"
        "(33, 200, 'pap', 'f'),     (83, 200, 'pap', 'h'),"
        "(40, 100, '4N', 'f'),      (90, 100, '4N', 'h'),"
        "(41, 200, '4N', 'f'),      (91, 200, '4N', 'h'),"
        "(42, 400, '4N', 'f'),      (92, 400, '4N', 'h')")

    cur.execute("CREATE VIEW IF NOT EXISTS Performances AS SELECT Swimmers.LastName, Swimmers.FirstName, Trials.Length, Trials.Swim, Times.Time, Times.Point FROM Times, Swimmers, Trials WHERE Swimmers.Id=Times.IdSwimmer AND Times.idTrial=Trials.id ORDER BY LastName, FirstName")
    
    cur.close()
    
    return;


def insertSwimmer(con, lastName, firstName, year, structure, gender, nationality=None):
    """
    Insère un nageur dans la base de données, et retourne son identifiant
    
    :param con: connexion à la base de donnée
    :param lastName: nom de famille du nageur
    :param firstName: prénom du nageur
    :param year: année de naissance du nageur
    :param structure: structure du nageur
    :param gender: genre du nageur
    :param nationality: nationalité du nageur
    :type lastName: string
    :type firstname: string
    :type year: int
    
    :return: identifiant du nageur
    :rtype: int
    """
    
    # TODO: UIF du nageurm et du club
    
    # chercher idNageur
    # si inexistant, inserer dans la base
    # retourner idNageur
    cur = con.cursor()
    
    cur.execute("SELECT Id FROM Swimmers WHERE LastName=? AND FirstName=? AND Year=? AND Structure=?", (lastName, firstName, year, structure))
    row = cur.fetchone()
    if row == None:
        if nationality == None:
            cur.execute("INSERT INTO Swimmers(LastName, FirstName, Year, Structure, Gender) VALUES (?,?,?,?,?)", (lastName, firstName, year, structure, gender))
        else:
            cur.execute("INSERT INTO Swimmers(LastName, FirstName, Year, Structure, Gender, Country) VALUES (?,?,?,?,?,?)", (lastName, firstName, year, structure, gender, nationality))
        con.commit()
        lid = cur.lastrowid
    else:
        lid = row[0]
        
    cur.close()

    return lid;

def insertCompetition(con, date, location, length):
    cur = con.cursor()
    
    # Vérifie si le bassin existe, sinon le crée
    cur.execute("SELECT Id FROM Pools WHERE Location=? AND Length=? ", (location, length))
    row = cur.fetchone()
    if row == None:
        cur.execute("INSERT INTO Pools(Location, Length) VALUES(?,?)", (location, length))
        lid = cur.lastrowid
    else:
        lid = row[0]
        
    ## Crée la compétition si nécessaire
    cur.execute("SELECT Id FROM Competitions WHERE IdPool=? AND Date=? ", (lid, date))
    row = cur.fetchone()
    if row == None:
        cur.execute("INSERT INTO Competitions(IdPool, Date) VALUES(?,?)", (lid, date))
        lid = cur.lastrowid
        con.commit()
    else:
        lid = row[0]
    
    cur.close()
    
    return lid;

def getIdTrial(con, length, swim, gender):
    """
    Retourne l'identifiant de l'épreuve
    
    :param con: connexion à la base de donnée
    :param length: distance de l'épreuve
    :param swim:
    :param gender:
    
    :return: identifiant de l'épreuve 
    """
    cur = con.cursor()
    cur.execute("SELECT Id FROM Trials WHERE Gender=? AND Length=? AND Swim=?", (genre, distance, nage))
    row = cur.fetchone()
    
    cur.close()
    
    if row == None:
        return None
        
    return row[0];

def existsIdCompetition(con, idCompetition):
    """
    Vérifie si une compétition a déjà été intégrée
    
    :param con: connexion à la base de données
    :param idCompetitiion: identifiant de la compétition
    :type idCompetition: int
    
    :return: vrai si la compétition a déjà été intégrée
    :rtype: boolean
    
    """
    
    cur = con.cursor()
    cur.execute("SELECT * FROM CompetitionsTrials WHERE IdCompetition=?", (idCompetition,))
    row = cur.fetchone()
    cur.close()
    
    if row == None:
        return False
    
    return True


def insertTrialInCompetition(con, idCompetition, idTrial):
    """
    Associe une épreuve à une compétition
    
    :param con: connexion à la base de données
    :param idCompetitiion: identifiant de la compétition
    :param idTrial: identifiant de l'épreuve
    :type idCompetition: int
    :type idTrial: int
    """
    cur = con.cursor()

    cur.execute("SELECT Id FROM CompetitionsTrials WHERE IdCompetition=? AND IdTrial=? ", (idCompetition, idTrial))
    row = cur.fetchone()
    if row == None:
        cur.execute("INSERT INTO CompetitionsTrials(IdCompetition, IdTrial) VALUES(?,?)", (idCompetition, idTrial))
    #    lid = cur.lastrowid
    #else:
    #    lid = row[0]
        
        con.commit()
    
    cur.close()
    
    #return lid;
    return;

def insertBestPerformance(con, idSwimmer, idCompetition, idtrial, time, point, relais = False):
    # MaJ idNageur...
    """
    Insére/Conserve pour un nageur sa meilleure performance pour un type d'épreuve
    
    :param con: connection à la base de données
    :param idSwimmer: identifiant du nageur
    :param idCompetition: identifiant de la compétition
    :param idTrial: identifiqnt de l'épreuve
    :param time: temps
    :param point: nombre de point correspondant au temps
    
    :type idSwimmer: int
    :type idCompetition: int
    :type idTrial: int
    :type time: float
    :type point: int
    
    """
    
    cur = con.cursor()

    cur.execute("SELECT Id, Time FROM Times WHERE IdSwimmer=? AND IdTrial=?", (idSwimmer, idtrial))
    row = cur.fetchone()
    if row == None:
        cur.execute("INSERT INTO Times(IdSwimmer, IdCompetition, IdTrial, Time, Point, Relay) VALUES (?,?,?,?,?,?)", (idSwimmer, idCompetition, idtrial, time, point, relais))
    else:
        if row[1] > time:
            cur.execute("UPDATE Times SET IdCompetition=?, Time=?, Point=?, Relay=? WHERE Id=?", (idCompetition, time, point, relais, row[0]))
    
    con.commit()
    
    cur.close()
    
    return;

def exportTableInCSV(con, table):
    cursor = con.cursor()
    
    request = "SELECT * FROM {}".format(table)
    cursor.execute(request)

    filename = "{}.csv".format(table)
    with open(filename, "w") as csv_file:
        csv_writer = csv.writer(csv_file, dialect='excel', delimiter=';')
        csv_writer.writerow([i[0] for i in cursor.description]) # write headers
        csv_writer.writerows(cursor)

    cursor.close()
        
    return;
