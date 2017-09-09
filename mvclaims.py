import pywikibot
import sys
import json
import uuid

HELP = """
This scripts moves claims between properties
python3 mvclaims.py QID PROP-FROM PROP-TO
"""

if len(sys.argv) < 3:
    print(HELP)
    exit()

site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()
site.throttle.setDelays(writedelay=1)

qid = sys.argv[1]
fromP = sys.argv[2]
toP = sys.argv[3]

item = pywikibot.ItemPage(repo, qid)
item.get()
if fromP not in item.claims:
    print("No such property!")
    exit()

if toP in item.claims:
    print("Target property already exists!")
    exit()

for claim in item.claims[fromP]:
    jsonData = claim.toJSON()
    jsonData['mainsnak']['property'] = toP
    jsonData['id'] = qid + '$' + str(uuid.uuid4())
    print(json.dumps(jsonData))
    newclaim = pywikibot.Claim.fromJSON(site, jsonData)
    newclaim.on_item = item
    item.repo.save_claim(newclaim, summary="Moving %s to %s" % (fromP, toP))

