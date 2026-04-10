import streamlit as st
from google import genai
import pandas as pd

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Cologne Finder", page_icon="💨")

# --- 2. CONNECT TO GOOGLE ---
# Grab the key from the Streamlit secret vault
try:
    gemini_key = st.secrets["GEMINI_KEY"]
    client = genai.Client(api_key=gemini_key)
except KeyError:
    st.error("🚨 API Key missing! Please add GEMINI_KEY to Streamlit Secrets.")
    st.stop()

# --- 3. LOAD YOUR DATABASE ---
@st.cache_data
def load_cologne_list():
    try:
        # Read the CSV file you uploaded earlier
        df = pd.read_csv("Cologne List_rows.csv")
        # Combine the Brand and Name columns so the AI knows exactly what it is looking at
        df['Full_Name'] = df['Brand'].astype(str) + " " + df['Name'].astype(str)
        # Turn that column into a standard Python list
        return df['Full_Name'].tolist()
    except FileNotFoundError:
        st.error("🚨 Could not find 'Cologne List_rows.csv'. Make sure it is uploaded to your GitHub repository!")
        st.stop()

# Load the list of 229 colognes
cologne_list = load_cologne_list()

# --- 4. THE QUIZ UI ---
st.title("Find Your Signature Scent 💨")
st.write("Take the quiz below, and our AI Sommelier will find your perfect match.")

st.subheader("Tell us what you are looking for:")
season = st.selectbox("What season is this for?", ["Summer", "Winter", "Spring", "Fall", "Year-round"])
vibe = st.selectbox("What is the vibe?", ["Date Night", "Office/Professional", "Casual Everyday", "Loud & Noticed", "Fresh & Clean"])

# --- 5. THE SEARCH ENGINE ---
if st.button("Find My Signature Scent"):
    
    # We build a highly specific prompt using their exact answers and your master list
    prompt = f"""
    You are an expert fragrance sommelier. 
    I need a cologne recommendation for a {vibe} setting during the {season}.
    
    Here is the ONLY list of colognes you are allowed to choose from: 
    {cologne_list}
    
    Please pick exactly ONE fragrance from that list that perfectly matches a {season} {vibe}. 
    Tell me the name of the cologne clearly, and write a short, exciting paragraph explaining exactly why the notes fit this vibe perfectly.
    """
    
    # Send it to Gemini with a loading spinner
    with st.spinner("Consulting the fragrance experts..."):
        try:
            ai_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            # Show the final result!
            st.success("We found your match!")
            st.write(ai_response.text)
            
        except Exception as e:
            st.error(f"Something went wrong with the AI: {e}")
