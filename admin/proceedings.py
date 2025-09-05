#!/usr/bin/env python3

import requests

from secrets import API_TOKEN
import browser_cookie3, re, sys, os, subprocess

rootdir = "/home/alex/src/alpaca-templates/admin/"

limit = None

if len(sys.argv) > 1:
  limit = sys.argv[1]
  subprocess.run(["rm", "-rf", "cache/" + limit])

print("limit", limit)
BASE_URL = "https://conference.algorithmicpattern.org/api/"

# Configuration
event_slug = 2025

cookiejar = browser_cookie3.firefox(domain_name='doc.patternclub.org')

# [{'id': 263, 'question': 1, 'answer': 'file://Proposal Tonje K Johnstone.pdf', 
#   'answer_file': 'https://conference.algorithmicpattern.org/media/2025/question_uploads/Proposal_Tonje_K_Johnstone_mIdpXmh.pdf', 
# 'submission': '3TACNN', 'review': None, 'person': None, 'options': []
#   }, 
#   {'id': 264, 'question': 8, 'answer': 'On-line', 'answer_file': None, 'submission': '3TACNN', 'review': None, 'person': None, 'options': [2]
#   }, 
#   {'id': 484, 'question': 13, 'answer': 'file://Final Tonje K Johnstone.pdf', 'answer_file': 'https://conference.algorithmicpattern.org/media/2025/question_uploads/Final_Tonje_K_Johnstone_PAagpvr.pdf', 'submission': '3TACNN', 'review': None, 'person': None, 'options': []
#   }
#   ]

def prettyjoin(my_list):
    my_list = list(my_list)
    return " and ".join([", ".join(my_list[:-1]),my_list[-1]] if len(my_list) > 2 else my_list)

def get_accepted_submissions():
    url = f"{BASE_URL}events/{event_slug}/submissions/?expand=answers,speakers,submission_type"
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Accept": "application/json"
    }

    submissions = []
    next_page = url

    while next_page:
        response = requests.get(next_page, headers=headers)
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            break
        
        data = response.json()
        # print(data['results'])
        for submission in data['results']:
            if limit and limit != submission["code"]:
                continue
            # print(submission["speakers"])
            # print(submission["title"])
            type = submission["submission_type"]["name"]["en"]
            if submission["state"] == "confirmed" and (type == "Online talk" or type == "Sheffield-based talk"):
                # submission["speakers"] = list(map(lambda slug: get_author(slug), submission['speakers']))
                for answer in submission["answers"]:
                    if answer["question"] == 2:
                        submission["hedgedoc"] = answer["answer"]
                submissions.append(submission)
                # print(submission)
        next_page = data["next"]  # Pagination handling

    return submissions

def get_author(author_slug):
    url = f"{BASE_URL}events/{event_slug}/speakers/{author_slug}/"
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        return
        
    data = response.json()
    print(data)
    return data

def get_answers(question):
    url = f"{BASE_URL}events/{event_slug}/answers/?question={question}"
    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: {response.status_code}, {response.text}")
        return
        
    data = response.json()
    print(data)

def render_markdown(sub):
    code = sub["code"]
    sourcefile = "source.md"
    htmlfile = "render.html"
    mediadir = "media/"

    if not os.path.exists(rootdir + "cache/" + code):
        os.makedirs(rootdir + "cache/" + code)
    os.chdir(rootdir + "cache/" + code)

    alias = sub["title"]
    alias = re.sub('\s', '_', alias)
    cachealias = rootdir + "cache/" + alias + ".html"
    if not os.path.exists(cachealias):
        os.symlink(code + "/render.html", cachealias)

    url = sub["hedgedoc"]
    url = re.sub('/?(\#.*)?$', '', url)
    url = url + '/download/'
    r = requests.get(url, cookies=cookiejar)

    if r.status_code != 200:
        print("Response code: " + str(r.status_code))
        sys.exit(-2)
    with open(sourcefile, "w") as text_file:
        text_file.write(r.text)

    result = r.text
    subprocess.run(["/usr/bin/pandoc", "--mathjax", "-s", sourcefile, "--extract-media="+mediadir, 
                    "--template="+rootdir+"template.html", "--css=../../pandoc.css", "-o", htmlfile])

    return htmlfile

if __name__ == "__main__":
    accepted_submissions = get_accepted_submissions()

    if accepted_submissions:
        print(f"Accepted submissions:\n\n")
        for sub in accepted_submissions:
            speakers = prettyjoin(map(lambda x: x['name'], sub["speakers"]))
            sub['prettyspeakers'] = speakers
            print(f"\n[{sub['code']}] {sub['title']} by {(speakers)}\n")
            if "hedgedoc" in sub:
                print(f"  {sub['hedgedoc']}\n  http://localhost:8080/{sub['code']}/render.html")
                file = render_markdown(sub)
                
    else:
        print("No accepted submissions found or an error occurred.")
