import streamlit as st
from google import genai
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Cologne Finder", page_icon="💨")

# --- 2. CONNECT TO GOOGLE & SERPAPI ---
try:
    gemini_key = st.secrets["GEMINI_KEY"]
    serpapi_key = st.secrets["SERPAPI_KEY"]
    client = genai.Client(api_key=gemini_key)
except KeyError:
    st.error("🚨 API Keys missing! Please make sure both GEMINI_KEY and SERPAPI_KEY are in Streamlit Secrets.")
    st.stop()

# --- 3. THE SCRAPER TOOL ---
# --- 3. THE SCRAPER TOOL ---
# --- 3. THE SCRAPER TOOL ---
def get_cheapest_price(cologne_name):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_shopping",
        "q": cologne_name,
        "hl": "en",
        "gl": "us",
        "api_key": serpapi_key
    }
    
    safe_name = cologne_name.replace(" ", "+")
    fallback_link = f"https://www.google.com/search?tbm=shop&q={safe_name}"
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if "shopping_results" in data:
            
            # THE FIX: Loop through the top 5 results to find a valid link!
            for result in data["shopping_results"][:5]:
                price = result.get("price", "N/A")
                source = result.get("source", "N/A")
                
                # If this specific result has a real link, grab it and stop looking!
                if "link" in result:
                    return price, source, result["link"]
                elif "product_link" in result:
                    return price, source, result["product_link"]
                    
    except Exception:
        pass 
        
    # If it checks all 5 and STILL fails, use the fallback
    return "No price found", "N/A", fallback_link

# --- 4. LOAD YOUR DATABASE ---
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

# --- 5. THE QUIZ UI ---
st.title("Find Your Signature Scent 💨")
st.write("Take the quiz below, and our AI Sommelier will find your perfect match.")

st.subheader("Tell us what you are looking for:")
season = st.selectbox("What season is this for?", ["Summer", "Winter", "Spring", "Fall", "Year-round"])
vibe = st.text_input("What is the exact vibe?", placeholder="e.g. Dark and mysterious, fresh out the shower, office boss...")
longevity = st.selectbox("How long should it last? (Longevity)", ["Moderate (4-6 hours)", "Long-lasting (8+ hours)", "Eternal (12+ hours)"])
projection = st.selectbox("How loud should it be? (Projection)", ["Intimate (Skin scent)", "Moderate (Arm's length)", "Strong (Leaves a trail)", "Beast Mode (Fills the room)"])

# --- 6. THE SEARCH ENGINE ---
if st.button("Find My Signature Scent"):
    
    prompt = f"""
    You are an expert fragrance sommelier. 
    I need a specific cologne recommendation from you based on these exact preferences:
    - Season: {season}
    - Vibe: {vibe}
    - Desired Longevity: {longevity}
    - Desired Projection: {projection}
    
    Here is the ONLY list of colognes you are allowed to choose from: 
    {cologne_list}
    
    CRITICAL INSTRUCTION: You must pick exactly ONE fragrance. 
    Put the EXACT NAME of the cologne on the VERY FIRST LINE of your response by itself. Do not write anything else on line 1.
    Then, starting on line 2, write a short, exciting paragraph explaining why the notes fit the vibe and performance requests.
    """
    
    with st.spinner("Consulting the fragrance experts..."):
        try:
            # 1. Ask Gemini
            ai_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            # 2. Slice the response to get the name for the scraper
            response_text = ai_response.text.strip()
            lines = response_text.split("\n")
            
            # The first line is the name, the rest is the description
            exact_cologne_name = lines[0].strip().replace("*", "") # Removes any bolding stars
            description = "\n".join(lines[1:]).strip()
            
            st.success(f"We found your match: **{exact_cologne_name}**!")
            st.write(description)
            
        except Exception as e:
            st.error(f"Something went wrong with the AI: {e}")
            st.stop()
            
    # 3. Trigger the scraper while the user is reading the review!
    with st.spinner("Hunting for the best live price..."):
        price, store, link = get_cheapest_price(exact_cologne_name)
        
        # 4. Show the final shopping card
        st.subheader("🛒 Live Pricing")
        if price != "No price found":
            st.write(f"**Best Price:** {price} at {store}")
            
            # This prints the raw web address so they can see it
            st.write(f"**Direct Link:** {link}")
            
            # This creates a nice, clickable app button!
            st.link_button("Buy Now", link)
        else:
            st.write("Could not find a reliable live price on Google Shopping. You might have to hunt for this one!")
