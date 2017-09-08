#!/usr/bin/python3

import pywikibot
import sys
from pywikibot import pagegenerators
from pywikibot.data.sparql import SparqlQuery
import re

QUERY = """
SELECT ?id WHERE {
    ?site schema:name "%s"@es;  schema:about ?id .
}
"""
QUERY_LINK = """
SELECT ?name WHERE {
    ?page schema:about wd:%s;  schema:inLanguage "es"; schema:name ?name .
}
"""
QID = sys.argv[1]
sparql_query = SparqlQuery()
linkre = re.compile('\[\[([^|]+)?(\|.+)?]]')
titlere = re.compile('\{\{lang-(\w+)\|(.+)}}')
yearre = re.compile('\[\[(\d+)')

def find_by_label(label):
    match = linkre.match(label)
    if match:
        label = match.group(1)
    page = pywikibot.Page(site, label)
    if page.isRedirectPage():
        redir = page.getRedirectTarget()
        label = redir.title()
    sparql = QUERY % (label)
#    print(sparql)
    items = sparql_query.get_items(sparql, item_name="id")
#    print(items)
    if not items:
        return None
    return next(iter(items))

def find_by_sitelink(qid):
    sparql = QUERY_LINK % (qid)
#    print(sparql)
    results = sparql_query.select(sparql)
    return results[0]['name']

def extract_title(title):
    match = titlere.match(title)
    if match:
        return '{0}:"{1}"'.format(match.group(1), match.group(2))
    return None

def get_year(year):
    match = yearre.match(year)
    if match:
        return match.group(1)
    return year
    

property_map = {
    'año':  ('P571', lambda x: "+" + get_year(x) + "-01-01T00:00:00Z/9"),
    'anchura': ('P2049', lambda x: x.replace(" cm", "") + "U174728"),
    'longitud': ('P2048', lambda x: x.replace(" cm", "") + "U174728"),
    'título': ('P1476', lambda x: 'es:"' + x.lstrip("''").rstrip("''")  + '"'),
    'autor': ('P170', find_by_label),
    'imagen': ('P18', lambda x: '"' + x + '"'),
    'localización': ('P195', find_by_label),
}

site = pywikibot.Site("es", "wikipedia")
for page in pagegenerators.PagesFromTitlesGenerator([find_by_sitelink(QID)], site):
    print(QID + "\tP31\tQ3305213")
    print(QID + "\tDen\t\"painting\"")
    print(QID + "\tDru\t\"картина\"")
    print(QID + "\tDuk\t\"картина\"")
#    print(QID + "\tDes\t\"pintura\"")
    itemData = {}
    for (template, args) in page.templatesWithParams():
        if template.title() == 'Plantilla:Ficha de pintura' or template.title() == 'Plantilla:Ficha de obra de arte':
            argmap = dict(arg.split('=', maxsplit=1) for arg in args)
            for name in property_map:
                if name in argmap:
                    value = argmap[name]
                    try:
                        val = property_map[name][1](value)
                    except:
                        pass
                    if val != None:
                        itemData[property_map[name][0]] = val
    for prop in itemData:
        print("{0}\t{1}\t{2}\tS143\tQ8449".format(QID, prop, itemData[prop]))
