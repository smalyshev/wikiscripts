import pywikibot
import sys
from pywikibot.data.sparql import SparqlQuery

"""
This scripts fixes wrong units in quantities.
Two forms:
cat id-list | python3 fixunit.py PROP TRUE-UNIT
or:
python3 fixunit.py PROP TRUE-UNIT FALSE-UNIT
"""

PROP = sys.argv[1]
UNIT = sys.argv[2]
QUERY = """
SELECT ?id WHERE {
    ?id p:%s/psv:%s [ wikibase:quantityUnit wd:%s ]
    FILTER(?id != wd:Q4115189 && ?id != wd:Q13406268 && ?id != wd:Q15397819)
}
"""

sparql_query = SparqlQuery()

if UNIT == '1' or UNIT == 'Q199':
    UNIT = None
else:
    UNIT = 'http://www.wikidata.org/entity/' + UNIT

site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()

if len(sys.argv) <= 3:
    source = sys.stdin
else:
    # use query
    sparql = QUERY % (PROP, PROP, sys.argv[3])
    items = sparql_query.get_items(sparql, item_name="id")
    print("%s items found: %s" % (len(items), items))
    source = items

for qid in source:
    qid = qid.strip()
    if qid[0:5] == 'http:':
        # strip http://www.wikidata.org/entity/
        qid = qid[31:]
    item = pywikibot.ItemPage(repo, qid)
    item.get()
    if PROP not in item.claims:
        print("No %s for %s, skip!" % (PROP, qid))
        continue
    for claim in item.claims[PROP]:
        if claim.getSnakType() != 'value':
            continue
        target = claim.getTarget()
        if not isinstance(target, pywikibot.WbQuantity):
            print("Non-quantity value in %s for %s, skip!" % (PROP, qid))
            continue
        if UNIT == None and target.unit == '1':
            continue
        if target.unit != UNIT:
            print("Bad unit for %s:%s - want %s, now %s. Fixing." % (qid, PROP, UNIT, target.unit))
            target._unit = UNIT
            claim.changeTarget(target)
