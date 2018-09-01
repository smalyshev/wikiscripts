#!/usr/bin/python3

import pywikibot
import sys
from pywikibot import pagegenerators
from pywikibot.data.sparql import SparqlQuery
import re

QUERY = """
SELECT ?id WHERE {
    ?site schema:name "%s"@ru; schema:about ?id .
}
"""
QUERY_LINK = """
SELECT ?name WHERE {
  ?page schema:about wd:%s; schema:inLanguage "ru"; schema:name ?name .
}
"""
QID = sys.argv[1]
sparql_query = SparqlQuery()
linkre = re.compile('\[\[([^|]+)?(\|.+)?]]')
titlere = re.compile('\{\{lang-(\w+)\|(.+)}}')
yearre = re.compile('\[\[(\d+) ')

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
    'год':  ('P571', lambda x: "+" + get_year(x) + "-01-01T00:00:00Z/9"),
    'ширина': ('P2049', lambda x: x.replace(",", ".") + "U174728"),
    'высота': ('P2048', lambda x: x.replace(",", ".") + "U174728"),
    'название': ('P1476', lambda x: 'ru:"' + x.lstrip('«').rstrip('»')  + '"'),
    'автор': ('P170', find_by_label),
    'художник': ('P170', find_by_label),
    'файл': ('P18', lambda x: '"' + x + '"'),
    'музей': ('P195', find_by_label),
    'оригинал': ('P1476', extract_title)
}

site = pywikibot.Site("ru", "wikipedia")
for page in pagegenerators.PagesFromTitlesGenerator([find_by_sitelink(QID)], site):
    print(QID + "\tP31\tQ3305213")
#    print(QID + "\tDen\t\"painting\"")
#    print(QID + "\tDru\t\"картина\"")
    itemData = {}
    for (template, args) in page.templatesWithParams():
        if template.title() == 'Шаблон:Произведение искусства':
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
        print("{0}\t{1}\t{2}\tS143\tQ206855".format(QID, prop, itemData[prop]))
