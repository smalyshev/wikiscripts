import pywikibot
import sys
from pywikibot.data.sparql import SparqlQuery

HELP = """
This scripts fixes vessels where volume is given as "mass"
"""

PROP = 'P2067'
QUERY = """
SELECT ?id ?idLabel WHERE {
    ?id p:P2067/psv:P2067 [ wikibase:quantityUnit wd:Q199 ] .
    ?id wdt:P31 wd:Q848944 .
    FILTER(?id != wd:Q4115189 && ?id != wd:Q13406268 && ?id != wd:Q15397819)
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
"""
TON = 'http://www.wikidata.org/entity/Q752079'
VOLUME = 'P2234'

site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()
site.throttle.setDelays(writedelay=1)

sparql_query = SparqlQuery()
items = sparql_query.get_items(QUERY, item_name="id")

print("%d items found" % len(items))
for item in items:
    qid = item.strip()
    if qid[0:5] == 'http:':
        # strip http://www.wikidata.org/entity/
        qid = qid[31:]
    item = pywikibot.ItemPage(repo, qid)
    item.get()
    if PROP not in item.claims:
        print("No %s for %s, skip!" % (PROP, qid))
        continue
    badclaims = []
    for claim in item.claims[PROP]:
        if claim.getSnakType() != 'value':
            continue
        target = claim.getTarget()
        if not isinstance(target, pywikibot.WbQuantity):
            print("Non-quantity value in %s for %s, skip!" % (PROP, qid))
            continue
        if target.unit != '1':
            print("Unit specified in %s for %s, skip!" % (PROP, qid))
            continue
        if not claim.has_qualifier('P1880', 'Q752079'):
            print("No qualifier in %s for %s, skip!" % (PROP, qid))
            continue
        badclaims.append(claim)
        target._unit = TON
        newclaim = pywikibot.Claim(site, VOLUME)
        newclaim.setSnakType('value')
        newclaim.setRank(claim.rank)
        newclaim.setTarget(target)
        newclaim.sources = claim.sources
        newclaim.on_item = item
        print("Found bad claim in %s, fixing..." % qid)
        item.addClaim(newclaim)
    item.removeClaims(badclaims)
