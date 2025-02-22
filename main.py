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

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        login_page()
    else:
        st.title("You are logged in as: " + st.session_state['user']['email'])

if __name__ == "__main__":
    main()