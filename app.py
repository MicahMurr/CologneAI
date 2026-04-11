import streamlit as st
from google import genai
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Cologne AI", page_icon="💨", layout="centered")

# --- 2. CONNECT TO KEYS ---
try:
    gemini_key = st.secrets["GEMINI_KEY"]
    serpapi_key = st.secrets["SERPAPI_KEY"]
    client = genai.Client(api_key=gemini_key)
except KeyError:
    st.error("🚨 API Keys missing! Add GEMINI_KEY and SERPAPI_KEY to Streamlit Secrets.")
    st.stop()

# --- 3. THE PRICE SCRAPER ---
def get_price_comparison(cologne_name):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_shopping",
        "q": cologne_name,
        "hl": "en",
        "gl": "us",
        "api_key": serpapi_key
    }
    
    fallback_link = f"https://www.google.com/search?tbm=shop&q={cologne_name.replace(' ', '+')}"
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        deals = []
        if "shopping_results" in data:
            for result in data["shopping_results"][:3]:
                price = result.get("price")
                source = result.get("source")
                link = result.get("link") or result.get("product_link")
                if price and source and link:
                    deals.append({"price": price, "store": source, "link": link})
            if deals:
                return deals
    except Exception:
        pass
        
    return [{"price": "Check Price", "store": "Google Shopping", "link": fallback_link}]

# --- 4. LOAD DATABASE ---
@st.cache_data
def load_cologne_list():
    try:
        # Loading the specific file you mentioned
        df = pd.read_csv("Cologne List_rows.csv")
        
        # Combining Brand and the new "Perfume" header
        df['Full_Name'] = df['Brand'].astype(str) + " " + df['Perfume'].astype(str)
        return df['Full_Name'].tolist()
    except Exception as e:
        st.error(f"🚨 Error loading CSV: {e}")
        st.stop()

cologne_list = load_cologne_list()

# --- 5. UI LAYOUT ---
st.title("Cologne Search AI 💨")
st.write("Find your signature scent and the best live prices.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Fall", "Year-round"])
    longevity = st.selectbox("Longevity", ["Moderate (4-6h)", "Long-lasting (8-10h)", "Eternal (12h+)"])
    budget = st.selectbox("Max Budget", ["Any Price", "Under $50", "$50 - $100", "$100 - $200", "$200+ (Luxury)"])

with col2:
    vibe = st.text_input("The Vibe", placeholder="e.g. Fresh, woody, date night...")
    projection = st.selectbox("Projection", ["Intimate", "Moderate", "Strong", "Beast Mode"])

st.divider()

# --- 6. AI & RESULTS ---
if st.button("Find My Match & Best Prices", use_container_width=True):
    
    prompt = f"""
    You are a luxury fragrance expert. 
    User Preferences:
    - Season: {season} | Vibe: {vibe} | Longevity: {longevity} | Projection: {projection} | Budget: {budget}
    
    Choose ONE from this list: {cologne_list}
    
    Line 1: EXACT NAME ONLY.
    Line 2+: Stylish explanation of why it fits the vibe and the budget.
    """
    
    with st.spinner("Curating your match..."):
        try:
            ai_response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            lines = ai_response.text.strip().split("\n")
            exact_name = lines[0].strip().replace("*", "")
            description = "\n".join(lines[1:]).strip()
            
            st.success(f"Match Found: **{exact_name}**")
            st.info(description)
            
            # Now hunt for prices
            with st.spinner("Finding the best deals..."):
                deals = get_price_comparison(exact_name)
                st.subheader("🛒 Current Pricing & Deals")
                for deal in deals:
                    d1, d2, d3 = st.columns([1, 2, 1])
                    with d1:
                        st.write(f"**{deal['price']}**")
                    with d2:
                        st.write(f"at {deal['store']}")
                    with d3:
                        st.link_button("View Deal", deal['link'])
                        
        except Exception as e:
            st.error(f"Error: {e}")
