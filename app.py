import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client

# 1. Setup Connections (Using Streamlit Secrets for safety!)
url = "https://xatsjhkqgazqowsyjbff.supabase.co"
# We'll set these up in the Streamlit Dashboard later
key = st.secrets["-t-2s7CotA_CRfJeJXr"]
gemini_key = st.secrets["AIzaSyBqp1CAE1lOqypwH0kFwdmr71RUzmGTGdc"]

supabase: Client = create_client(url, key)
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Website Header
st.title("👃 Cologne Search")
st.write("Find your signature scent using AI.")

# 3. Fetch Data from Supabase
response = supabase.table('Cologne List').select('*').order('Likes', desc=True).limit(5).execute()
cologne_list = [f"{c['Name']} by {c['Brand']}" for c in response.data]

# 4. UI logic
user_vibe = st.text_input("What's the vibe?")

if st.button("Search"):
    prompt = f"Expertly recommend one cologne from this list: {cologne_list} for the vibe: {user_vibe}."
    ai_response = model.generate_content(prompt)
    st.success(ai_response.text)
