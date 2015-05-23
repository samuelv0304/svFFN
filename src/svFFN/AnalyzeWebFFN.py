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

from lxml import html
import requests

import csv
import urllib.request
import codecs

import svFFN.miscFFN

def findSiteIdCptByName(site, season, name):
    """
    Recherche dans le site indiqué toutes les compétitions portant le nom indiqué et retourne la liste des identifiants de ces compétitions.
    
    :param site: nom du département ou de la région sur laquelle faire la recherche
    :param season: saison
    :param name: nom des compétitions recherchées, une regexp est autorisée
    :type site: string
    :type season: int
    :type name: string
    :return: liste d'identifiant de compétition
    :rtype: list
    """
    idcpt = []
    
    url = 'http://{}.ffnatation.fr/script/nat_compets.php?idsai={}'.format(site, season)
    page = requests.get(url)
    tree = html.fromstring(page.text)
    
    # This will create a list of results: Nom des compétitions
    regexpNS = "http://exslt.org/regular-expressions"
    regexp="//table/tr/td/div/a[@href][re:test(., '{}', 'i')]".format(name)
    rows = tree.xpath(regexp, namespaces={'re':regexpNS}) # Nom des compétitions
    for row in rows:
        idcpt.append(row.attrib['href'].split('=')[-1])
    
    return idcpt;

def findDepIdCptByName(season, dep, name):
    """
    [DEPRECATED]
    Recherche dans le département indiqué toutes les compétitions portant le nom indiqué et retourne la liste des identifiants de ces compétitions.
    
    :param season: saison
    :param dep: numéro du département
    :param name: nom des compétitions recherchées, une regexp est autorisée
    :type season: int
    :type dep: int
    :type name: string
    :return: liste d'identifiant de compétition
    :rtype: list
    """
    
    return findSiteIdCptByName(miscFFN.departements[dep], season, name)

def findRegIdCptByName(season, reg, name):
    """
    [DEPRECATED]
    Recherche dans le département indiqué toutes les compétitions portant le nom indiqué et retourne la liste des identifiants de ces compétitions.
    
    :param season: saison
    :param dep: numéro du département
    :param name: nom des compétitions recherchées, une regexp est autorisée
    :type season: int
    :type dep: int
    :type name: string
    :return: liste d'identifiant de compétition
    :rtype: list
    """
    
    return findSiteIdCptByName(miscFFN.regions[reg], season, name)

def getResultsOfCompetitionFromCSV(season, dep, idcpt, removeFirstLine = True):
    """
    Récupère l'ensemble des résultats d'une compétition
    
    :param season: saison concernée de l'épreuve
    :param dep: département concerné
    :param idcpt: numéro de la compétition
    :param removeFirstLine: supprime ou non la premiére ligne du fichier CSV, qui peut contenir le titre
    :type season: int
    :type dep: int
    :type idcpt: int
    
    :return: liste (distance, nage, nom, prénom, club, année de naissance, sexe, temps, date de la compétition)
    :rtype: list 
    
    """
    results = []
    
    url = 'http://{}.ffnatation.fr/script/nat_results_csv.php?idcpt={}'.format(miscFFN.departements[dep], idcpt)
        
    stream = urllib.request.urlopen(url)
    csvfile = csv.reader(codecs.iterdecode(stream, 'iso-8859-1'), delimiter=';') # utf-8
    for line in csvfile:
    #    #insertSwimmer(con, line[2], line[3], line[5], line[4], line[6])
        epr = line.pop(0).partition(" ") # analyser l'épreuve au format : "dist nage genre"
        line.pop(0) # supprime format d'épreuve
        line.insert(0, epr[2].rpartition(" ")[0]) # nage
        line.insert(0, epr[0]) # distance
        results.append(line)

    if (removeFirstLine):
        results.pop(0)

    return results;

def _getElementText(element):
    if element.text != None:
        return element.text
    
    text = element.xpath("*/text()")
    if len(text) >= 1:
        return text[0]

    return None

def getResultsOfTrial(idcpt, idTrial):
    """
    Retourne les nageurs et leur résultat au cours d'une épreuve d'une compétition

    :param idcpt: identifiant compétition
    :param idTrial: identifiant épreuve
    
    :type idcpt:int
    :type idTrial: int
    
    :return: list of results (name, first name, year of birth, nationality, structure, time, point)
    """
    results = []

    url = 'http://ffn.extranat.fr/webffn/resultats.php?idcpt={}&idepr={}'.format(idcpt, idTrial)
    page = requests.get(url)
    tree = html.fromstring(page.text)
    
    #This will create a list of results:
    rows = tree.xpath('//div[@id="containerMain"]//table/tr/td[@class="tabColPts"][contains(text(),"pts")]/parent::*')
    for row in rows:
        # Use tabColInd, tabColNai, tabColNat, tabColStr, tabColTps, tabColPts
        result = []
        for element in row.iterchildren():
            value = element.get('class')
            if value == 'tabColInd':
                identifiant = _getElementText(element)
                # Check nationality
                identifiants = identifiant.split('/')
                nationality = None
                if len(identifiants) > 1:
                    nationality = identifiants[1].strip()

                identifiant = identifiants[0]
                identifiants = identifiant.split()
                name = identifiants[0]
                for index in range(len(identifiants)-3):
                    name += ' ' + identifiants[1+index]
                firstName = identifiants[-2]
                year = identifiants[-1].strip('()')
                result.append(name)
                result.append(firstName)
                result.append(year)
                result.append(nationality)
            elif value == 'tabColStr':
                structure = _getElementText(element)
                result.append(structure.split('[')[0].strip())
            elif value == 'tabColTps':
                times = _getElementText(element)
                result.append(float(times.replace('.', '').replace(':','.')))
            elif value == 'tabColPts':
                points = _getElementText(element)
                result.append(int(points.split(' ')[0]))

        results.append(result)

    return results;

def findIdEprForCompetition(idcpt):
    """
    Retourne la liste des épreuves de la compétition
    
    :param url: numéro du département
    :type url: string
    
    :return: liste des épreuves
    :rtype: list
    """
    
    results = []
    
    url = 'http://ffn.extranat.fr/webffn/resultats.php?idcpt={}'.format(idcpt)
    page = requests.get(url)
    tree = html.fromstring(page.text)
    
    # This will create a list of trials.
    rows = tree.xpath('//div[@id="containerMain"]//table/tr/td/select[@class="listeEpreuve"]/option/@value')
    # Absence de menu déroulant avec les épreuves
    if len(rows) > 0:
        for row in rows:
            parameters = row.split('&')
            for parameter in parameters:
                if parameter.startswith('idepr='):
                    results.append(int(parameter[6:]))
    else:
        codeNage = {'Nage' : 0, 'Dos' : 10, 'Brasse' : 20, 'Papillon' : 30}
        codeDist = {50 : 1, 100 : 2, 200 : 3, 400 : 4, 800 : 5, 1500 : 6}
        code4N = {100 : 40, 200 : 41, 400 : 42}
        # Analyse page Femme (idsex=2) et Homme (idsex=1)
        for sex in range(1,3):
            urlSex = '{}&idsex={}'.format(url, sex)

            page = requests.get(urlSex)
            tree = html.fromstring(page.text)
            
            idsex = (2-sex)*50
        
            rows = tree.xpath('//div[@id="containerMain"]//table/tr/td/div[@class="tabColInsertTextLeft"]')
            for row in rows:
                params = row.text.split(' ')
                if params[1][0] == '4':
                    idepr = idsex + code4N[int(params[0])]
                else:
                    idepr = idsex + codeDist[int(params[0])] + codeNage[params[1]]
                results.append(int(idepr))

    return results;

def getSiteResultsOfTrial(site, idcpt, idTrial):
    """
    [DEPRECATED]
    Retourne les nageurs et leur résultat au cours d'une épreuve d'une compétition
    
    :param site: nom du département ou de la région
    :param idcpt: identifiant compétition
    :param idTrial: identifiant épreuve
    
    :type site: string
    :type idcpt:int
    :type idTrial: int
    
    :return: list of results (name, first name, year of birth, nationality, structure, time, point)
    """
    results = []
    
    url = 'http://{}.ffnatation.fr/script/nat_results.php?idcpt={}&idepr={}'.format(site, idcpt, idTrial)
    page = requests.get(url)
    tree = html.fromstring(page.text)
    
    #This will create a list of results:
    rows = tree.xpath('//table/tr/td[@class="tabColPla"]/parent::*')
    for row in rows:
        # Use tabColInd, tabColNai, tabColNat, tabColStr, tabColTps, tabColPts
        result = []
        for element in row.itertext(with_tail=False):
            result.append(element)

        # Les disqualifiés et forfait ne sont pas pris en compte
        if len(result) < 8:
            continue

        nresult = []
        identifiant = result[2].split(' ') # Nom Prénom

        name = identifiant[0]
        for index in range(len(identifiant)-2):
            name += ' ' + identifiant[1+index]
        nresult.append(name) # Nom
        
        nresult.append(identifiant[-1]) # Prénom

        nresult.append(int(result[3])) # Année de naissance
        nresult.append(result[4]) # Nationalité
        nresult.append(result[5]) # Structure
        
        nresult.append(float(result[6].replace('.', '').replace(':','.'))) # temps
        nresult.append(int(result[7].split(' ')[0])) # points

        results.append(nresult)
    
    return results;
  
def findSiteIdEprForCompetition(site, idcpt):
    """
    [DEPRECATED]
    Retourne la liste des épreuves de la compétition
    
    :param site: nom du département ou de la région
    :param idcpt: numéro de la compétition
    :type site: string
    :type idcpt: int
    
    :return: liste des épreuves
    :rtype: list
    """    
    results = []
    
    url = 'http://{}.ffnatation.fr/script/nat_results.php?idcpt={}'.format(site, idcpt)
    page = requests.get(url)
    tree = html.fromstring(page.text)
    
    # This will create a list of trials.
    rows = tree.xpath('//div[@id="frameContent"]//table/tr/td/select[@class="listeEpreuve"]/option/@value')
    # Absence de menu déroulant avec les épreuves
    if len(rows) > 0:
        for row in rows:
            parameters = row.split('&')
            for parameter in parameters:
                if parameter.startswith('idepr='):
                    results.append(int(parameter[6:]))
    else:
        codeNage = {'Nage' : 0, 'Dos' : 10, 'Brasse' : 20, 'Papillon' : 30}
        codeDist = {50 : 1, 100 : 2, 200 : 3, 400 : 4, 800 : 5, 1500 : 6}
        code4N = {100 : 40, 200 : 41, 400 : 42}
        # Analyse page Femme (idsex=2) et Homme (idsex=1)
        for sex in range(1,3):
            urlSex = '{}&idsex={}'.format(url, sex)
            page = requests.get(urlSex)
            tree = html.fromstring(page.text)
            
            idsex = (2-sex)*50
        
            rows = tree.xpath('//div[@id="frameContent"]//table/tr/td/div[@class="tabColInsertTextLeft"]')
            for row in rows:
                params = row.text.split(' ')
                if params[1][0] == '4':
                    idepr = code4N[int(params[0])]
                else:
                    idepr = idsex + codeDist[int(params[0])] + codeNage[params[1]]
                results.append(int(idepr))

    return results;
    
def findRegIdEprForCompetition(reg, idcpt):
    """
    [DEPRECATED]
    Retourne la liste des épreuves de la compétition
    
    :param reg: numéro de la région
    :param idcpt: numéro de la compétition
    :type dep: int
    :type idcpt: int
    
    :return: liste des épreuves
    :rtype: list
    """    
    return findSiteIdEprForCompetition(miscFFN.regions[reg], idcpt)
