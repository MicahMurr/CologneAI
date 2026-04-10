import streamlit as st
from google import genai
from supabase import create_client, Client

# 1. Setup Connections (Using Streamlit Secrets for safety!)
url = "https://xatsjhkqgazqowsyjbff.supabase.co"
# We'll set these up in the Streamlit Dashboard later
key = st.secrets["SUPABASE_KEY"]
gemini_key = st.secrets["GEMINI_KEY"]

supabase: Client = create_client(url, key)
client = genai.Client(api_key=gemini_key)

# 2. Website Header
st.title("👃 Cologne Search")
st.write("Find your signature scent using AI.")

# 3. Fetch Data from Supabase
response = supabase.table('Cologne List').select('*').order('Likes', desc=True).limit(5).execute()
cologne_list = [f"{c['Name']} by {c['Brand']}" for c in response.data]

# 4. UI logic
user_vibe = st.text_input("What's the vibe?")

if st.button("Search"):                                                  
    prompt = f"Expertly recommend one cologne from this list: {cologne_list}" # (Keep your existing prompt line here)
    
    # NEW CODE FOR LINE 27: Use 'client' instead of 'model'
    ai_response = client.models.generate_content(
        model='gemini-1.5-flash', 
        contents=prompt
    )
    )

    
    st.success(ai_response.text)
