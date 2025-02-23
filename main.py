from datetime import datetime
import time
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
            'id': "Vagina",
            'title': "Software Engineer",
            'description': "Data Scientist Affinity Solutions Marketing Cloud seeks smart, curious, technically savvy candidates join cutting-edge data science team. hire best brightest give opportunity work industry-leading technologies. The data sciences team AFS/Marketing Cloud build models, machine learning algorithms power ad-tech/mar-tech products scale, develop methodology tools precisely effectively measure market campaign effects, research in-house public data sources consumer spend behavior insights. role, opportunity come new ideas solutions lead improvement ability target right audience, derive insights provide better measurement methodology marketing campaigns. You'll access core data asset machine learning infrastructure power ideas. Duties Responsibilities Support clients model building needs, including maintaining improving current modeling/scoring methodology processes, Provide innovative solutions customized modeling/scoring/targeting appropriate ML/statistical tools, Provide analytical/statistical support marketing test design, projection, campaign measurement, market insights clients stakeholders. Mine large consumer datasets cloud environment support hoc business statistical analysis, Develop Improve automation capabilities enable customized delivery analytical products clients, Communicate methodologies results management, clients none technical stakeholders. Basic Qualifications Advanced degree Statistics/Mathematics/Computer Science/Economics fields requires advanced training data analytics. Being able apply basic statistical/ML concepts reasoning address solve business problems targeting, test design, KPI projection performance measurement. Entrepreneurial, highly self-motivated, collaborative, keen attention detail, willingness capable learn quickly, ability effectively prioritize execute tasks high pressure environment. Being flexible accept different task assignments able work tight time schedule. Excellent command one programming languages; preferably Python, SAS Familiar one database technologies PostgreSQL, MySQL, write basic SQL queries Great communication skills (verbal, written presentation) Preferred Qualifications Experience exposure large consumer and/or demographic data sets. Familiarity data manipulation cleaning routines techniques.",
            'recruiter_id': 1,
            'job_qualities': "Pussy",
            'questions': ["Mei ci dou xiang zhuang", "Do you shave your pussy"],
            'created_at': datetime.now()
        },
        {
            'id': "Dildo",
            "title": "Data Scientist",
            "description": "We are looking for a talented data scientist to join our team.",
            'recruiter_id': 2,
            'job_qualities': "Pussy",
            'questions': [],
            'created_at': datetime.now()
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

    # Custom CSS for a card-like interface
    st.markdown(
        f"""
        <div style="
            border: 2px solid #ddd; 
            border-radius: 12px; 
            color: black;
            padding: 20px; 
            margin: 20px 0px; 
            background-color: white; 
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        ">
            <h2>{current_job['title']}</h2>
            <p>{current_job['description']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, _, col2 = st.columns([2, 10, 2])

    with col1:
        if st.button("👎 Pass"):
            st.session_state['current_job_index'] += 1
            st.session_state['show_modal'] = False
            st.rerun()

    with col2:
        if st.button("👍 Apply"):
            if len(current_job['questions']) == 0:
                application = Application(current_job['id'], st.session_state['user']['id'], [])
                applications_collection.insert_one(application.to_dict())
                st.session_state['current_job_index'] += 1
                st.success("Application submitted!")
                st.rerun()
            else:
                st.session_state['show_modal'] = True
            

    if st.session_state['show_modal']:
        st.subheader("This job requires additional information")
        
        user_inputs = []

        for i, question in enumerate(current_job['questions']):
            response = st.text_input(question, key=f"user_input_{i}")
            user_inputs.append(response)

        # st.write("Your Responses:", user_inputs)

        col3, _, col4 = st.columns([2, 10, 2])

        with col3:
            if st.button("❌ Cancel"):
                st.session_state['show_modal'] = False  # Close modal without changing job
                st.rerun()
            
        with col4:
            if st.button("✅ Submit"):
                st.session_state['user_response'] = user_inputs  # Store response
                st.session_state['show_modal'] = False  # Close modal
                application = Application(current_job['id'], st.session_state['user']['id'], user_inputs)
                applications_collection.insert_one(application.to_dict())
                st.session_state['current_job_index'] += 1
                st.success("Application submitted!")
                st.rerun()

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
            time.sleep(2)
            st.rerun()

def recruiter_job_post():
    st.title("Add a New Job Posting 📄")
    
    # Initialize questions list in session state if it doesn't exist
    if 'job_questions' not in st.session_state:
        st.session_state.job_questions = []
        
    with st.form("job_posting_form"):
        st.subheader("Basic Information")
        title = st.text_input("Job Title")
        description = st.text_area("Job Description")
        job_qualities = st.text_input("What qualities are you looking for in applicants?")


        st.subheader("Screening Questions")
        st.write("Add questions you'd like to ask applicants")
        # Display each question field
        for i, question in enumerate(st.session_state.job_questions):
            st.text_input(
                f"Question {i+1}",
                value=question,
                key=f"question_{i}"
            )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            add_question = st.form_submit_button("Add Question")
        with col2:
            remove_question = st.form_submit_button("Remove Last Question")    

        if add_question:
            st.session_state.job_questions.append("")
            st.rerun()
            
        if remove_question and len(st.session_state.job_questions) > 0:
            st.session_state.job_questions.pop()
            st.rerun()

        submit_form = st.form_submit_button("Submit Job Posting")
            
        if submit_form:
            # Get updated questions from form
            updated_questions = []
            for i in range(len(st.session_state.job_questions)):
                question = st.session_state[f"question_{i}"]
                if question.strip():
                    updated_questions.append(question)
            
            # Create and save job posting
            job = JobPosting(
                title=title,
                description=description,
                job_qualities=job_qualities,
                recruiter_id=st.session_state['user']['id'],
                questions=updated_questions
            )
            jobs_collection.insert_one(job.to_dict())
            
            # Reset questions
            st.session_state.job_questions = [""]
            
            st.success("Job posted successfully!")
            time.sleep(2)
            st.rerun()

def application_status_page():
    st.title("Application Status 📝")
    st.write("Check the status of your applications here.")
    # Perform the aggregation pipeline to join jobs_collection
    applications = applications_collection.aggregate([
        {
            "$match": {"applicant_id": st.session_state['user']['id']}
        },
        {
            "$lookup": {
                "from": "jobs",  # The collection to join with
                "localField": "job_id",     # Field in applications_collection
                "foreignField": "id",       # Matching field in jobs_collection
                "as": "job_details"         # Output array containing job details
            }
        }
    ])

    for application in applications:
        job_details = application.get("job_details", [])
        
        # Safely extract the first job if it exists, otherwise skip
        if not job_details:
            continue
        job = job_details[0]
        job_title = job.get("title", "Unknown Job")
        job_description = job.get("description", "No description available")
        job_posted_date = job.get("created_at", None)

        formatted_job_date = (
            job_posted_date.strftime("%m/%d/%Y %I:%M %p")
            if job_posted_date else "Unknown Date"
        )

        application_date = application.get("created_at", None)
        formatted_app_date = (
            application_date.strftime("%m/%d/%Y %I:%M %p")
            if application_date else "Unknown Date"
        )

        with st.container():
            st.markdown(
                f"""
                <div style="
                    border: 1px solid #ddd;
                    border-radius: 10px;
                    padding: 15px;
                    margin: 10px 0;
                    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
                    background-color: #f9f9f9;
                    color: #333;
                ">
                    <h3 style="color: #333;">{job_title}</h3>
                    <p><b>Job Description:</b> {job_description[:150]}...</p>
                    <p><b>Job Posted:</b> {formatted_job_date}</p>
                    <p><b>Status:</b> <span style="color: {'green' if application['status'] == 'Accepted' else 'red' if application['status'] == 'Rejected' else 'blue'};">
                        {application['status']}
                    </span></p>
                    <p><b>Date Applied:</b> {formatted_app_date}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

def recruiter_applications():
    pass

def main():
    if 'show_modal' not in st.session_state:
        st.session_state['show_modal'] = False
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login_page()
    else:
        if not st.session_state["profile_complete"]:
            profile_setup_page()
        else:
            if st.session_state['user']['role'] == 'applicant':
                tab1, tab2 = st.tabs(["Application Status 📝", "Job Swipe 👆"])
                with tab1:
                    application_status_page()
                with tab2:
                    job_page()
            else:  # recruiter
                tab1, tab2 = st.tabs(["Add a New Job Posting 📄", "Review Applications 🔍"])
                with tab1:
                    recruiter_job_post()
                
                with tab2:
                    recruiter_applications()

if __name__ == "__main__":
    main()