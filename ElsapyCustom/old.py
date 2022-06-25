# Install pandas and elsapy before running

from ElsapyCustom.elsclient import *
from ElsapyCustom.elsprofile import *
from ElsapyCustom.elssearch import *
from ElsapyCustom.elsdoc import *

import logging

client = ElsClient('70ec981569c73615021911465abb2f94', num_res=1337)

# doc = AbsDoc(scp_id = '85129920558')
# doc.read(client)

# affil = ElsAffil(affil_id = '60105869')
# affil.read(client)
# thing = client.exec_request('https://api.elsevier.com/content/search/scopus?query=Innopolis+University')
# thing = client.exec_request('https://api.elsevier.com/content/author/author_id/8557895400')

innopolis_authors = ElsSearch("affil(Innopolis University)", 'author')
innopolis_authors.execute(client, True)

i = 1
for el in innopolis_authors.results:
    print(str(i) + ". " + el['preferred-name']['given-name'] + " " + el['preferred-name']['surname'])
    i += 1

print('Input target author surname:')
name = input().lower()

print('Starting search for "' + name + '"')
auth_srch = ElsSearch("authlast(" + name + ")", 'author')
auth_srch.execute(client)
print("Author search has", len(auth_srch.results), "results:")
i = 1
authors = [0]
for el in auth_srch.results:
    try:
        aff = el['affiliation-current']['affiliation-name']
        print(
            str(i) + ". " + el['preferred-name']['given-name'] + " " + el['preferred-name']['surname'] + " from " + aff)
    except Exception:
        print(str(i) + ". " + el['preferred-name']['given-name'] + " " + el['preferred-name']['surname'])
    authors.append(el)
    i += 1

print()

while True:
    print("Select author to query papers, or q to exit:")
    inp = input()

    if inp.lower() == 'q':
        break

    print("Quering " + authors[int(inp)]['preferred-name']['given-name'] + " " + authors[int(inp)]['preferred-name'][
        'surname'])
    author = ElsAuthor(uri=authors[int(inp)]['prism:url'])

    if author.read(client):
        if author.read_docs(client):
            print("  Full query success")
        else:
            print("  Doc query failed")
        print("  Document count: " + author.data['coredata']['document-count'])
        print("  Cited by count: " + author.data['coredata']['cited-by-count'])
        print("  Citation count: " + author.data['coredata']['citation-count'])
        print("")
    else:
        print("  Author query failed")

    print()
