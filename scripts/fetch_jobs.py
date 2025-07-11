import requests
import json
import os
from datetime import datetime
import re

SERPER_API_KEY = os.environ.get('SERPER_API_KEY')
SEARCH_QUERY = """
(
site:myworkdayjobs.com
OR site:job-boards.greenhouse.io
OR site:jobs.ashbyhq.com
OR site:jobs.lever.co
OR site:workable.com
OR site:careers-page.com
)
AND
(
inurl:jobs
OR inurl:job
OR inurl:application
OR inurl:/j/
OR inurl:apply
)
AND
'Engineer' AND 'Remote' AND -onsite AND -hybrid
"""
pattern = r"(http[s|]?:\/\/jobs\.ashbyhq\.com\/([^\/]+)\/|http[s|]?:\/\/jobs\.workable\.com\/view\/[^\/]+\/[^\/]+-at-([^\/]+)\/|http[s|]?:\/\/apply\.workable\.com\/([^\/]+)\/|http[s|]?:\/\/job-boards\.greenhouse\.io\/([^\/]+)\/jobs\/\d+|http[s|]?:\/\/([^.]+)\.wd[1-5]\.myworkdayjobs\.com\/|http[s|]?:\/\/jobs\.lever\.co\/([^\/]+)\/|http[s|]?:\/\/(www\.)?careers-page\.com\/([^\/]+)\/|http[s|]?:\/\/remote\.united\/([^\/]+)\/)"
DATA_FILE = 'data/jobs_data.json'

def get_serper_results_recursive(query, page=1):
    url = "https://google.serper.dev/search"
    all_results = {}
    payload = json.dumps({"q": query, "page": page, "num": 100, "type": "search", "location": "United States", "tbs": "qdr:w"})
    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        res = {
            i.get('link'): {**i
            } for i in data.get('organic', []) if i.get('link') and len(i.get('link').split('/'))
        }

        for link in res:
            match = re.search(pattern, link)
            if match:
                company = match.groups()[1:]  # Skip full match and www group
                res[link]['company_name'] = next((group for group in company if group is not None), 'Unknown Company')

        all_results.update(res)
        if res and page < 10:
            all_results.update(get_serper_results_recursive(query, page + 1))
    except Exception as e:
        print(f"Error fetching page {page}: {e}")
    
    return all_results

def load_jobs():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_jobs(jobs):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(jobs, f, indent=2)

def main():
    existing_jobs = load_jobs()
    initial_count = len(existing_jobs)
    
    new_jobs = get_serper_results_recursive(SEARCH_QUERY)
    existing_jobs.update(new_jobs)
    
    save_jobs(existing_jobs)
    
    print(f"Added {len(existing_jobs) - initial_count} new jobs")
    print(f"Total jobs: {len(existing_jobs)}")

if __name__ == "__main__":
    main()