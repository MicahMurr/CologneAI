import ollama
from supabase import create_client, Client

# 1. Supabase Connection (The Vault)
url = "https://xatsjhkqgazqowsyjbff.supabase.co"
key = "sb_secret_Ll1tYlxJ5bNQ-t-2s7CotA_CRfJeJXr" # Put your Supabase secret key here!
supabase: Client = create_client(url, key)

def fetch_and_analyze():
    print("🤖 Connecting to Supabase Vault...")
    response = supabase.table('Cologne List').select('*').order('Likes', desc=True).limit(5).execute()
    
    print("✅ Vault Accessed! Extracting the top 5 scents...")
    
    # Create a clean list of just the names and brands
    cologne_list = []
    for cologne in response.data:
        name = cologne.get('Name', 'Unknown')
        brand = cologne.get('Brand', 'Unknown')
        cologne_list.append(f"{name} by {brand}")
        
    user_vibe = "I need a dark, mysterious fragrance for a late-night date."
    print(f"\n👤 User asks: '{user_vibe}'")
    print("🧠 Booting up your local AI (Llama 3.2)...\n")
    
    # 2. The Prompt Engineering
    prompt = f"""
    You are 'ScentAI', a master fragrance expert. 
    Here are the top 5 highest-rated colognes in our database right now:
    {cologne_list}
    
    A user just asked: "{user_vibe}"
    
    Based ONLY on the 5 colognes listed above, pick the absolute best one for this vibe. 
    Write a punchy, persuasive 2-sentence recommendation explaining why they should wear it.
    """
    
    # 3. Generate the AI's Answer directly on your Mac hardware
    ai_response = ollama.generate(model='llama3.2', prompt=prompt)
    
    print("✨ ScentAI Recommendation:")
    print("-" * 50)
    print(ai_response['response'].strip())
    print("-" * 50)

if __name__ == "__main__":
    fetch_and_analyze()
