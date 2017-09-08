# wikiscripts
This repo contains various pywikibot scripts. Needs pywikibot checkout to work.

Check out inside pywikibot repo and run:
    python3 pwb.py wikiscripts/script.py

No guarantees whatsoever, these scripts are all quick-n-dirty and should be used
with extreme care only by people who know what they are doing. 

Included scripts:

check_empty.py - Check "no data" properties in case there's data now, for PrefBot
fixship.py - Fixes vessels where volume is given as "mass" (may be not needed already)
fixunit.py - Fixes wrong units in quantities.
paint_be.py - Painting data import for bewiki
paint_en.py - Painting data import for enwiki
paint_es.py - Painting data import for eswiki
paint_ru.py - Painting data import for ruwiki
paint_uk.py - Painting data import for ukwiki
units.py - Get the list of anomalous units
