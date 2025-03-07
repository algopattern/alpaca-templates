#!/usr/bin/env python3

import requests
import browser_cookie3

# get login info from firefox
cookiejar = browser_cookie3.firefox(domain_name='doc.patternclub.org')

url = 'https://doc.patternclub.org/new'
headers = {'Content-type': 'text/markdown'}

# read template
file = open('../alpaca-template-2025.md')
md = file.read()
file.close()

# create hedgedoc document
r = requests.post(url, headers=headers, cookies=cookiejar, data=md.encode('utf-8'))

# construct email
file = open('./email.txt')
md = file.read()
file.close()
md = md.replace("URL", r.url)

print(md)
