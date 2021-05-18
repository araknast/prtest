#!/usr/bin/env python3

reset_scores = True
dampening = 0.85
iterations = 14 # according to wikipedia this should be about ln(num_pages)

import pyssdb
db = pyssdb.Client()
pages = db.hkeys("pr", "", "", -1)
num_pages = len(pages)
initial_score = 1.0/num_pages


print("{} pages in db".format(len(pages)))

if reset_scores:
    print("setting initial scores to {}".format(initial_score))

    for page in pages:
        db.hset("pr", page, str(initial_score))
    print("reset scores")

    
for iteration in range(iterations):
    pages_processed = 0
    for page in pages:
        if pages_processed % 10000 == 0:
            print("(Iteration {}) {} entries processed.".format(iteration + 1, pages_processed))
        page_url = page.decode("utf-8")
        page_score = 0.0
        refs = db.zkeys("r:" + page_url, 0, 0, 0, -1)
        for ref in refs:
            ref_url = ref.decode("utf-8")
            ref_score = db.hget("pr", ref_url)
            ref_num_links = db.get("nl:" + ref_url)

            if ref_num_links is None or int(ref_num_links) == 0:
                print("referrer {} num_links is broken, deleting...".format(ref_url))
                db.zdel("r:" + page_url, ref_url)
                continue
            elif ref_score is None:
                print("referrer {} score is broken, deleting...".format(ref_url))
                db.zdel("r:" + page_url, ref_url)
                continue
            else:
                ref_num_links = int(ref_num_links)
                ref_score = float(ref_score)

            page_score += ref_score/ref_num_links
        page_score = dampening * page_score
        page_score += (1.0-dampening)/num_pages
        db.hset("pr", page, str(page_score))
        pages_processed += 1
