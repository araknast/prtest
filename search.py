#!/usr/bin/env python3
import uuid
import pyssdb
import time
import sys

db = pyssdb.Client()
search_query = str(sys.argv[1])
query_id = "q:" + str(uuid.uuid4())

search_terms = search_query.split()
#search_terms = [ "t:" + x for x in search_terms]
matches = db.zkeys(search_terms.pop(), 0, 0, 1, -1)
for search_term in search_terms:
    matches = set(matches).intersection(db.zkeys(search_term, 0, 0, 1, -1))

matches = list(map(lambda x: (x, float(db.hget("pr2",x.decode("utf-8").split("/")[2]))), matches))
matches = sorted(matches, key=lambda x: x[1], reverse=True)
print("Found {} results for \"{}\"".format(len(matches), search_query))

for i, match in enumerate(matches):
    print("{}. {} ({})".format((i+1), match[0].decode(), float(match[1])))
