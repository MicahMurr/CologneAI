import streamlit as st
from google import genai
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Cologne AI", page_icon="💨", layout="centered")

# Initialize the "Memory" for the step-by-step quiz
if "quiz_step" not in st.session_state:
    st.session_state.quiz_step = 0
if "preferences" not in st.session_state:
    st.session_state.preferences = {}

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
def load_cologne_data():
    try:
        df = pd.read_csv("Cologne List_rows.csv")
        df['AI_Info'] = (
            df['Brand'].astype(str) + " " + 
            df['Perfume'].astype(str) + 
            " (Rating: " + df['Rating Value'].astype(str) + 
            ", Votes: " + df['Votes'].astype(str) + ")"
        )
        return df['AI_Info'].tolist()
    except Exception as e:
        st.error(f"🚨 Error loading CSV! Details: {e}")
        st.stop()

cologne_info_list = load_cologne_data()

# --- 5. THE APP LAYOUT (TABS) ---
st.title("Cologne Search AI 💨")
st.write("Find your signature scent and the best live prices.")

# Create the 3 main navigation tabs
tab1, tab2, tab3 = st.tabs(["🎯 The AI Quiz", "🔍 Direct Search", "📚 Fragrance 101"])

# ==========================================
# TAB 1: THE STEP-BY-STEP QUIZ
# ==========================================
with tab1:
    # A list of all our questions
    questions = [
        {"key": "Gender", "title": "Who is this fragrance for?", "type": "radio", "options": ["Men", "Women", "Unisex / Anyone"]},
        {"key": "Season", "title": "What season are you shopping for?", "type": "select", "options": ["Summer", "Winter", "Spring", "Fall", "Year-round"]},
        {"key": "Budget", "title": "What is your maximum budget?", "type": "select", "options": ["Any Price", "Under $50", "$50 - $100", "$100 - $200", "$200+ (Luxury)"]},
        {"key": "Type", "title": "What type of fragrance?", "type": "select", "options": ["Any", "Designer", "Niche", "Clone / Inspiration"]},
        {"key": "Projection", "title": "How loud should it be (Projection)?", "type": "select", "options": ["Intimate", "Moderate", "Strong", "Beast Mode"]},
        {"key": "Vibe", "title": "What is the exact vibe? (Optional)", "type": "text", "placeholder": "e.g. Fresh, woody, dark, office safe..."}
    ]

    step = st.session_state.quiz_step

    # If they haven't finished the quiz yet...
    if step < len(questions):
        q = questions[step]
        st.subheader(f"Step {step + 1} of {len(questions)}")
        st.write(f"### {q['title']}")
        
        # Draw the correct type of input
        if q["type"] == "radio":
            answer = st.radio("", q["options"], key=f"q_{step}")
        elif q["type"] == "select":
            answer = st.selectbox("", q["options"], key=f"q_{step}")
        elif q["type"] == "text":
            answer = st.text_input("", placeholder=q["placeholder"], key=f"q_{step}")
            
        st.divider()
        col1, col2 = st.columns(2)
        
        # Logic for buttons
        if step == len(questions) - 1:
            if col1.button("Finish & Find Match 🚀", use_container_width=True):
                st.session_state.preferences[q["key"]] = answer
                st.session_state.quiz_step = 99 # 99 means "Go to results"
                st.rerun()
        else:
            if col1.button("Next ➡️", use_container_width=True):
                st.session_state.preferences[q["key"]] = answer
                st.session_state.quiz_step += 1
                st.rerun()
            if col2.button("Skip & Find Match Now 🚀", use_container_width=True):
                st.session_state.preferences[q["key"]] = answer
                st.session_state.quiz_step = 99
                st.rerun()

    # If they finished or skipped...
    elif step == 99:
        st.subheader("Your Custom Match")
        
        # Combine whatever answers they managed to give us into a clean list for the AI
        prefs_text = "\n".join([f"- {k}: {v}" for k, v in st.session_state.preferences.items()])
        
        prompt = f"""
        You are a luxury fragrance expert. 
        User Preferences:
        {prefs_text}
        
        Choose ONE from this list. IMPORTANT: Prioritize colognes with the HIGHEST Rating and HIGHEST Vote counts.
        List: {cologne_info_list}
        
        RULES:
        1. Line 1: EXACT NAME ONLY (Brand + Perfume name only).
        2. Line 2+: Stylish explanation of why it fits their specific preferences.
        """
        
        with st.spinner("Consulting the Sommelier..."):
            try:
                ai_response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                lines = ai_response.text.strip().split("\n")
                exact_name = lines[0].strip().replace("*", "")
                description = "\n".join(lines[1:]).strip()
                
                st.success(f"**{exact_name}**")
                st.info(description)
                
                with st.spinner("Finding the best deals..."):
                    deals = get_price_comparison(exact_name)
                    st.write("### 🛒 Live Pricing")
                    for deal in deals:
                        d1, d2, d3 = st.columns([1, 2, 1])
                        with d1: st.write(f"**{deal['price']}**")
                        with d2: st.write(f"at {deal['store']}")
                        with d3: st.link_button("View Deal", deal['link'])
                            
            except Exception as e:
                st.error(f"Error: {e}")
                
        st.divider()
        if st.button("🔄 Retake Quiz", use_container_width=True):
            st.session_state.quiz_step = 0
            st.session_state.preferences = {}
            st.rerun()

# ==========================================
# TAB 2: THE DIRECT SEARCH
# ==========================================
with tab2:
    st.subheader("Direct Cologne Search")
    st.write("Already know what you want? Skip the AI and hunt for the best price.")
    
    search_selection = st.selectbox("Search your database:", cologne_info_list)
    
    if st.button("Check Live Prices 🛒"):
        # Slice off the "(Rating: 4.5)" part so the search engine only gets the name
        clean_name = search_selection.split(" (Rating:")[0]
        
        with st.spinner(f"Searching stores for {clean_name}..."):
            deals = get_price_comparison(clean_name)
            for deal in deals:
                d1, d2, d3 = st.columns([1, 2, 1])
                with d1: st.write(f"**{deal['price']}**")
                with d2: st.write(f"at {deal['store']}")
                with d3: st.link_button("View Deal", deal['link'])

# ==========================================
# TAB 3: THE GLOSSARY
# ==========================================
with tab3:
    st.subheader("Fragrance 101")
    
    st.markdown("### 🏛️ Fragrance Types")
    st.markdown("**Designer:** Fragrances created by major fashion houses (Dior, Chanel, Versace). They are designed to be mass-appealing, high quality, and crowd-pleasers.")
    st.markdown("**Niche:** Fragrances created by specialized perfume houses (Creed, Parfums de Marly, Xerjoff). They often use higher quality, rare ingredients and create more unique, artistic, or daring scent profiles. They are usually more expensive.")
    st.markdown("**Clone / Inspiration:** Fragrances crafted by brands (Lattafa, Armaf, Dossier) specifically to mimic the scent of expensive Niche or Designer fragrances at a fraction of the cost.")
    
    st.divider()
    
    st.markdown("### 🔊 Projection (Sillage)")
    st.markdown("**Intimate:** Sits close to the skin. Someone has to lean in to smell you (perfect for dates or strict offices).")
    st.markdown("**Moderate:** Projects about an arm's length away. Leaves a polite, subtle scent trail.")
    st.markdown("**Strong:** Leaves a noticeable trail when you walk by. People will smell you when you enter a room.")
    st.markdown("**Beast Mode:** Extremely powerful. Fills the entire room and commands attention. Apply with caution!")
