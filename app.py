import streamlit as st
from google import genai
import pandas as pd
import requests

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Cologne AI", page_icon="💨", layout="centered")

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
def get_price_comparison(cologne_name, search_sample=False):
    query = f"{cologne_name} sample decant" if search_sample else cologne_name
    url = "https://serpapi.com/search"
    params = {
        "engine": "google_shopping",
        "q": query,
        "hl": "en",
        "gl": "us",
        "api_key": serpapi_key
    }
    fallback_link = f"https://www.google.com/search?tbm=shop&q={query.replace(' ', '+')}"
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

# --- 5. THE BRAND HEADER & TABS ---

# THIS IS THE NEW LOGO SECTION!
head_col1, head_col2 = st.columns([1, 4]) # Gives the logo 1 part of the screen, and the title 4 parts

with head_col1:
    # A temporary sleek logo from the web. You can change this URL later!
    st.image("https://cdn-icons-png.flaticon.com/512/1005/1005749.png", width=100)

with head_col2:
    st.title("Cologne Search AI 💨")
    st.write("Find your signature scent and the best live prices.")

st.divider()

tab1, tab2, tab3 = st.tabs(["🎯 The AI Quiz", "🔍 Direct Search", "📚 Fragrance 101"])

# ==========================================
# TAB 1: THE STEP-BY-STEP QUIZ
# ==========================================
with tab1:
    questions = [
        {"key": "Gender", "title": "Who is this fragrance for?", "type": "radio", "options": ["Men", "Women"]},
        {"key": "Season", "title": "What season are you shopping for?", "type": "select", "options": ["Summer", "Winter", "Spring", "Fall", "Year-round"]},
        {"key": "Type", "title": "What type of fragrance?", "type": "select", "options": ["Any", "Designer", "Niche", "Clone / Inspiration"]},
        {"key": "Projection", "title": "How loud should it be (Projection)?", "type": "select", "options": ["Intimate", "Moderate", "Strong", "Beast Mode"]},
        {"key": "Size", "title": "Are you looking to buy a full bottle or a sample to test?", "type": "radio", "options": ["Full Bottle", "Sample / Decant"]},
        {"key": "Budget", "title": "What is your maximum budget for this size?", "type": "select", "options": ["Any Price", "Under $25", "Under $50", "$50 - $100", "$100+"]},
        {"key": "Vibe", "title": "What is the exact vibe? (Optional)", "type": "text", "placeholder": "e.g. Fresh, woody, dark, office safe..."}
    ]

    step = st.session_state.quiz_step

    if step < len(questions):
        q = questions[step]
        st.subheader(f"Step {step + 1} of {len(questions)}")
        st.write(f"### {q['title']}")
        
        if q["type"] == "radio":
            answer = st.radio("", q["options"], key=f"q_{step}")
        elif q["type"] == "select":
            answer = st.selectbox("", q["options"], key=f"q_{step}")
        elif q["type"] == "text":
            answer = st.text_input("", placeholder=q["placeholder"], key=f"q_{step}")
            
        st.divider()
        col1, col2 = st.columns(2)
        
        if step == len(questions) - 1:
            if col1.button("Finish & Find Match 🚀", use_container_width=True):
                st.session_state.preferences[q["key"]] = answer
                st.session_state.quiz_step = 99
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

    elif step == 99:
        st.subheader("Your Custom Match")
        
        prefs_text = "\n".join([f"- {k}: {v}" for k, v in st.session_state.preferences.items()])
        
        prompt = f"""
        You are a luxury fragrance expert. 
        User Preferences:
        {prefs_text}
        
        Choose ONE from this list. IMPORTANT: Prioritize colognes with the HIGHEST Rating and HIGHEST Vote counts.
        List: {cologne_info_list}
        
        RULES:
        1. GENDER RULE: If the user selected 'Men', you may choose men's fragrances OR unisex fragrances that lean masculine. If they selected 'Women', choose women's fragrances OR unisex fragrances that lean feminine. 
        2. BUDGET RULE: Ensure the recommendation fits the budget *for the size requested*. A sample of a $300 Niche fragrance will easily fit an "Under $50" budget.
        3. Line 1: EXACT NAME ONLY (Brand + Perfume name only).
        4. Line 2+: Stylish explanation of why it fits their preferences.
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
                    wants_sample = st.session_state.preferences.get("Size") == "Sample / Decant"
                    deals = get_price_comparison(exact_name, search_sample=wants_sample)
                    
                    if wants_sample:
                        st.write("### 🧪 Best Sample / Decant Prices")
                    else:
                        st.write("### 🛒 Best Full Bottle Prices")
                        
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
    
    bottle_size = st.radio("What are you looking for?", ["Full Bottle", "Sample / Decant"], horizontal=True)
    
    if st.button("Check Live Prices 🛒"):
        clean_name = search_selection.split(" (Rating:")[0]
        wants_sample = (bottle_size == "Sample / Decant")
        
        with st.spinner(f"Searching stores for {clean_name}..."):
            deals = get_price_comparison(clean_name, search_sample=wants_sample)
            for deal in deals:
                d1, d2, d3 = st.columns([1, 2, 1])
                with d1: st.write(f"**{deal['price']}**")
                with d2: st.write(f"at {deal['store']}")
                with d3: st.link_button("View Deal", deal['link'])

# ==========================================
# TAB 3: THE GLOSSARY
# ==========================================
with tab3:
    st.subheader("The Sommelier's Glossary")
    st.write("Everything you need to know to shop like an expert.")
    
    st.markdown("### 💧 Concentration Levels (How long it lasts)")
    st.markdown("**Eau de Toilette (EDT):** The standard. Lighter and fresher. Usually lasts 3 to 5 hours. Great for the office or warm weather.")
    st.markdown("**Eau de Parfum (EDP):** The sweet spot. Higher oil concentration, meaning it projects better and usually lasts 6 to 8 hours. The standard for luxury scents.")
    st.markdown("**Parfum / Extrait de Parfum:** The heaviest hitter. Highest oil concentration. It sits a bit closer to the skin but lasts 10 to 24+ hours. Very rich and dense.")

    st.divider()

    st.markdown("### 🎼 The Fragrance Pyramid (How it changes)")
    st.markdown("**Top Notes (The Opening):** What you smell in the first 15 minutes. Usually fresh, citrusy, or sharp. *Never buy a cologne based purely on the top note!*")
    st.markdown("**Heart Notes (The Core):** What it smells like for the next 2 to 4 hours. This is the true 'personality' of the scent.")
    st.markdown("**Base Notes (The Dry Down):** The foundation. These are the heavy woods, musks, and vanillas that linger on your skin for the rest of the day.")

    st.divider()

    st.markdown("### 🏛️ Fragrance Categories")
    st.markdown("**Designer:** Created by major fashion houses (Dior, Chanel). Mass-appealing, high quality, and designed to get compliments.")
    st.markdown("**Niche:** Created by specialized perfume houses (Creed, Parfums de Marly). They use rare ingredients and take artistic risks. More expensive and unique.")
    st.markdown("**Clone / Inspiration:** Crafted by brands (Lattafa, Armaf) to mimic expensive Niche or Designer fragrances at a fraction of the cost.")

    st.divider()
    
    st.markdown("### 🧬 Fragrance Families (Accords)")
    st.markdown("**Gourmand:** Scents that smell 'edible.' Think vanilla, chocolate, coffee, caramel, and honey. Very popular in winter and for date nights.")
    st.markdown("**Fougère (Fern):** The classic 'barbershop' smell. Clean, green, shaving-cream vibes. Usually features lavender and oakmoss. Extremely masculine and office-safe.")
    st.markdown("**Aquatic / Marine:** Smells like the ocean, sea salt, or a fresh shower. The ultimate summer scent profile.")
    st.markdown("**Amber (Oriental):** Warm, spicy, and exotic. Features resins, cinnamon, cardamom, and incense. Heavy and mysterious.")

    st.divider()

    st.markdown("### 🤫 Pro Terminology & Secrets")
    st.markdown("**Decant:** A smaller, sample-sized vial (usually 2ml, 5ml, or 10ml) of a luxury fragrance. The perfect way to test an expensive scent without buying a full bottle.")
    st.markdown("**Sillage (See-yazh):** Often confused with projection. Projection is how far the scent pushes off you when standing still. *Sillage* is the invisible scent trail you leave behind in the air when you walk past someone.")
    st.markdown("**Maceration (Maturation):** Letting a cologne 'sit.' Sometimes, brand-new bottles (especially Clones) smell harsh on day one. Spraying it 5-10 times and leaving it in a dark drawer for a month allows the oils to mix and smooth out.")
    st.markdown("**Blind Buy:** Buying a fragrance without ever smelling it first (which our AI is here to help you do safely!).")
    st.markdown("**Reformulation:** When a brand secretly changes the recipe of a classic cologne to comply with chemical laws or save money. This is why a bottle from 2015 might last longer than a bottle bought today.")
    st.markdown("**Flanker:** A sequel or spin-off of a popular cologne (e.g., *Bleu de Chanel* has an EDT, EDP, and Parfum version).")
    st.markdown("**Pulse Points:** The best places to spray cologne because the body heat helps push the scent into the air (Neck, behind the ears, inner wrists, and inner elbows).")
