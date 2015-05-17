Ce programme extrait du site internet de la Fédération Française de Natationles les résultats d'une ou plusieurs compétitions pour les stocker dans une base de données locale afin de les analyser.

Un exemple d'application est réalisé pour le Natathlon Benjamin de la saison 2015. Pour cela vous devez lancer la commande

    natathlon.py -d -r

D'autres options sont possibles, vous pouvez les obtenir avec :

    natathlon.py -h

Le format du fichier CSV accepté en lecture a le format suivant :

    Titre, idCpt1, idCpt2, idCpt3
    Autre titre, idCptX, idCptY

Fonctionnement erroné
---------------------

Si vous constatez un fonctionnement erroné, n'hésitez pas à en faire part. L'auteur essaiera de corriger le problème.

Licence
-------

This code is licensed under GNU Affero General Public License v3. See LICENSE for more details.

Avertissement
-------------

Ce programme est donné à titre de démontration et indicatif. Seul le classement produit par la FFN est officiel.

Ce programme exploite les pages HTML délivré par le site internet de la FFN. Toute modification du site peut rendre ce programme non opérationnel.
