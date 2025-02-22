from datetime import datetime
import os
from pathlib import Path
import constants
import streamlit as st
import pymongo
from schema import User, Application, JobPosting

def get_database():
    client = pymongo.MongoClient(constants.MONGODB_URI, server_api=pymongo.server_api.ServerApi('1'))
    return client['job_matching_db']

#init db
db = get_database()
users_collection = db['users']
jobs_collection = db['jobs']
applications_collection = db['applications']

def login_page():
    st.title("TalentSwipe 🪄: Job AI- Matching Platform")
    
    with st.form("login_form"):
        #enter login fields
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["recruiter", "applicant"])
        
        if st.form_submit_button("Login"):
            user = users_collection.find_one({'email': email, 'password': password, 'role': role})
            if user:
                st.session_state['user'] = user
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['profile_complete'] = user.get('profile') != None
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        if st.form_submit_button("Sign Up"):
            #validate fields
            if not email or not password or not role:
                st.error("Please fill in all fields")
                return
            user = User(email, password, role)
            try:
                users_collection.insert_one(user.to_dict())
            except pymongo.errors.DuplicateKeyError:
                st.error("Email already exists")
                return
            st.success("Account created successfully!")

def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        #save uploaded file to a folder
        file_path = Path("uploads") / uploaded_file.name
        os.makedirs("uploads", exist_ok=True)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return str(file_path)
    return None

def get_recommended_jobs(user):
    #return placeholder jobs
    return [
        {
            "title": "Software Engineer",
            "description": "We are looking for a talented software engineer to join our team."
        },
        {
            "title": "Data Scientist",
            "description": "We are looking for a talented data scientist to join our team."
        }
    ]

def job_page():
    st.title("Find Your Next Job")
    
    if 'recommended_jobs' not in st.session_state:
        st.session_state['recommended_jobs'] = get_recommended_jobs(st.session_state['user'])
        st.session_state['current_job_index'] = 0
    
    if st.session_state['current_job_index'] >= len(st.session_state['recommended_jobs']):
        st.write("No more jobs to show!")
        if st.button("Start Over"):
            st.session_state['recommended_jobs'] = get_recommended_jobs(st.session_state['user'])
            st.session_state['current_job_index'] = 0
            st.rerun()
        return
    
    current_job = st.session_state['recommended_jobs'][st.session_state['current_job_index']]
    
    st.write(f"## {current_job['title']}")
    st.write(current_job['description'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👎 Pass"):
            st.session_state['current_job_index'] += 1
            st.rerun()
    
    with col2:
        if st.button("👍 Apply"):
            application = Application(current_job['id'], st.session_state['user']['id'])
            applications_collection.insert_one(application.to_dict())
            st.session_state['current_job_index'] += 1
            st.success("Application submitted!")
            st.experimental_rerun()

def profile_setup_page():
    st.title("Welcome to TalentSwipe! Complete Your Profile 🧑‍💻")
    
    with st.form("profile_form"):
        name = st.text_input("Full Name")
        dob = st.date_input("Date of Birth")
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        
        #fields for diff roles
        if st.session_state['user']['role'] == 'applicant':
            resume = st.file_uploader("Upload Resume (PDF)")
            profile_fields = {
                'experience_years': st.number_input("Years of Experience", min_value=0, max_value=50),
                'education': st.text_input("Highest Education Level")
            }
        else:  # recruiter
            resume = None
            profile_fields = {
                'company_name': st.text_input("Company Name"),
                'company_description': st.text_area("Company Description"),
                'company_location': st.text_input("Company Location")
            }
        
        if st.form_submit_button("Save Profile"):
            resume_path = save_uploaded_file(resume) if resume else None
            #mongodb only accept datetime objs
            dob_formatted = datetime(dob.year, dob.month, dob.day)
            
            #base profile data
            profile_data = {
                'name': name,
                'dob': dob_formatted,
                'sex': sex
            }
            
            #role-specific field
            if st.session_state['user']['role'] == 'applicant':
                profile_data.update({
                    'resume_path': resume_path,
                    **profile_fields,
                })
            else:
                profile_data.update(profile_fields)
            
            #add profile to database
            users_collection.update_one(
                {'_id': st.session_state['user']['_id']},
                {'$set': {'profile': profile_data}}
            )
                  
            st.session_state['profile_complete'] = True
            st.success("Profile saved successfully!")
            st.rerun()

def recruiter_job_post():
    pass

def recruiter_applications():
    pass

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login_page()
    else:
        if not st.session_state["profile_complete"]:
            profile_setup_page()
        else:
            if st.session_state['user']['role'] == 'applicant':
                job_page()
            else:  # recruiter
                tab1, tab2 = st.tabs(["Add a New Job Posting 📄", "Review Applications 🔍"])
                
                with tab1:
                    recruiter_job_post()
                
                with tab2:
                    recruiter_applications()

if __name__ == "__main__":
    main()