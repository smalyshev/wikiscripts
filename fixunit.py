import pywikibot
import sys
from pywikibot.data.sparql import SparqlQuery
from argparse import ArgumentParser

HELP = """
This scripts fixes wrong units in quantities.
Two forms:
cat id-list | python3 fixunit.py PROP TRUE-UNIT
or:
python3 fixunit.py PROP TRUE-UNIT FALSE-UNIT [TYPE]
"""

parser = ArgumentParser(description='This scripts fixes wrong units in quantities.')
parser.add_argument("-p", "--prop", dest="prop", help="Property to work on", metavar="P123", required=True)
parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="Print SPARQL queries being run")
parser.add_argument("-f", "--from", dest="fromUnit", help="Original (wrong) unit", metavar="Q123")
parser.add_argument("-t", "--to", dest="toUnit", help="Correct unit", required=True, metavar="Q123")
parser.add_argument("-T", "--type", dest="type", help="Type of items to process", metavar="Q123")
parser.add_argument("-D", "--drop", dest="drop", action="store_true", help="Drop statement instead of changing units")
parser.add_argument("-q", dest="qualifiers", action="store_true", help="Look in qualifiers")
parser.add_argument("-a", dest="all", action="store_true", help="Look in both statements and qualifiers")

options = parser.parse_args()

QUERY = """
SELECT ?id WHERE {
    ?id p:%s/psv:%s [ wikibase:quantityUnit wd:%s ] .
	%s
    FILTER(?id != wd:Q4115189 && ?id != wd:Q13406268 && ?id != wd:Q15397819)
}
"""
QUERY_Q = """
SELECT ?id WHERE {
    ?id ?p ?s .
    # Ignore examples
    FILTER(?p != p:P1855)
    ?s pqv:%s [ wikibase:quantityUnit wd:%s ] .
    %s
    FILTER(?id != wd:Q4115189 && ?id != wd:Q13406268 && ?id != wd:Q15397819)
}
"""
STDUNITS = {
    '1': 'Q199',
    'bad1': '1',
    'badm': 'm2',
    'm': 'Q11573',
    'm2': 'Q25343',
    '%': 'Q11229',
    'cm': 'Q174728',
    'km': 'Q828224',
    'kg': 'Q11570',
    'kmh': 'Q180154',
    'km2': 'Q712226',
    'y': 'Q577',
    'amu': 'Q483261',
    'usd': 'Q4917',
    "min": 'Q7727'
}

def convert_unit(unit):
    if unit in STDUNITS:
        unit = STDUNITS[unit]
    else:
        if unit[0] != 'Q':
            raise RuntimeError("Bad unit: "+ unit)
    return unit

if options.toUnit == '1':
    UNIT = None
else:
    UNIT = 'http://www.wikidata.org/entity/' + convert_unit(options.toUnit) 
PROP = options.prop

itemFilter = ""
if options.type:
    itemFilter = "?id wdt:P31 wd:%s ." % options.type 

sparql_query = SparqlQuery()
site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()
site.throttle.setDelays(writedelay=1)

def ids_from_sparql():
    bad_unit = convert_unit(options.fromUnit)
    if options.qualifiers:
        sparql = QUERY_Q % (PROP, bad_unit, itemFilter)
    else:
        sparql = QUERY % (PROP, PROP, bad_unit, itemFilter)
    if options.verbose:
        print(sparql)
    items = sparql_query.get_items(sparql, item_name="id")
    print("%s items found: %s" % (len(items), items))
    source = items
    if len(source) > 200:
        print("Too many items, you are probably doing something wrong. Let's re-think it.")
        return []
    return items

def process_claim(qid, claim):
    if claim.getSnakType() != 'value':
        return
    target = claim.getTarget()
    if not isinstance(target, pywikibot.WbQuantity):
        print("Non-quantity value in %s for %s, skip!" % (PROP, qid))
        return
    # Now we know this statement is our target
    if options.drop:
        comment = "Bad claim in %s:%s, removing." % (qid, PROP)
        print(comment)
        item.removeClaims(claim, summary=comment)
        return
    if UNIT is None and target.unit == '1':
        return
    if target.unit != UNIT:
        comment = "Bad unit for %s:%s - want %s, now %s. Fixing." % (qid, PROP, UNIT, target.unit)
        print(comment)
        target._unit = UNIT
        claim.changeTarget(target, summary=comment)

def process_claim_qualifier(qid, claim, qclaim, bad_unit):
    if qclaim.getSnakType() != 'value':
        return
    target = qclaim.getTarget()
    if not isinstance(target, pywikibot.WbQuantity):
        print("Non-quantity value in %s for %s, skip!" % (PROP, qid))
        return
    # Now we know this statement is our target
    if options.drop:
        comment = "Bad claim in %s/%s, removing." % (qid, PROP)
        print(comment)
        claim.removeQualifier(qclaim, summary=comment)
        return
    if UNIT is None and target.unit == '1':
        return
    if target.unit != UNIT:
        if target.unit != bad_unit:
            print("Bad unit for %s:%s:%s - want %s, now %s, not %s. Ignoring." % (qid, claim.id, PROP, UNIT, target.unit, bad_unit))
            return
        comment = "Bad unit for %s:%s:%s - want %s, now %s. Fixing." % (qid, claim.id, PROP, UNIT, target.unit)
        print(comment)
        target._unit = UNIT
        claim.repo.save_claim(claim, summary=comment)

if not options.fromUnit:
    source = sys.stdin
else:
    source = ids_from_sparql()

for qid in source:
    qid = qid.strip()
    if qid[0:5] == 'http:':
        # strip http://www.wikidata.org/entity/
        qid = qid[31:]
    item = pywikibot.ItemPage(repo, qid)
    item.get()
    if not options.qualifiers or options.all:
        if PROP not in item.claims:
            print("No %s for %s, skip!" % (PROP, qid))
            continue
        for claim in item.claims[PROP]:
            process_claim(qid, claim)
    if options.qualifiers or options.all:
        # Qualifier check
        bad_unit = options.fromUnit
        if bad_unit != '1':
            bad_unit = 'http://www.wikidata.org/entity/' + convert_unit(bad_unit)
        for p in item.claims:
            for claim in item.claims[p]:
                if PROP not in claim.qualifiers:
                    continue
                for qclaim in claim.qualifiers[PROP]:
                    process_claim_qualifier(qid, claim, qclaim, bad_unit)