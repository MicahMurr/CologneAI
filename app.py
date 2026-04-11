import streamlit as st
from google import genai
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Cologne AI", page_icon="💨", layout="centered")

# --- 2. CONNECT TO GOOGLE & SERPAPI ---
try:
    gemini_key = st.secrets["GEMINI_KEY"]
    serpapi_key = st.secrets["SERPAPI_KEY"]
    client = genai.Client(api_key=gemini_key)
except KeyError:
    st.error("🚨 API Keys missing! Add GEMINI_KEY and SERPAPI_KEY to Streamlit Secrets.")
    st.stop()

# --- 3. THE PRICE COMPARISON SCRAPER ---
def get_price_comparison(cologne_name):
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_shopping",
        "q": cologne_name,
        "hl": "en",
        "gl": "us",
        "api_key": serpapi_key
    }
    
    # Fallback search if the API returns zero specific store results
    fallback_link = f"https://www.google.com/search?tbm=shop&q={cologne_name.replace(' ', '+')}"
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        deals = []
        if "shopping_results" in data:
            # We look at the first 5 results to ensure we find real stores
            for result in data["shopping_results"][:5]:
                price = result.get("price")
                source = result.get("source")
                # Grab direct link or the product info link
                link = result.get("link") or result.get("product_link")
                
                if price and source and link:
                    deals.append({"price": price, "store": source, "link": link})
            
            # If we found at least one deal, return the list
            if deals:
                return deals
                    
    except Exception:
        pass
        
    # Standard fallback if scraping fails or returns nothing
    return [{"price": "Check Price", "store": "Google Shopping", "link": fallback_link}]

# --- 4. LOAD YOUR DATABASE ---
@st.cache_data
def load_cologne_list():
    try:
        df = pd.read_csv("Cologne List_rows.csv")
        df['Full_Name'] = df['Brand'].astype(str) + " " + df['Name'].astype(str)
        return df['Full_Name'].tolist()
    except:
        st.error("🚨 Could not find 'Cologne List_rows.csv'. Check your GitHub files!")
        st.stop()

cologne_list = load_cologne_list()

# --- 5. THE LUXURY UI ---
st.title("Cologne Search AI 💨")
st.write("Find your signature scent and the best live prices.")
st.divider()

st.subheader("What are you looking for?")

# Organize inputs into a professional 2x2 grid
col1, col2 = st.columns(2)

with col1:
    season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Fall", "Year-round"])
    longevity = st.selectbox("Longevity", ["Moderate (4-6h)", "Long-lasting (8-10h)", "Eternal (12h+)"])
    budget = st.selectbox("Max Budget", ["Any Price", "Under $50", "$50 - $100", "$100 - $200", "$200+ (Luxury)"])

with col2:
    vibe = st.text_input("The Vibe", placeholder="e.g. Fresh, woody, date night...")
    projection = st.selectbox("Projection", ["Intimate", "Moderate", "Strong", "Beast Mode"])

st.divider()

# --- 6. THE SEARCH ENGINE ---
if st.button("Find My Match & Best Prices", use_container_width=True):
    
    prompt = f"""
    You are a luxury fragrance expert. 
    User Preferences:
    - Season: {season}
    - Vibe: {vibe}
    - Longevity: {longevity}
    - Projection: {projection}
    - Budget Range: {budget}
    
    Pick ONLY ONE fragrance from this list: {cologne_list}
    
    Your recommendation MUST fit the budget range. If 'Under $50', pick a high-value 'cheapie' from the list.
    Line 1: EXACT NAME ONLY.
    Line 2+: A short, stylish explanation of why it fits the vibe and the budget.
    """
    
    with st.spinner("Curating your match..."):
        try:
            ai_response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            lines = ai_response.text.strip().split("\n")
            exact_name = lines[0].strip().replace("*", "")
            description = "\n".join(lines[1:]).strip()
            
            st.success(f"Match Found: **{exact_name}**")
            st.info(description)
            
        except Exception as e:
            st.error(f"AI Error: {e}")
            st.stop()
            
    with st.spinner("Searching for the best deals..."):
        deals = get_price_comparison(exact_name)
        
        st.subheader("🛒 Current Pricing & Deals")
        
        # Display the comparison table (Price | Store | Link Button)
        for deal in deals:
            d_col1, d_col2, d_col3 = st.columns([1, 2, 1])
            with d_col1:
                st.write(f"**{deal['price']}**")
            with d_col2:
                st.write(f"at {deal['store']}")
            with d_col3:
                st.link_button("View Deal", deal['link'])            # We take the top 3 real store results
            for result in data["shopping_results"][:3]:
                price = result.get("price")
                source = result.get("source")
                link = result.get("link") or result.get("product_link")
                if price and source and link:
                    deals.append({"price": price, "store": source, "link": link})
            return deals
    except Exception:
        pass
        
    # If no results found, return the fallback search link
    return [{"price": "Check Price", "store": "Google Shopping", "link": fallback_link}]

# --- 4. LOAD YOUR DATABASE ---
@st.cache_data
def load_cologne_list():
    try:
        df = pd.read_csv("Cologne List_rows.csv")
        df['Full_Name'] = df['Brand'].astype(str) + " " + df['Name'].astype(str)
        return df['Full_Name'].tolist()
    except:
        st.error("🚨 Could not find 'Cologne List_rows.csv'.")
        st.stop()

cologne_list = load_cologne_list()

# --- 5. THE LUXURY UI ---
st.title("Cologne Search AI 💨")
st.write("Find your signature scent and the best live prices.")
st.divider()

st.subheader("What are you looking for?")

# 2x2 Grid Layout
col1, col2 = st.columns(2)

with col1:
    season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Fall", "Year-round"])
    longevity = st.selectbox("Longevity", ["Moderate (4-6h)", "Long-lasting (8-10h)", "Eternal (12h+)"])
    budget = st.selectbox("Max Budget", ["Any Price", "Under $50", "$50 - $100", "$100 - $200", "$200+ (Luxury)"])

with col2:
    vibe = st.text_input("The Vibe", placeholder="e.g. Fresh, woody, date night...")
    projection = st.selectbox("Projection", ["Intimate", "Moderate", "Strong", "Beast Mode"])

st.divider()

# --- 6. THE SEARCH ENGINE ---
if st.button("Find My Match & Best Prices", use_container_width=True):
    
    # Prompting the AI to respect the budget
    prompt = f"""
    You are a luxury fragrance expert. 
    User Preferences:
    - Season: {season}
    - Vibe: {vibe}
    - Longevity: {longevity}
    - Projection: {projection}
    - Budget Range: {budget}
    
    Pick ONLY ONE fragrance from this list: {cologne_list}
    
    Your recommendation MUST fit the budget selected. If 'Under $50', pick a high-value 'cheapie'. 
    Line 1: EXACT NAME ONLY.
    Line 2+: A short, stylish explanation of why it fits.
    """
    
    with st.spinner("Curating your match..."):
        try:
            ai_response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            lines = ai_response.text.strip().split("\n")
            exact_name = lines[0].strip().replace("*", "")
            description = "\n".join(lines[1:]).strip()
            
            st.success(f"Match Found: **{exact_name}**")
            st.info(description)
            
        except Exception as e:
            st.error(f"AI Error: {e}")
            st.stop()
            
    with st.spinner("Searching for the best deals..."):
        deals = get_price_comparison(exact_name)
        
        st.subheader("🛒 Current Pricing & Deals")
        
        # Displaying deals in a clean table-like format
        for deal in deals:
            d_col1, d_col2, d_col3 = st.columns([1, 2, 1])
            with d_col1:
                st.write(f"**{deal['price']}**")
            with d_col2:
                st.write(f"at {deal['store']}")
            with d_col3:
                st.link_button("View Deal", deal['link'])            for result in data["shopping_results"][:3]: # Grab the top 3 deals
                price = result.get("price")
                source = result.get("source")
                link = result.get("link") or result.get("product_link")
                if price and source and link:
                    results.append({"price": price, "store": source, "link": link})
            
            if results:
                return results
                    
    except Exception:
        pass
        
    return [{"price": "Check Live", "store": "Google Shopping", "link": fallback_link}]

# --- 4. LOAD YOUR DATABASE ---
@st.cache_data
def load_cologne_list():
    try:
        df = pd.read_csv("Cologne List_rows.csv")
        df['Full_Name'] = df['Brand'].astype(str) + " " + df['Name'].astype(str)
        return df['Full_Name'].tolist()
    except:
        st.error("🚨 Could not find CSV file.")
        st.stop()

cologne_list = load_cologne_list()

# --- 5. THE LUXURY UI ---
st.title("Cologne Search AI 💨")
st.write("Your personal fragrance sommelier and price tracker.")

st.divider()

st.subheader("Personalize Your Search")

# UI Grid
col1, col2 = st.columns(2)

with col1:
    season = st.selectbox("Season", ["Summer", "Winter", "Spring", "Fall", "Year-round"])
    longevity = st.selectbox("Longevity", ["Moderate", "Long-lasting", "Eternal"])
    # NEW: Budget Feature
    budget = st.selectbox("Max Budget", ["Any Price", "Under $50", "$50 - $100", "$100 - $200", "$200+ (Luxury)"])

with col2:
    vibe = st.text_input("Vibe", placeholder="e.g. Fresh, mysterious, woody...")
    projection = st.selectbox("Projection", ["Intimate", "Moderate", "Strong", "Beast Mode"])

st.divider()

# --- 6. THE SEARCH ENGINE ---
if st.button("Find My Match & Best Prices"):
    
    prompt = f"""
    You are a luxury fragrance expert. 
    User Preferences:
    - Season: {season} | Vibe: {vibe} | Longevity: {longevity} | Projection: {projection} | Budget: {budget}
    
    List to choose from: {cologne_list}
    
    INSTRUCTION: Pick ONE fragrance that fits these criteria and the budget.
    Line 1: EXACT NAME ONLY.
    Line 2+: Why it's perfect for them.
    """
    
    with st.spinner("Analyzing fragrance notes..."):
        try:
            ai_response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
            lines = ai_response.text.strip().split("\n")
            exact_name = lines[0].strip().replace("*", "")
            description = "\n".join(lines[1:]).strip()
            
            st.success(f"Match Found: **{exact_name}**")
            st.write(description)
            
        except Exception as e:
            st.error(f"AI Error: {e}")
            st.stop()
            
    with st.spinner("Finding the best deals..."):
        deals = get_price_comparison(exact_name)
        
        st.subheader("🛒 Best Prices Found")
        
        # Display as a clean table or list of buttons
        for deal in deals:
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.write(f"**{deal['price']}**")
            with c2:
                st.write(f"at {deal['store']}")
            with c3:
                st.link_button("View Deal", deal['link'])        if "shopping_results" in data:
            # Check EVERY result until we find one with a real price and a direct store link
            for result in data["shopping_results"]:
                price = result.get("price")
                source = result.get("source")
                
                # Try to get the direct link, or the product link
                link = result.get("link") or result.get("product_link")
                
                # Only return it if it has all 3!
                if price and source and link:
                    return price, source, link
                    
    except Exception:
        pass # If the API crashes, ignore it and use the fallback
        
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
# --- 5. THE QUIZ UI ---
st.title("Find Your Signature Scent 💨")
st.write("Take the quiz below, and our AI Sommelier will find your perfect match.")

st.divider() # Adds a clean horizontal line

st.subheader("Tell us what you are looking for:")

# Create a sleek 2x2 grid layout!
col1, col2 = st.columns(2)

with col1:
    season = st.selectbox("What season is this for?", ["Summer", "Winter", "Spring", "Fall", "Year-round"])
    longevity = st.selectbox("How long should it last? (Longevity)", ["Moderate (4-6 hours)", "Long-lasting (8+ hours)", "Eternal (12+ hours)"])

with col2:
    vibe = st.text_input("What is the exact vibe?", placeholder="e.g. Dark, mysterious, office boss...")
    projection = st.selectbox("How loud should it be? (Projection)", ["Intimate (Skin scent)", "Moderate (Arm's length)", "Strong (Leaves a trail)", "Beast Mode (Fills the room)"])

st.divider() # Adds another line before the button

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
            ai_response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt
            )
            
            response_text = ai_response.text.strip()
            lines = response_text.split("\n")
            
            exact_cologne_name = lines[0].strip().replace("*", "") 
            description = "\n".join(lines[1:]).strip()
            
            st.success(f"We found your match: **{exact_cologne_name}**!")
            st.write(description)
            
        except Exception as e:
            st.error(f"Something went wrong with the AI: {e}")
            st.stop()
            
    with st.spinner("Hunting for the best live price..."):
        price, store, link = get_cheapest_price(exact_cologne_name)
        
        st.subheader("🛒 Live Pricing")
        if price != "No price found":
            st.write(f"**Best Price:** {price} at {store}")
            st.link_button(f"Buy from {store}", link)
        else:
            st.write("Could not find a reliable live price. Here is a quick link to search for it:")
            st.link_button("Search Google Shopping", link)
