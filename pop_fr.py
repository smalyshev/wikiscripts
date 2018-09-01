#!/usr/bin/python3

import pywikibot
import sys
from pywikibot import pagegenerators
from pywikibot.data.sparql import SparqlQuery
import re

"""
Import population figure from frwiki template
"""

QUERY_LINK = """
SELECT ?name WHERE {
  ?page schema:about wd:%s; schema:inLanguage "fr"; schema:name ?name .
}
"""
QID = sys.argv[1]
if QID[0] != 'Q':
    QID = QID[30:]
sparql_query = SparqlQuery()
datere = re.compile('(\d\d\d\d)')

def find_by_sitelink(qid):
    sparql = QUERY_LINK % (qid)
#    print(sparql)
    results = sparql_query.select(sparql)
    return results[0]['name']

site = pywikibot.Site("fr", "wikipedia")
for page in pagegenerators.PagesFromTitlesGenerator([find_by_sitelink(QID)], site):
    for (template, args) in page.templatesWithParams():
#        print(template.title(), args)
        if template.title() == 'Modèle:Infobox Ville':
            argmap = dict(arg.split('=', maxsplit=1) for arg in args)
            if 'année_pop' in argmap:
                match = datere.match(argmap['année_pop'])
                if match:
                    print(match.group(1))
