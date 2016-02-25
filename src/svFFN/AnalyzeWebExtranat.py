#!/usr/bin/env python3
#
#    Analyze and extract the information from the Extranat web site
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

import requests
from lxml import html

def initSession(username, password):
    """
    Initialise une session web sur le site extranat en tant qu'admin
    
    :param username: identifiant sur le serveur extranat
    :param password: mot de passe du compte identifiant
    :type username: str
    :type password: str
    
    :return: session
    """
    headers = {'User-Agent': 'Mozilla/5.0'}
    url = 'https://www.extranat.fr/cgi-bin/login.php'
    
    session = requests.session()
    session.headers.update(headers)
    
    r = session.get(url)
    if r.status_code != 200:
        print("Error code:{}".format(r.status_code))
        return None

    #cookies = dict(licence=r.cookies['licence'])
        
    # did this for first to get the cookies from the page, stored them with next line:
    #cookies = requests.utils.cookiejar_from_dict(requests.utils.dict_from_cookiejar(session.cookies))
    
    tree = html.fromstring(r.text)
    rows = tree.xpath('//form/div/div/input[@name="time"]')
    if rows == None or len(rows) != 1:
        print("Error: malformed page, time value is not present")
        return None
    time = rows[0].value

    values = { 'time': int(time), 'login': username, 'profil': 23, 'passwd': password , 'envoi' : ''}

    url = '{0}?'.format(url)
    #r = session.post(url,data=values,cookies =cookies)
    r = session.post(url,data=values)
    # enctype="multipart/form-data"
    # form name="login"
    # input type="hidden" name="time"
    # input name="login" type="text
    # input name="profil" 23
    # input name="passwd" type="password"
    # input name="envoi" type="submit"
    if r.status_code != 200:
        print("Error code (login):{}".format(r.status_code))
        return None
        
    return session

def _findSiteIdCptByName(session, season, site, name):
    
    
    # value_saison
    # value_region
    # value_departement
    values = {'value_affichage' : 'all', 'value_saison' : str(season)}
    values.update(site)
    
    url = 'https://www.extranat.fr/natcourse/cgi-bin/competition_liste.php5'
    #r = session.post(url, data=values, cookies =cookies)
    r = session.post(url, data=values)
    if r.status_code != 200:
        print("Error code (competition):{}".format(r.status_code))
        return
    #print("Status code:{}".format(r.status_code))
    #print(r.text)
    tree = html.fromstring(r.text)
    regexpNS = "http://exslt.org/regular-expressions"
    # CptLight qui est le type de compétition, alors que CptText est le nom
    regexp = '//body/div/div[@id="container"]//table[@class="tableauCpt"]/tbody[starts-with(@id, "periode_")]//tr/td/span[@class="CptLight"][re:test(text(), "{}", "i")]/ancestor::td/preceding-sibling::td'.format(name)

    idcpt = []
    rows = tree.xpath(regexp, namespaces={'re':regexpNS})
    for row in rows:
        for element in row.iter():
            if element.text is not None and not element.text.strip():
                continue
            idcpt.append(element.text)
    return idcpt
    

def findDepIdCptByName(session, season, dep, name):
    """
    Recherche dans le département indiqué toutes les compétitions portant le nom indiqué et retourne la liste des identifiants de ces compétitions.
    
    :param sessions: sessions http
    :param season: saison
    :param dep: numéro du département
    :param name: nom des compétitions recherchées, une regexp est autorisée
    :type season: int
    :type dep: int
    :type name: string
    :return: liste d'identifiant de compétition
    :rtype: list
    """

    if isinstance(dep, str) and len(dep) <= 3:
        d =dep
        while len(d) < 3:
            d = "0{}".format(d)
    elif isinstance(dep, int) and dep < 96:
        d = "{0:03}".format(dep)
    else:
        return []

    return _findSiteIdCptByName(session, season, {'value_departement' : d}, name)
    
def findRegIdCptByName(session, season, reg, name):
    """
    Recherche dans le département indiqué toutes les compétitions portant le nom indiqué et retourne la liste des identifiants de ces compétitions.
    
    :param sessions: sessions http
    :param season: saison
    :param reg: numéro de la réfion
    :param name: nom des compétitions recherchées, une regexp est autorisée
    :type season: int
    :type dep: int
    :type name: string
    :return: liste d'identifiant de compétition
    :rtype: list
    """

    if isinstance(reg, str) and len(reg) <= 2:
        r =reg
        while len(r) < 2:
            r = "0{}".format(r)
    elif isinstance(reg, int) and reg < 30:
        r = "{0:02}".format(reg)
    else:
        return []

    return _findSiteIdCptByName(session, season, {'value_region' : str(r)}, name)
    
