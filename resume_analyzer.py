import os
from dotenv import load_dotenv
import openai
from PyPDF2 import PdfReader
from docx import Document
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI API
api_key = os.getenv('OPENAI_API_KEY')
if api_key and api_key != "your_api_key_here":
    openai.api_key = api_key
    API_KEY_VALID = True
else:
    API_KEY_VALID = False
    print("WARNING: No valid OpenAI API key found. Resume analysis features will return sample data.")

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def extract_text_from_docx(docx_path):
    """Extract text from a DOCX file."""
    try:
        doc = Document(docx_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX: {e}")
        return None

def get_sample_analysis():
    """Return sample resume analysis data when API key is not available."""
    return {
        "skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "Data Analysis"],
        "experience": ["Software Developer at XYZ Corp (2 years)", "Web Developer at ABC Inc (1 year)"],
        "education": ["Bachelor's in Computer Science"],
        "strengths": ["Strong problem-solving abilities", "Team collaboration", "Fast learner"],
        "areas_for_improvement": ["Could benefit from more cloud experience", "Consider adding certifications"]
    }

def get_sample_recommendations():
    """Return sample company recommendations when API key is not available."""
    return {
        "recommended_companies": [
            {"name": "Google", "reason": "Matches your skills in software development"},
            {"name": "Microsoft", "reason": "Good fit for your technical background"},
            {"name": "Amazon", "reason": "Opportunities for your web development skills"},
            {"name": "IBM", "reason": "Aligns with your data analysis experience"}
        ],
        "recommended_roles": [
            "Software Engineer",
            "Full Stack Developer",
            "Frontend Developer",
            "Backend Developer"
        ],
        "industries_to_consider": [
            "Tech",
            "E-commerce",
            "Financial Services",
            "Healthcare IT"
        ]
    }

def get_sample_match_info():
    """Return sample job match information when API key is not available."""
    return {
        "match_score": 75,
        "matching_skills": ["Python", "JavaScript", "React"],
        "missing_skills": ["AWS", "Docker"],
        "overall_assessment": "Good match with room for improvement"
    }

def get_sample_customization():
    """Return sample resume customization when API key is not available."""
    return """
# Resume Customization Suggestions

## Skills Section
- Highlight your Python and JavaScript experience prominently
- Add any projects related to web development
- Mention your experience with databases if applicable

## Experience Section
- Emphasize teamwork and collaboration aspects
- Quantify your achievements with metrics where possible
- Focus on relevant projects that match the job description

## Additional Improvements
- Add a summary section tailored to this specific role
- Consider reorganizing your skills to prioritize those mentioned in the job description
- Include relevant keywords from the job posting throughout your resume
"""

def analyze_resume(resume_text):
    """Analyze resume using OpenAI API."""
    if not API_KEY_VALID:
        print("Using sample resume analysis data (no API key)")
        return get_sample_analysis()
        
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Upgraded to GPT-4 for better analysis
            messages=[
                {"role": "system", "content": "You are a professional resume analyzer. Extract key information from the resume and format it as a JSON object with the following structure: {\"skills\": [array of skills], \"experience\": [array of experience items], \"education\": [array of education items], \"strengths\": [array of strengths], \"areas_for_improvement\": [array of areas to improve]}. Use only the information provided in the resume."},
                {"role": "user", "content": f"Analyze this resume and extract key information:\n\n{resume_text}"}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Try to parse the response as JSON, with fallback handling
        try:
            content = response.choices[0].message['content'].strip()
            # If the response has markdown code blocks, extract the JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            return json.loads(content)
        except json.JSONDecodeError:
            print(f"Error parsing JSON from OpenAI response: {content[:100]}...")
            # Extract key information with regex as fallback
            import re
            skills = re.findall(r'"skills":\s*\[(.*?)\]', content, re.DOTALL)
            skills = [s.strip(' "\'') for s in skills[0].split(',')] if skills else []
            
            return {
                "skills": skills,
                "experience": ["Experience extracted from resume"],
                "education": ["Education extracted from resume"],
                "strengths": ["Strengths identified in resume"],
                "areas_for_improvement": ["Consider adding more detail"]
            }
    except Exception as e:
        print(f"Error analyzing resume: {e}")
        import traceback
        print(traceback.format_exc())
        return get_sample_analysis()

def analyze_job_description(job_description):
    """Analyze job description using OpenAI API."""
    if not API_KEY_VALID:
        print("Using sample job analysis data (no API key)")
        return {"required_skills": ["Python", "JavaScript", "AWS", "Docker", "React"]}
        
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional job description analyzer. Extract key requirements and qualifications."},
                {"role": "user", "content": f"Analyze this job description and extract key requirements, skills, and qualifications in JSON format:\n\n{job_description}"}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return json.loads(response.choices[0].message['content'])
    except Exception as e:
        print(f"Error analyzing job description: {e}")
        return {"required_skills": ["Python", "JavaScript", "AWS", "Docker", "React"]}

def match_resume_to_job(resume_analysis, job_analysis):
    """Match resume skills to job requirements using OpenAI API."""
    if not API_KEY_VALID:
        print("Using sample match data (no API key)")
        return get_sample_match_info()
    
    # Simple matching algorithm for speed
    try:
        # Quick matching without API call for performance
        match_score = 0.5  # Default mid-range score
        
        # If skills are available from both sides, do direct matching
        if isinstance(resume_analysis, dict) and isinstance(job_analysis, dict):
            resume_skills = resume_analysis.get('skills', [])
            job_skills = job_analysis.get('skills', [])
            
            if resume_skills and job_skills:
                # Normalize skills (lowercase, remove punctuation)
                resume_skills_norm = [s.lower().strip(',.!?;:()[]{}') for s in resume_skills]
                job_skills_norm = [s.lower().strip(',.!?;:()[]{}') for s in job_skills]
                
                # Count matches
                matches = sum(1 for s in resume_skills_norm if any(js in s or s in js for js in job_skills_norm))
                if job_skills:
                    match_score = min(1.0, matches / len(job_skills) * 1.2)  # Scale up a bit, cap at 1.0
        
        # For more complex cases with good API key, use OpenAI
        if API_KEY_VALID and match_score < 0.25:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # Use GPT-4 for better matching
                    messages=[
                        {"role": "system", "content": "You are a professional resume matcher. Compare resume qualifications with job requirements and return ONLY a match score between 0.0 and 1.0, where 1.0 is a perfect match."},
                        {"role": "user", "content": f"Compare this resume with job requirements and provide a match score between 0.0 and 1.0:\n\nResume: {json.dumps(resume_analysis)}\n\nJob: {json.dumps(job_analysis)}"}
                    ],
                    temperature=0.3,
                    max_tokens=50
                )
                
                content = response.choices[0].message['content'].strip()
                # Extract just the number
                import re
                match = re.search(r'(\d+\.\d+|\d+)', content)
                if match:
                    api_score = float(match.group(1))
                    if 0 <= api_score <= 1:
                        return api_score
                    else:
                        return api_score / 100 if api_score > 1 else 0.5  # Normalize if needed
            except Exception as e:
                print(f"Error using OpenAI for match score: {e}")
                # Continue with the simpler score
        
        return match_score
        
    except Exception as e:
        print(f"Error matching resume to job: {e}")
        import traceback
        print(traceback.format_exc())
        return 0.5  # Default mid-range score

def customize_resume(resume_text, job_description):
    """Customize resume for a specific job using OpenAI API."""
    if not API_KEY_VALID:
        print("Using sample customization data (no API key)")
        return get_sample_customization()
        
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a professional resume customizer. Tailor resumes to match job requirements while maintaining honesty and authenticity."},
                {"role": "user", "content": f"Customize this resume for the following job description. Provide specific suggestions for modifications and improvements:\n\nResume:\n{resume_text}\n\nJob Description:\n{job_description}"}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error customizing resume: {e}")
        return get_sample_customization()

def recommend_companies(resume_analysis):
    """Recommend companies based on resume skills using OpenAI API."""
    if not API_KEY_VALID:
        print("Using sample company recommendations (no API key)")
        return get_sample_recommendations()
        
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career advisor specializing in tech company recommendations."},
                {"role": "user", "content": f"Based on these skills and qualifications, recommend suitable companies and roles:\n\n{json.dumps(resume_analysis)}"}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return json.loads(response.choices[0].message['content'])
    except Exception as e:
        print(f"Error recommending companies: {e}")
        return get_sample_recommendations()
