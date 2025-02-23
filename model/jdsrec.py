import spacy
from collections import defaultdict
import pandas as pd
from PyPDF2 import PdfReader
import os
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


nlp = spacy.load("en_core_web_lg")
sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

DEGREE_PATTERN = re.compile(r"(Ph\.?D|Doctorate|Master'?s?|M\.?S|MBA|Bachelor'?s?|B\.?S|B\.?A|Associate'?s?)\s*(degree)?", re.IGNORECASE)

def load_skill_dataset():
        df = pd.read_csv('model/related_skills.csv')
        all_skills = set()
        for skills in df.values:
            all_skills.update([skill.lower() for skill in skills if isinstance(skill, str)])
        return all_skills
   
def read_pdf_resume(filename):
    """Read and extract text from PDF resume"""
    try:
        resume_text = ""
        reader = PdfReader(filename)
        for page in reader.pages:
            extracted_text = page.extract_text()
            resume_text += extracted_text
        return resume_text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

def read_job_desc(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()
        return text
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""

SKILL_DATABASE = load_skill_dataset()

def extract_key_phrases(text):
    """Case-insensitive phrase extraction"""
    doc = nlp(text.lower())
    
  
    phrases = defaultdict(set)
    patterns = [
        {"POS": {"IN": ["NOUN", "PROPN"]}, "OP": "+"},
        {"POS": "ADJ", "OP": "*"},
        {"POS": "VERB", "OP": "*"}
    ]
    matcher = spacy.matcher.Matcher(nlp.vocab)
    matcher.add("KEY_PHRASES", [patterns])
    
    for match_id, start, end in matcher(doc):
        phrase = doc[start:end].text.title()
        phrases["noun_phrases"].add(phrase)
    return phrases

def analyze_experience(text):
    """Case-insensitive experience analysis"""
    doc = nlp(text.lower())
    

    experience = defaultdict(list)
    experience.update({
        "years": 0,
        "accomplishments": [],
        "technologies": []
    })
    

    for ent in doc.ents:
        if ent.label_ == "DATE" and "year" in ent.text:
            if ent.text[0].isdigit():
                experience["years"] += int(ent.text[0])
    

    action_verbs = {"lead", "develop", "implement", "improve"}
    for sent in doc.sents:
        if any(token.lemma_ in action_verbs for token in sent):
            experience["accomplishments"].append(sent.text.capitalize())
    
  
    tech_keywords = {"python", "sql", "tensorflow", "pytorch", "tableau", "spark"}
    experience["technologies"] = [token.text.title() for token in doc 
                                 if token.lemma_ in tech_keywords]
    
    return dict(experience) 

def extract_skills(text):
    """Extract skills from text using the Kaggle dataset as reference"""
    doc = nlp(text.lower())
    found_skills = set()
    
 
    for sent in doc.sents:
       
        for token in sent:
            if token.text.lower() in SKILL_DATABASE:
                found_skills.add(token.text.lower())
            
        # Check for multi-word skills
        for i in range(len(sent)):
            for j in range(i + 1, min(i + 4, len(sent) + 1)):  
                phrase = ' '.join([token.text.lower() for token in sent[i:j]])
                if phrase in SKILL_DATABASE:
                    found_skills.add(phrase)
    
    return found_skills

def enhanced_match_score(resume_text, job_desc_text):
    """Calculate match score using Kaggle dataset skills"""

    resume_doc = nlp(resume_text.lower())
    job_doc = nlp(job_desc_text.lower())

    required_skills = extract_skills(job_desc_text)
    resume_skills = extract_skills(resume_text)
    
 
    print("\nSkill Matching Details:")
    print(f"Required Skills ({len(required_skills)}):", sorted(required_skills))
    print(f"Resume Skills ({len(resume_skills)}):", sorted(resume_skills))
    

    matching_skills = resume_skills & required_skills
    missing_skills = required_skills - resume_skills
    
    print(f"\nMatching Skills ({len(matching_skills)}):", sorted(matching_skills))
    print(f"Missing Skills ({len(missing_skills)}):", sorted(missing_skills))
    

    if required_skills:
        skill_match = len(matching_skills) / len(required_skills)
        print(f"\nSkill Match: {len(matching_skills)} matches / {len(required_skills)} required = {skill_match:.2f}")
    else:
        skill_match = 0
    
    similarity_score = resume_doc.similarity(job_doc)
    composite_score = (0.6 * skill_match + 0.4 * similarity_score)
    
    return {
        "composite_score": round(composite_score, 2),
        "skill_match": round(skill_match, 2),
        "similarity_score": round(similarity_score, 2),
        "matching_skills": sorted(list(matching_skills)),
        "missing_skills": sorted(list(missing_skills)),
        "required_skills": sorted(list(required_skills)),
        "resume_skills": sorted(list(resume_skills))
    }

def extract_name_from_text(text):
    """Extract name from resume text using NER"""
    doc = nlp(text)
    
   
    first_section = doc[:1000]
    

    names = [ent.text for ent in first_section.ents if ent.label_ == "PERSON"]
    
    if names:
    
        return names[0]
    return "Name not found"

def process_job_descs(resume_dir, job_desc_dir):
    """Process multiple resumes and return ranked results"""
    results = []
    resume_text = read_pdf_resume(resume_dir)
    
    # Get all PDF files in the directory
    job_files = [f for f in os.listdir(job_desc_dir) if f.endswith('.txt')]
    
    for job_file in job_files:
        try:
            
           
            job_desc_text = read_job_desc(os.path.join(job_desc_dir, job_file))
            if job_desc_text:
                
                match_result = enhanced_match_score(resume_text, job_desc_text)
                results.append({
                    "filename_name": job_file,
                    "extracted_name": job_file,
                    "composite_score": match_result["composite_score"],
                    "skill_match": match_result["skill_match"],
                    "similarity_score": match_result["similarity_score"],
                    "matching_skills": match_result["matching_skills"],
                    "missing_skills": match_result["missing_skills"]
                })
        except Exception as e:
            print(f"Error processing {job_file}: {e}")
    
 
    results.sort(key=lambda x: x["composite_score"], reverse=True)
    return results

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
    
    for line in job_desc_text.split('\n'):
        if any(kw in line.lower() for kw in preferred_keywords):
            preferred_section = line
            break
    
    if preferred_section:
        resume_doc = nlp(resume_text)
        preferred_doc = nlp(preferred_section)
        return resume_doc.similarity(preferred_doc)
    return 0.5

def calculate_composite_score(resume_text, job_desc_text):
    """Calculate final composite score"""
    processor = ResumeProcessor()
    
    # Get job requirements
    job_experience = processor.extract_experience(job_desc_text, is_job_description=True)
    required_years = job_experience['years'] or 5
    
    # Calculate score components
    sbert_similarity = enhanced_sbert_matching(resume_text, job_desc_text)
    preferred_score = calculate_preferred_score(resume_text, job_desc_text)
    
    # Skill matching
    resume_skills = processor.extract_skills(resume_text)
    job_skills = processor.extract_skills(job_desc_text)
    skill_match = len(resume_skills & job_skills) / max(len(job_skills), 1)
    
    # Experience and education
    candidate_experience = processor.extract_experience(resume_text)
    experience_score = min(candidate_experience['years'] / max(required_years, 1), 1.0)
    education = processor.extract_education(resume_text)
    
    return (
        0.2 * sbert_similarity +
        0.40 * skill_match +
        0.10 * experience_score +
        0.10 * education['score'] +
        0.2 * preferred_score +
        0.1
    )

def rank_jds(resume_path, job_list):
    """Rank job descriptions against a single resume"""
    resume_text = read_pdf_resume(resume_path)
    
    if not resume_text:
        print("Error: Could not read resume")
        return []
    results = []
    
    # for jd_file in os.listdir(jd_dir):
    for job in job_list:
        jd_text = job['description']
            
        # with open(os.path.join(jd_dir, jd_file), 'r', encoding='utf-8') as f:
        #     jd_text = f.read()
        
        score = calculate_composite_score(resume_text, jd_text)
        doc = nlp(jd_text)
        job_title = next((ent.text for ent in doc.ents if ent.label_ == "JOB_TITLE"), "Unknown Position")
        
        # results.append({
        #     'job_title': job_title,
        #     'score': round(score, 2),
        #     'file': jd_file
        # })

        results.append({
            "id": job["id"],
            "score": round(score, 2),
        })
    
    return sorted(results, key=lambda x: x['score'], reverse=True)

# if __name__ == "__main__":
#     resume_path = "/Users/sainandhan/Desktop/Jobs/WisResume.pdf"
#     jd_dir = "/Users/sainandhan/Desktop/Jobs/JD"
    
#     # Read resume once
#     resume_text = read_pdf_resume(resume_path)
    
#     if not resume_text:
#         print("Error: Could not read resume")
#     else:
#         rankings = rank_jds(resume_text, jd_dir)
        
#         print("\nTop Job Opportunities:")
#         for i, job in enumerate(rankings[:10], 1):
#             print(f"{i}. {job['file']} - Score: {job['score']} ({job['file']})")


