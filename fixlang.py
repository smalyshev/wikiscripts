import pywikibot
import sys
import json
import uuid
from pywikibot.data.sparql import SparqlQuery

HELP = """
Fix language in title from labels
"""

site = pywikibot.Site("wikidata", "wikidata")
site.throttle.setDelays(writedelay=1)
repo = site.data_repository()
sparql_query = SparqlQuery()
TITLES_QUERY = """
SELECT * WHERE {
  ?p wdt:P31 wd:Q3305213 .
  ?p (wdt:P1705|wdt:P1476) ?title .
  FILTER(lang(?title) = "und")
} LIMIT 100
"""

def fix_lang(claims, labels):
    for claim in claims:
        if claim.getSnakType() != 'value':
            continue
        target = claim.getTarget()
        print(target)
        if not isinstance(target, pywikibot.WbMonolingualText):
            continue
        if target.language != 'und':
            continue
        for lablang in labels:
            if labels[lablang] == target.text:
                print("Found match: %s:%s" % (lablang, labels[lablang]))
                target.language = lablang
                claim.changeTarget(target, summary="Fixing title language")
                break

results = sparql_query.get_items(TITLES_QUERY, item_name="p")
for itemID in results:
    item = pywikibot.ItemPage(repo, itemID)
    item.get()
    print("Processing %s" % itemID)
    if 'P1705' in item.claims:
        fix_lang(item.claims['P1705'], item.labels)
    if 'P1476' in item.claims:
        fix_lang(item.claims['P1476'], item.labels)
