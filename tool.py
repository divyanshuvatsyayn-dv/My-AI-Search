import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq

# --- 1. CONFIG ---
st.set_page_config(page_title="Divyanshu AI", page_icon="🤖", layout="centered")

# --- 2. STYLE ---
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: -webkit-linear-gradient(left, #FF4B4B, #FF9000);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<div class="main-title">🤖 Divyanshu AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Powered by Groq & Llama 3.3 | Live Search Engine</div>', unsafe_allow_html=True)
st.markdown("---")

# --- 4. SECRETS CHECK ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ API Key not found! Please set GROQ_API_KEY in Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# --- 5. CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. MAIN LOGIC (FIXED) ---
if prompt := st.chat_input("Kuch puchiye..."):
    
    # User Msg
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Msg
    with st.chat_message("assistant"):
        with st.spinner("Searching..."):
            # Search
            try:
                results = DDGS().text(prompt, max_results=3)
                context = ""
                if results:
                    for r in results:
                        context += f"Source: {r['title']} - {r['body']}\n"
            except:
                context = "No internet results found."

            # Prompt
            full_prompt = f"""
            User Question: {prompt}
            Internet Info: {context}
            Answer in Hinglish (Hindi+English). Be helpful and concise.
            """
            
            # --- FIX: Manual Streaming ---
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )
            
            # Text ko saaf tarike se nikalna
            response_placeholder = st.empty()
            full_response = ""
            
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
    # Save AI Msg
    st.session_state.messages.append({"role": "assistant", "content": full_response})
