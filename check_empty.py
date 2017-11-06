#!/usr/bin/python3
import pywikibot
from pywikibot.data.sparql import SparqlQuery
import sys

"""
Check "no data" properties in case there's data now
"""
sparql_query = SparqlQuery()

START_END_QUERY = """
PREFIX q: <http://www.wikidata.org/prop/qualifier/>
SELECT DISTINCT ?s WHERE {
  BIND (p:%s as ?prop)
  ?s ?prop ?st .
# One claim with start time
  ?st q:P580 ?t .
# and no end time
  OPTIONAL { ?st q:P582 ?t2 }
  FILTER(!bound(?t2))
  ?st wikibase:rank wikibase:NormalRank.
# it's best rank, i.e. no preferred
  ?st a wikibase:BestRank .
# Another claim
  ?s ?prop ?st2 .
  FILTER(?st2 != ?st)
# with an end time
  ?st2 q:P582 ?t3 .
# and it's not a dead person
  OPTIONAL { ?s wdt:P570 ?d }
  FILTER(!bound(?d))
  ?st2 wikibase:rank wikibase:NormalRank.
} LIMIT 10
"""

POINT_QUERY = """
PREFIX q: <http://www.wikidata.org/prop/qualifier/>
SELECT DISTINCT ?s WHERE {
  BIND (p:%s as ?prop)
  ?s ?prop ?st .
# One claim with point-in-time
  ?st q:P585 ?t .
# Normal rank
  ?st wikibase:rank wikibase:NormalRank.
  ?st a wikibase:BestRank .
# Another claim
  ?s ?prop ?st2 .
  FILTER(?st2 != ?st)
# with an end time
  ?st2 q:P585 ?t3 .
# and it's not a dead person
  OPTIONAL { ?s wdt:P570 ?d }
  FILTER(!bound(?d))
  ?st2 wikibase:rank wikibase:NormalRank.
  ?st2 a wikibase:BestRank .
} LIMIT 10
"""

with open(sys.argv[1]) as f:
    items = f.readlines()

print("Got %d items" % len(items))

for item in items:
    item = item.strip()
    se_query = START_END_QUERY % item
    pit_query = POINT_QUERY % item
    print("Checking %s..." % item)
    results = sparql_query.get_items(se_query, item_name="s")
    if len(results) > 0:
        print(" %d start/end results for %s" % (len(results), item))
    results = sparql_query.get_items(pit_query, item_name="s")
    if len(results) > 0:
        print(" %d PIT results for %s" % (len(results), item))
        