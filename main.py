from datetime import datetime
import os
from pathlib import Path
import constants
import streamlit as st
import pymongo
from schema import User

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

def applicant_profile_setup_page():
    st.title("Welcome to TalentSwipe! Complete Your Profile 🧑‍💻")
    
    with st.form("profile_form"):
        name = st.text_input("Full Name")
        dob = st.date_input("Date of Birth")
        sex = st.selectbox("Sex", ["Male", "Female", "Other"])
        resume = st.file_uploader("Upload Resume (PDF)")
        
        if st.form_submit_button("Save Profile"):
            resume_path = save_uploaded_file(resume)
            #mongodb only accepts datetime
            dob_formatted = datetime(dob.year, dob.month, dob.day)
            profile_data = {
                'name': name,
                'dob': dob_formatted,
                'sex': sex,
                'resume_path': resume_path
            }
            users_collection.update_one(
                {'_id': st.session_state['user']['_id']},
                {'$set': {'profile': profile_data}}
            )
            st.session_state['profile_complete'] = True
            st.rerun()

def job_page():
    st.title("Job Page")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login_page()
    else:
        if st.session_state['user']['role'] == 'applicant':
            if not st.session_state["profile_complete"]:
                applicant_profile_setup_page()
            else:
                job_page()
        else:  # recruiter
            pass

if __name__ == "__main__":
    main()