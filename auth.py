import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin import firestore
import bcrypt

# Import the main app function
from main_app import main_app

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),  # Handle newline correctly
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
        "universe_domain": st.secrets["firebase"]["universe_domain"]
    })
    firebase_admin.initialize_app(cred)


# Firestore to store user info
db = firestore.client()

# Function to hash the password
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

# Function to sign up a user
def sign_up(email, password):
    try:
        hashed_password = hash_password(password)
        user = auth.create_user(email=email, password=password)

        user_info = {
            'email': email,
            'hashed_password': hashed_password,
        }
        db.collection('users').document(user.uid).set(user_info)

        st.success(f"Successfully signed up as {email}")
    except Exception as e:
        st.error(f"Error creating user: {e}")

# Function to check the password
def check_password(stored_hashed_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hashed_password.encode('utf-8'))

# Function to sign in a user
def sign_in(email, password):
    try:
        user = auth.get_user_by_email(email)
        user_doc = db.collection('users').document(user.uid).get()
        if user_doc.exists:
            stored_hashed_password = user_doc.to_dict().get('hashed_password')
            if check_password(stored_hashed_password, password):
                st.session_state['user'] = user  # Set the user in session state
                st.success(f"Successfully signed in as {email}")
                return True
            else:
                st.error("Invalid password!")
                return False
        else:
            st.error("User not found!")
            return False
    except Exception as e:
        st.error(f"Error signing in: {e}")
        return False

# Streamlit UI for login and signup
def auth_page():
    # st.title("Firebase Login/Signup")

    if 'user' in st.session_state and st.session_state['user'] is not None:
        main_app()  # Call the main app function if already logged in
        return  # Prevent further execution

    # Tab-based navigation
    tab = st.sidebar.radio("Login/Signup", ["Login", "Signup"])

    if tab == "Signup":
        st.subheader("Create a new account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            sign_up(email, password)

    elif tab == "Login":
        st.subheader("Login to your account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if sign_in(email, password):
                main_app()  # Call the main app function on successful login

# Call the authentication page function
if __name__ == "__main__":
    auth_page()
