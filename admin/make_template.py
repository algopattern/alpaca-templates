#!/usr/bin/env python3

import requests
import browser_cookie3

cookiejar = browser_cookie3.firefox(domain_name='doc.patternclub.org')

url = 'https://doc.patternclub.org/new'
headers = {'Content-type': 'text/markdown'}

file = open('../alpaca-template-2025.md')
md = file.read()
file.close()

r = requests.post(url, headers=headers, cookies=cookiejar, data=md.encode('utf-8'))

file = open('./email.txt')
md = file.read()
file.close()

md = md.replace("URL", r.url)

print(md)
