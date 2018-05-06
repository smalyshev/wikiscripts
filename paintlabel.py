import pywikibot
import sys
import json
import uuid
from pywikibot.data.sparql import SparqlQuery

HELP = """
This script applies painting title to label in the same language
"""

site = pywikibot.Site("wikidata", "wikidata")
site.throttle.setDelays(writedelay=1)
repo = site.data_repository()
sparql_query = SparqlQuery()
TITLES_QUERY = """
SELECT ?p ?title WHERE {
  ?p wdt:P31 wd:Q3305213 .
  ?p (wdt:P1705|wdt:P1476) ?title .
  BIND(lang(?title) as ?lt)
  FILTER(?lt != "und")
  FILTER NOT EXISTS {
    ?p rdfs:label ?pl .
    FILTER(lang(?pl) = ?lt)
  }
} LIMIT 100
"""

results = sparql_query.select(TITLES_QUERY, full_data=True)
#print(results)
for result in results:
    lang = result['title'].language
    title = result['title'].value
    if "-" in lang:
        print("Skipping hyphenaten language %s for now" % lang)
        continue
    item = pywikibot.ItemPage(repo, result['p'].getID())
    item.get()
    if lang in item.labels:
        print("%s already has label %s" % (result['p'].getID(), lang))
    else:
        print("Adding %s for %s:%s" % (title, result['p'].getID(), lang))
        item.labels[lang] = title
        item.editLabels(item.labels, summary="Set label from title")
