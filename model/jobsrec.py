import spacy
import re
import pandas as pd
import numpy as np
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_lg")
sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

DEGREE_PATTERN = re.compile(r"(Ph\.?D|Doctorate|Master'?s?|M\.?S|MBA|Bachelor'?s?|B\.?S|B\.?A|Associate'?s?)\s*(degree)?", re.IGNORECASE)


def load_skill_database():
    """Load skills from related_skills.csv"""
    df = pd.read_csv('model/related_skills.csv')
    return {skill.lower() for skills in df.values for skill in skills if isinstance(skill, str)}

SKILL_DATABASE = load_skill_database()

def read_pdf_resume(filename):
    """Extract text from PDF resume"""
    try:
        resume_text = ""
        reader = PdfReader(filename)
        for page in reader.pages:
            resume_text += page.extract_text() or ""
        return resume_text.strip()
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")
        return ""

class ResumeProcessor:
    def __init__(self):
        self.degree_scores = {
            'phd': 1.0, 'doctorate': 1.0, 'master': 0.8, 'ms': 0.8,
            'mba': 0.8, 'bachelor': 0.6, 'bs': 0.6, 'ba': 0.6, 'associate': 0.4
        }

    def extract_experience(self, text, is_job_description=False):
        """Extract experience requirements from text"""
        doc = nlp(text)
        years = 0
        
        
        patterns = [
            r"(\d+)\+? years? of experience",
            r"minimum of (\d+) years",
            r"at least (\d+) years"
        ]
        
        if is_job_description:
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    years = max(years, int(match.group(1)))
                    break
        else:
            # Extract candidate's experience from resume
            for ent in doc.ents:
                if ent.label_ == "DATE" and re.search(r'\d+', ent.text):
                    years = max(years, int(re.search(r'\d+', ent.text).group()))
        
        return {"years": years}

    def extract_education(self, text):
        """Extract education qualifications"""
        doc = nlp(text)
        matches = DEGREE_PATTERN.finditer(doc.text)
        degrees = {match.group(1).lower() for match in matches}
        score = max((self.degree_scores.get(deg, 0) for deg in degrees), default=0)
        return {'score': score}

    def extract_skills(self, text):
        """Extract skills using predefined database"""
        doc = nlp(text)
        return {token.text.lower() for token in doc if token.text.lower() in SKILL_DATABASE}

def enhanced_sbert_matching(text1, text2):
    """Calculate semantic similarity using SBERT"""
    embeddings = sentence_model.encode([text1, text2])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]

def calculate_preferred_score(resume_text, job_desc_text):
    """Calculate preferred qualifications similarity using SpaCy"""
    preferred_keywords = ["preferred qualifications", "nice to have", "desired skills"]
    preferred_section = ""
    
    # Find preferred qualifications section
    for line in job_desc_text.split('\n'):
        if any(kw in line.lower() for kw in preferred_keywords):
            preferred_section = line
            break
    
    if preferred_section:
        # Process texts with SpaCy
        resume_doc = nlp(resume_text)
        preferred_doc = nlp(preferred_section)
        
        # Calculate similarity
        return resume_doc.similarity(preferred_doc)
    
    return 0.5  # Default score if no preferred section found

def calculate_composite_score(resume_text, job_desc_text):
    """Calculate final composite score"""
    processor = ResumeProcessor()
    
    # Get job requirements
    job_experience = processor.extract_experience(job_desc_text, is_job_description=True)
    required_years = job_experience['years'] or 5  # Default to 5 years if not specified
    
    # Calculate score components
    sbert_similarity = enhanced_sbert_matching(resume_text, job_desc_text)
    preferred_score = calculate_preferred_score(resume_text, job_desc_text)
    
    # Skill matching
    resume_skills = processor.extract_skills(resume_text)
    job_skills = processor.extract_skills(job_desc_text)
    skill_match = len(resume_skills & job_skills) / max(len(job_skills), 1)
    
    # Candidate experience
    candidate_experience = processor.extract_experience(resume_text)
    experience_score = min(candidate_experience['years'] / max(required_years, 1), 1.0)
    
    # Education
    education = processor.extract_education(resume_text)

    return (
        0.2 * sbert_similarity +
        0.40 * skill_match +
        0.10 * experience_score +
        0.10 * education['score'] +
        0.2 * preferred_score +
        0.1
    )

def rank_candidates(resume_dir, job_desc_text):
    """Process and rank candidates"""
    results = []
    
    #for filename in os.listdir(resume_dir):
    for applicant in resume_dir:
        filename = applicant["resume_path"]

        if not filename.endswith('.pdf'):
            continue
            
        try:
            resume_text = read_pdf_resume(filename) #os.path.join(resume_dir, filename)
            if not resume_text:
                continue
                
            score = calculate_composite_score(resume_text, job_desc_text)
            doc = nlp(resume_text)
            #name = next((ent.text for ent in doc.ents if ent.label_ == "PERSON"), "Unknown")
            
            # results.append({
            #     'name': name,
            #     'score': round(score, 2),
            #     'file': filename
            # })

            results.append({
                "id": applicant["id"],
                "score": round(score, 2),
            })
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
    
    return sorted(results, key=lambda x: x['score'], reverse=True)

# if __name__ == "__main__":
#     job_desc = """We are seeking a Data Scientist with experience in Python, SQL, Machine Learning, and Data Visualization."""
#     resume_dir = "/Users/sainandhan/Desktop/Jobs"
    
#     rankings = rank_candidates(resume_dir, job_desc)
    
#     print("\nTop Candidates:")
#     for i, candidate in enumerate(rankings[:10], 1):
#         print(f"{i}. {candidate['name']}: {candidate['score']} ({candidate['file']})")