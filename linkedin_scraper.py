from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import random
import time
from datetime import datetime
import urllib.parse
import os
from resume_analyzer import (
    extract_text_from_pdf,
    extract_text_from_docx,
    analyze_resume,
    analyze_job_description,
    match_resume_to_job,
    customize_resume,
    recommend_companies
)
import traceback

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# List of user agents to rotate through
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/api/test')
def test():
    return jsonify({"status": "API is working!"})

@app.route('/api/analyze-resume', methods=['POST'])
def analyze_resume_endpoint():
    try:
        if 'resume' not in request.files:
            return jsonify({"error": "No resume file provided"}), 400
        
        file = request.files['resume']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save the file temporarily
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        # Extract text based on file type
        if file.filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(file_path)
        elif file.filename.endswith('.docx'):
            resume_text = extract_text_from_docx(file_path)
        else:
            return jsonify({"error": "Unsupported file format"}), 400
        
        if not resume_text:
            return jsonify({"error": "Could not extract text from resume"}), 400
        
        # Analyze resume
        analysis = analyze_resume(resume_text)
        if not analysis:
            return jsonify({"error": "Could not analyze resume"}), 500
        
        # Get company recommendations
        recommendations = recommend_companies(analysis)
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            "analysis": analysis,
            "recommendations": recommendations
        })
        
    except Exception as e:
        print(f"Error analyzing resume: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": "Resume analysis failed",
            "details": str(e),
            "stacktrace": traceback.format_exc()
        }), 500

@app.route('/api/customize-resume', methods=['POST'])
def customize_resume_endpoint():
    try:
        if 'resume' not in request.files or 'jobDescription' not in request.form:
            return jsonify({"error": "Resume file and job description required"}), 400
        
        file = request.files['resume']
        job_description = request.form['jobDescription']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save the file temporarily
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        # Extract text based on file type
        if file.filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(file_path)
        elif file.filename.endswith('.docx'):
            resume_text = extract_text_from_docx(file_path)
        else:
            return jsonify({"error": "Unsupported file format"}), 400
        
        if not resume_text:
            return jsonify({"error": "Could not extract text from resume"}), 400
        
        # Analyze both resume and job description
        resume_analysis = analyze_resume(resume_text)
        job_analysis = analyze_job_description(job_description)
        
        if not resume_analysis or not job_analysis:
            return jsonify({"error": "Analysis failed"}), 500
        
        # Get match information and customization suggestions
        match_info = match_resume_to_job(resume_analysis, job_analysis)
        customization = customize_resume(resume_text, job_description)
        
        # Clean up
        os.remove(file_path)
        
        return jsonify({
            "matchInfo": match_info,
            "customization": customization
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    ]
    
    # Use a more reliable job search URL
    jobs = []
    try:
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        
        # Try first from LinkedIn API
        url = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        params = {
            "keywords": query,
            "location": location,
            "start": 0,
            "count": 25
        }
        
        print(f"Requesting: {url} with params: {params}")
        response = requests.get(url, headers=headers, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                job_cards = soup.find_all('div', class_='base-card')
                
                if not job_cards:
                    print("No job cards found in response, content length:", len(response.text))
                    # If the response is valid but empty or wrong format, try alternate scraping technique
                    if len(job_cards) == 0:
                        # If no cards were found with the normal method, try secondary parsing
                        all_jobs = soup.find_all('li')
                        print(f"Found {len(all_jobs)} list items to try alternate parsing")
                        
                        for job in all_jobs:
                            title_elem = job.find('h3', class_='base-search-card__title')
                            company_elem = job.find('h4', class_='base-search-card__subtitle')
                            location_elem = job.find('span', class_='job-search-card__location')
                            date_elem = job.find('time', class_='job-search-card__listdate')
                            link_elem = job.find('a', class_='base-card__full-link')
                            
                            if title_elem:
                                job_data = {
                                    'title': title_elem.text.strip(),
                                    'company': company_elem.text.strip() if company_elem else 'Unknown Company',
                                    'location': location_elem.text.strip() if location_elem else location,
                                    'posted_date': date_elem.text.strip() if date_elem else 'Recently',
                                    'link': link_elem['href'] if link_elem else '',
                                    'skills': ['Python', 'JavaScript', 'React'] # Placeholder skills
                                }
                                jobs.append(job_data)
                
                # Process normal job cards if found
                for card in job_cards:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    date_elem = card.find('time', class_='job-search-card__listdate')
                    link_elem = card.find('a', class_='base-card__full-link')
                    
                    if title_elem:
                        job_data = {
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip() if company_elem else 'Unknown Company',
                            'location': location_elem.text.strip() if location_elem else location,
                            'posted_date': date_elem.text.strip() if date_elem else 'Recently',
                            'link': link_elem['href'] if link_elem else '',
                            'skills': ['Python', 'JavaScript', 'React'] # Placeholder skills
                        }
                        jobs.append(job_data)
                
                print(f"Successfully scraped {len(jobs)} jobs")
                
                # If we got at least one job, return them; otherwise fall back to samples
                if jobs:
                    return jobs
                print("No jobs found in response, falling back to samples")
                return get_sample_jobs(location)
                
            except Exception as e:
                print(f"Error parsing response: {e}")
                print("Response content (first 500 chars):", response.text[:500])
                return get_sample_jobs(location)
        else:
            print(f"Error: Received status code {response.status_code}")
            print("Response content (first 500 chars):", response.text[:500] if response.text else "Empty response")
            return get_sample_jobs(location)
            
    except Exception as e:
        print(f"Error making request: {e}")
        import traceback
        print(traceback.format_exc())
        return get_sample_jobs(location)

@app.route('/api/jobs/<query>/<location>')
def get_jobs_by_location(query, location):
    print(f"Received request for {query} jobs in {location}")
    
    # Get resume data from query parameters if available
    resume_data = request.args.get('resume_data')
    print(f"Resume data present: {resume_data is not None}")
    
    # Fetch jobs from LinkedIn API
    jobs = search_jobs_api(query, location)
    
    # Calculate match percentage for each job if resume data is available
    if resume_data:
        try:
            resume_data = json.loads(resume_data)
            print(f"Resume data parsed successfully: {type(resume_data)}")
            
            # Calculate match percentage for each job
            for job in jobs:
                match_score = match_resume_to_job(resume_data, {
                    'title': job.get('title', ''),
                    'description': job.get('description', ''),
                    'skills': job.get('skills', [])
                })
                job['match'] = int(match_score * 100)
                print(f"Match score for {job['title']}: {job['match']}%")
        except Exception as e:
            print(f"Error processing resume data: {str(e)}")
            import traceback
            print(traceback.format_exc())
            # Continue without match data if there's an error
        
    return jsonify(jobs)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
