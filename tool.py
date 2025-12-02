import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq

# --- PAGE SETUP ---
st.set_page_config(page_title="Divyanshu AI", page_icon="🚀")
st.title("🚀 Divyanshu's AI Search")
st.caption("Free for everyone! No Key needed.")

# --- GET KEY FROM SECRETS (Hidden) ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("Owner ne API Key set nahi ki hai.")
    st.stop()

# --- SEARCH FUNCTION ---
def search_web(query):
    try:
        return DDGS().text(query, max_results=3)
    except:
        return None

# --- MAIN APP ---
query = st.text_input("Kuch bhi punchein:", placeholder="Ex: Top 5 movies of 2024")

if query:
    try:
        client = Groq(api_key=api_key)
        
        with st.spinner('Thinking...'):
            # 1. Search
            results = search_web(query)
            context = ""
            if results:
                for r in results:
                    context += f"Info: {r['body']}\n\n"
            
            # 2. AI Answer
            prompt = f"User Question: {query}\nInfo: {context}\nAnswer in Hinglish:"
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            
            st.success("✅ Jawab:")
            st.write(completion.choices[0].message.content)
            
    except Exception as e:
        st.error(f"Error: {e}")
