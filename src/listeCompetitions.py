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

from svFFN import AnalyzeWebExtranat, miscFFN

import argparse
import csv

def saveIdCompetitions(filename, cpts):
    if cpts == None:
        return

    with open(filename, "w") as csv_file:
        csv_writer = csv.writer(csv_file, dialect='excel')
        csv_writer.writerows(cpts)
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extrait du site extranat, les numéros de compétitions à analyser. Nécessite un compte sur extranat");
    parser.add_argument('-l', '--login', required=True, type=str, help='identifiant.')
    parser.add_argument('-p', '--password', required=True, type=str, help='mot de passe.')
    parser.add_argument('-f', '--fichier', required=True, type=str, help='nom du fichier où sauver les identifiants des compétitions.')
    parser.add_argument('-s', '--saison', required=False, type=int, help='supèrieur à 2001, et au plus égal à la saison courante. Par défaut saison courante.')
    parser.add_argument('-d', '--departement', required=False, nargs='?', const=0, type=int, help='numéro du département. Sans paramètre, tous les départements sont insérés.')
    parser.add_argument('-r', '--region', required=False, nargs='?', const=0, type=int, help='numéro de la région. Sans paramètre, toutes les régions sont insérées.')
    
    args = parser.parse_args()
    
    season = miscFFN.current_season()
    if args.saison == None:
        args.saison = season
    elif args.saison < 2002 or args.saison > season:
    	print('Le paramètre saison doit être supèrieur à 2001, et au plus égal à la saison courante ', season) 
    	sys.exit(1)

    
    #desc = '^natathlon.*(12-13).*'
    #desc = '.*natathlon.*(12-13).*'
    desc = '^type : natathlon.*(12-13).*'
    session = AnalyzeWebExtranat.initSession(args.login, args.password)
    
    cpts = []
    if args.departement == 0:
        for dep in miscFFN.departements_orphelins:
            idcpts = AnalyzeWebExtranat.findDepIdCptByName(session, args.saison, dep, desc)
            if len(idcpts) > 0:
                idcpts.insert(0, miscFFN.departements_orphelins[dep])
                cpts.append(idcpts)
    elif args.departement and args.departement > 0:
         idcpts = AnalyzeWebExtranat.findDepIdCptByName(session, args.saison, args.departement, desc)
         if len(idcpts) > 0:
             idcpts.insert(0, miscFFN.departements_orphelins[args.departement])
             cpts.append(idcpts)
    if args.region == 0:
        for reg in miscFFN.regions_orphelines:
            idcpts = AnalyzeWebExtranat.findRegIdCptByName(session, args.saison, reg, desc)
            if len(idcpts) > 0:
                idcpts.insert(0, miscFFN.regions_orphelines[reg])
                cpts.append(idcpts)
    elif args.region and args.region > 0:
        idcpts = AnalyzeWebExtranat.findRegIdCptByName(session, args.saison, args.region, desc)
        if len(idcpts) > 0:
            idcpts.insert(0, miscFFN.regions_orphelines[args.region])
            cpts.append(idcpts)

    saveIdCompetitions(args.fichier, cpts)
