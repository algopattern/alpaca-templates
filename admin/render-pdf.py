#!/usr/bin/env python3

import sys
import requests
import browser_cookie3
import urllib.parse
import webbrowser
import re
import pandoc
from pandoc.types import *

if len(sys.argv) < 2:
    print("please supply a note url")
    sys.exit(-1)

url = sys.argv[1]
print("url:", url)
url = re.sub('/?(\#.*)?$', '', url)
url = url + '/download/'


# get login info from firefox
cookiejar = browser_cookie3.firefox(domain_name='doc.patternclub.org')


# get hedgedoc document
# r = requests.post(url, headers=headers, cookies=cookiejar, data=md.encode('utf-8'))
r = requests.get(url, cookies=cookiejar)

if r.status_code != 200:
    print("Response code: " + str(r.status_code))
    sys.exit(-2)
# print(r.text)

headers = []

doc = pandoc.read(r.text)

blocks = doc[1]

header = ""

for block in blocks:
    if block.__class__.__name__ == "Header":
        print(block)
        level, attr, inlines = block.c  # 'c' holds content: [level, attributes, inlines]
        if level == 1:
            # Convert the inline elements to plain text
            parts = []
            for elem in inlines:
                if elem.__class__.__name__ == "Str":
                    parts.append(elem.c)
                elif elem.__class__.__name__ == "Space":
                    parts.append(" ")
            header = "".join(parts).strip()
            break

print(header)

# print("\n\nheaders..\n\n")
# for elt in pandoc.iter(r.text):
#     print("hmm!", elt)
#     if isinstance(elt, Header):
#         #  if elt[0] == 1: # this is header 1, remove this if statement if you want all headers.
#         headers.append(elt[1][0])

# print(headers)

# # construct email
# file = open('./email.txt')
# md = file.read()
# file.close()
# md = md.replace("URL", r.url)

# #print(md + "\n\n")

# url = 'mailto:' + email + '?subject=' + urllib.parse.quote('Algorithmic Pattern talk submission templates') + '&body=' + urllib.parse.quote(md)

# print(url)
# webbrowser.open(url, new=0, autoraise=True)
