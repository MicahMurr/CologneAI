import streamlit as st
from google import genai
import pandas as pd

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Cologne Finder", page_icon="💨")

# --- 2. CONNECT TO GOOGLE ---
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
        df = pd.read_csv("Cologne List_rows.csv")
        df['Full_Name'] = df['Brand'].astype(str) + " " + df['Name'].astype(str)
        return df['Full_Name'].tolist()
    except FileNotFoundError:
        st.error("🚨 Could not find 'Cologne List_rows.csv'. Make sure it is uploaded to your GitHub repository!")
        st.stop()

cologne_list = load_cologne_list()

# --- 4. THE QUIZ UI ---
st.title("Find Your Signature Scent 💨")
st.write("Take the quiz below, and our AI Sommelier will find your perfect match.")

st.subheader("Tell us what you are looking for:")

# The Inputs
season = st.selectbox("What season is this for?", ["Summer", "Winter", "Spring", "Fall", "Year-round"])
vibe = st.selectbox("What is the vibe?", ["Date Night", "Office/Professional", "Casual Everyday", "Loud & Noticed", "Fresh & Clean"])
longevity = st.selectbox("How long should it last? (Longevity)", ["Moderate (4-6 hours)", "Long-lasting (8+ hours)", "Eternal (12+ hours)"])

# CHANGED: This is now a free-form text box!
projection = st.text_input("How loud should it be? (Projection)", placeholder="e.g. Skin scent, beast mode, fills the room...")

# --- 5. THE SEARCH ENGINE ---
if st.button("Find My Signature Scent"):
    
    # We feed all 4 of their choices directly into the AI's brain
    prompt = f"""
    You are an expert fragrance sommelier. 
    I need a specific cologne recommendation from you based on these exact preferences:
    - Season: {season}
    - Vibe: {vibe}
    - Desired Longevity: {longevity}
    - Desired Projection: {projection}
    
    Here is the ONLY list of colognes you are allowed to choose from: 
    {cologne_list}
    
    Please pick exactly ONE fragrance from that list that best matches ALL of these criteria. 
    Tell me the name of the cologne clearly, and write a short, exciting paragraph explaining why the notes fit the vibe, and how its performance matches their longevity and projection requests.
    """
    
    with st.spinner("Consulting the fragrance experts..."):
        try:
            ai_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            st.success("We found your match!")
            st.write(ai_response.text)
            
        except Exception as e:
            st.error(f"Something went wrong with the AI: {e}")
longevity = st.selectbox("How long should it last? (Longevity)", ["Moderate (4-6 hours)", "Long-lasting (8+ hours)", "Eternal (12+ hours)"])
projection = st.selectbox("How loud should it be? (Projection)", ["Intimate (Skin scent)", "Moderate (Arm's length)", "Strong (Leaves a trail)", "Beast Mode (Fills the room)"])

# --- 5. THE SEARCH ENGINE ---
if st.button("Find My Signature Scent"):
    
    # We feed all 4 of their choices directly into the AI's brain
    prompt = f"""
    You are an expert fragrance sommelier. 
    I need a specific cologne recommendation from you based on these exact preferences:
    - Season: {season}
    - Vibe: {vibe}
    - Desired Longevity: {longevity}
    - Desired Projection: {projection}
    
    Here is the ONLY list of colognes you are allowed to choose from: 
    {cologne_list}
    
    Please pick exactly ONE fragrance from that list that best matches ALL of these criteria. 
    Tell me the name of the cologne clearly, and write a short, exciting paragraph explaining why the notes fit the vibe, and how its performance matches their longevity and projection requests.
    """
    
    with st.spinner("Consulting the fragrance experts..."):
        try:
            ai_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            st.success("We found your match!")
            st.write(ai_response.text)
            
        except Exception as e:
            st.error(f"Something went wrong with the AI: {e}")
