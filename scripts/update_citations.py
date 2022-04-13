import sys

import toml
from scholarly import scholarly

author = scholarly.search_author_id('_7AMrKgAAAAJ')  # _7AMrKgAAAAJ is Quasar

quasar_stats = scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])

scholarly.pprint(quasar_stats)

# What papers cited our publications?
cit = []
for pub in quasar_stats['publications']:
    print(pub)
    cit.append([citation for citation in scholarly.citedby(pub)]) # limit the number of test runs because this will get blocked bu Google quickly

print(f'There are currently {len(quasar_stats["publications"])} Quasar papers.')
for pub in quasar_stats['publications']:
    print(' ',pub['bib']['title'])

fcit = [item for sublist in cit for item in sublist] # this is a flat list now
print(f'\nWe have {len(fcit)} citations so far for our Quasar papers.')

# I wonder if this can be done in fewer lines. :D
authors = [c["author_id"] for c in fcit]
citing_authors = [item for sublist in authors for item in sublist]
citing_authors = set([c for c in citing_authors if c]) # citing authors with Google Scholar profile
print(f'\nThere are {len(citing_authors)} people citing Quasar with a Google Scholar profile.')

# count how many papers cite those papers that use Quasar - this is the real impact.
secondary_cit = sum([paper["num_citations"] for paper in fcit])
print(f'\n{secondary_cit} papers cite the works which use Quasar.')

FN = "data/citations.toml"
td = toml.load(FN)

if len(fcit) < int(td["direct"]):
    print("Citation number has decreased; exiting.")
    sys.exit(-1)
else:
    td["direct"] = len(fcit)

with open(FN,  "wt") as of:
    toml.dump(td, of)
