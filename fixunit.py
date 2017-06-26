import pywikibot
import sys
from pywikibot.data.sparql import SparqlQuery

HELP = """
This scripts fixes wrong units in quantities.
Two forms:
cat id-list | python3 fixunit.py PROP TRUE-UNIT
or:
python3 fixunit.py PROP TRUE-UNIT FALSE-UNIT [TYPE]
"""

if len(sys.argv) < 3:
    print(HELP)
    exit()

PROP = sys.argv[1]
UNIT = sys.argv[2]
if len(sys.argv) > 4:
    TYPE = sys.argv[4]
else:
    TYPE = None
QUERY = """
SELECT ?id WHERE {
    ?id p:%s/psv:%s [ wikibase:quantityUnit wd:%s ] .
	%s
    FILTER(?id != wd:Q4115189 && ?id != wd:Q13406268 && ?id != wd:Q15397819)
}
"""
STDUNITS = {
    '1': 'Q199',
	'bad1': '1',
    '%': 'Q11229',
    'cm': 'Q174728',
    'km': 'Q828224',
    'kg': 'Q11570',
    'kmh': 'Q180154',
}

sparql_query = SparqlQuery()

if UNIT == '1' or UNIT == 'Q199':
    UNIT = None
else:
    if UNIT in STDUNITS:
        UNIT = STDUNITS[UNIT]
    UNIT = 'http://www.wikidata.org/entity/' + UNIT

if TYPE:
	QTYPE = "?id wdt:P31 wd:%s ." % TYPE
else:
	QTYPE = ""


site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()
site.throttle.setDelays(writedelay=1)

if len(sys.argv) <= 3:
    source = sys.stdin
else:
    # use query
    bad_unit = sys.argv[3]
    if bad_unit in STDUNITS:
        bad_unit = STDUNITS[bad_unit]
    sparql = QUERY % (PROP, PROP, bad_unit, QTYPE)
    print(sparql)
    items = sparql_query.get_items(sparql, item_name="id")
    print("%s items found: %s" % (len(items), items))
    source = items

if len(source) > 600:
	print("Too many items, you are probably doing something wrong. Let's re-think it.")

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
            comment = "Bad unit for %s:%s - want %s, now %s. Fixing." % (qid, PROP, UNIT, target.unit)
            print(comment)
            target._unit = UNIT
            claim.changeTarget(target, summary=comment)
