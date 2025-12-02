import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq

# --- 1. SETUP ---
st.set_page_config(page_title="Divyanshu AI", page_icon="🚀")
st.title("🚀 Divyanshu's Super Fast AI")
st.caption("Powered by Groq (Latest Llama 3.3 Model)")

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Groq API Key yahan daalein:", type="password")
    st.info("Key nahi hai? [console.groq.com](https://console.groq.com/keys) se free lein.")

# --- 3. SEARCH FUNCTION ---
def search_web(query):
    try:
        return DDGS().text(query, max_results=3)
    except:
        return None

# --- 4. MAIN APP ---
query = st.text_input("Kuch bhi punchein:", placeholder="Ex: Who is the richest person in 2024?")

if query:
    if not api_key:
        st.error("⚠️ Pehle Sidebar mein Groq API Key daalein!")
    else:
        try:
            client = Groq(api_key=api_key)
            
            with st.spinner('Checking internet...'):
                # A. Search
                web_results = search_web(query)
                context = ""
                if web_results:
                    for r in web_results:
                        context += f"Info: {r['body']}\n\n"
                
                # B. Ask AI (Updated Model Name)
                prompt = f"""
                You are Divyanshu's AI assistant.
                Question: {query}
                Info: {context}
                
                Answer in Hinglish (Hindi + English mix).
                """
                
                # --- FIX: Newest Model ---
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile", 
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                
                # C. Show Answer
                response = completion.choices[0].message.content
                st.success("✅ Jawab:")
                st.write(response)
                
        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.write("Shayad API Key galat hai, check karein.")