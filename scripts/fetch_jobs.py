# scripts/fetch_jobs.py
import requests
import json
import os
from datetime import datetime
import time

SERPER_API_KEY = os.environ.get('SERPER_API_KEY')
SERPER_API_KEY2 = os.environ.get('SERPER_API_KEY2')

SEARCH_QUERY = """
(site:*.myworkdayjobs.com OR site:job-boards.greenhouse.io/*/jobs/* OR site:jobs.ashbyhq.com/*/*/application OR site:jobs.lever.com/* OR site:*.workable.com/*/j/*) AND 'engineer' AND 'Remote' AND -onsite AND -Hybrid
"""

DATA_FILE = 'data/jobs_data.json'
def get_serper_results_recursive(query, page=1):
    url = "https://google.serper.dev/search"
    all_results = {}
    payload = json.dumps({"q": query, "page": page, "num":20, "type": "search", "location": "United States"})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status
        data = response.json()
    except:
        return all_results

    # Process and append current page's results
    res = {i.get('link'): {
                'title': i.get('title', ''),
                'link': i.get('link'),
                'snippet': i.get('snippet', ''),
                'date_fetched': i.get('date')
            }
        for i in data.get('organic', []) if i.get('link', None)
    }
    all_results.update(res)
    print(len(data.get('organic', [])))
    if 'nextPageToken' in data and data['nextPageToken']:
        all_results.update(get_serper_results_recursive(query, page + 1))
    return all_results

def load_jobs():
    """Load existing jobs from file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_jobs(jobs):
    """Save jobs to file."""
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