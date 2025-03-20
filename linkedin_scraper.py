from flask import Flask, jsonify
from flask_cors import CORS
import requests
import json
import random
import time
from datetime import datetime
import urllib.parse

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# List of user agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

@app.route('/api/test')
def test():
    return jsonify({"status": "API is working!"})

def get_sample_jobs(location):
    return [
        {
            "title": f"Software Engineer in {location}",
            "company": "Sample Company",
            "location": location,
            "posted_date": "Sample Date",
            "link": "https://www.linkedin.com/jobs"
        }
    ]

def search_jobs_api(query, location):
    print(f"Searching for {query} jobs in {location}")
    
    # Use the LinkedIn Jobs Search API
    base_url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    
    # Parameters
    params = {
        "keywords": query,
        "location": location,
        "position": 1,
        "pageNum": 0,
        "start": 0
    }
    
    # Headers to make the request look like it's coming from a browser
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.linkedin.com/jobs",
        "Connection": "keep-alive",
    }
    
    try:
        # Make the request
        response = requests.get(
            base_url,
            params=params,
            headers=headers,
            timeout=10
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            # Parse the response
            jobs = []
            
            # Extract job data from the response
            try:
                # The response might be JSON or HTML
                if "application/json" in response.headers.get("Content-Type", ""):
                    data = response.json()
                    print("Received JSON response")
                else:
                    print("Received HTML response")
                    # Extract job data from HTML
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all job cards
                    job_cards = soup.find_all('div', {'class': ['job-search-card', 'base-card']})
                    print(f"Found {len(job_cards)} job cards")
                    
                    for card in job_cards[:10]:  # Limit to 10 jobs
                        try:
                            # Extract job details
                            title_elem = card.find(['h3', 'h4'], {'class': ['base-search-card__title', 'job-search-card__title']})
                            company_elem = card.find(['h4', 'h5'], {'class': ['base-search-card__subtitle', 'job-search-card__subtitle']})
                            location_elem = card.find('span', {'class': ['job-search-card__location', 'base-search-card__metadata']})
                            link_elem = card.find('a', {'class': ['base-card__full-link', 'job-search-card__link']})
                            
                            if title_elem and company_elem and location_elem and link_elem:
                                job = {
                                    'title': title_elem.text.strip(),
                                    'company': company_elem.text.strip(),
                                    'location': location_elem.text.strip(),
                                    'link': link_elem.get('href'),
                                    'posted_date': 'Recently'
                                }
                                jobs.append(job)
                                print(f"Extracted job: {job}")
                        except Exception as e:
                            print(f"Error extracting job data: {e}")
                            continue
                    
                    if not jobs:
                        print("No jobs found in HTML response")
                        return get_sample_jobs(location)
                    
                    return jobs
            except Exception as e:
                print(f"Error parsing response: {e}")
                return get_sample_jobs(location)
        else:
            print(f"Error: Received status code {response.status_code}")
            return get_sample_jobs(location)
            
    except Exception as e:
        print(f"Error making request: {e}")
        return get_sample_jobs(location)

@app.route('/api/jobs/<query>/<location>')
def get_jobs_by_location(query, location):
    print(f"Received request for {query} jobs in {location}")
    jobs = search_jobs_api(query, location)
    return jsonify(jobs)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
