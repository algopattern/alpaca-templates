#!/usr/bin/env python3

import requests

from secrets import API_TOKEN

BASE_URL = "https://conference.algorithmicpattern.org/api/"

# Configuration
event_slug = 2025


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
            # print(submission["speakers"])
            # print(submission["title"])
            type = submission["submission_type"]["name"]["en"]
            if submission["state"] == "confirmed" and (type == "Online talk" or type == "Sheffield-based talk"):
                # submission["speakers"] = list(map(lambda slug: get_author(slug), submission['speakers']))
                for answer in submission["answers"]:
                    if answer["question"] == 2:
                        submission["hedgedoc"] = answer["answer"]
                submissions.append(submission)
                print(submission)
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


if __name__ == "__main__":
    accepted_submissions = get_accepted_submissions()

    if accepted_submissions:
        print(f"Accepted submissions:\n")
        for sub in accepted_submissions:
            speakers = prettyjoin(map(lambda x: x['name'], sub["speakers"]))
            print(f"- {sub['title']} by {(speakers)}")
            if "hedgedoc" in sub:
                print("   " + sub["hedgedoc"])
    else:
        print("No accepted submissions found or an error occurred.")
