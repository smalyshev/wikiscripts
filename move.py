import pywikibot
import sys
import json
import uuid

HELP = """
This scripts moves claims between items
python3 mvclaims.py QID-FROM QID-TO PROP
"""

if len(sys.argv) < 3:
    print(HELP)
    exit()

site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()
site.throttle.setDelays(writedelay=1)

qidF = sys.argv[1]
qidT = sys.argv[2]
prop = sys.argv[3]

itemF = pywikibot.ItemPage(repo, qidF)
itemF.get()
itemT = pywikibot.ItemPage(repo, qidT)
itemT.get()
if prop not in itemF.claims:
    print("No such property!")
    exit()

for claim in itemF.claims[prop]:
    jsonData = claim.toJSON()
    jsonData['mainsnak']['property'] = prop
    jsonData['id'] = qidT + '$' + str(uuid.uuid4())
    print(json.dumps(jsonData))
    newclaim = pywikibot.Claim.fromJSON(site, jsonData)
    newclaim.on_item = itemT
    itemT.repo.save_claim(newclaim, summary="Copying %s from %s to %s" % (prop, qidF, qidT))

