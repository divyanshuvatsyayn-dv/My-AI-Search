import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq

# --- 1. PRO PAGE CONFIG ---
st.set_page_config(page_title="Divyanshu AI", page_icon="🤖", layout="centered")

# --- 2. CUSTOM CSS (STYLING) ---
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
    .stChatInput {
        position: fixed;
        bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER UI ---
st.markdown('<div class="main-title">🤖 Divyanshu AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Powered by Groq & Llama 3.3 | Live Search Engine</div>', unsafe_allow_html=True)
st.markdown("---")

# --- 4. SECRETS MANAGEMENT ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ API Key not found in Secrets!")
    st.stop()

client = Groq(api_key=api_key)

# --- 5. CHAT HISTORY SETUP ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display old messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. MAIN CHAT LOGIC ---
if prompt := st.chat_input("Kuch puchiye... (Ex: Who won IPL 2024?)"):
    
    # User Message Show karein
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # AI Response Start
    with st.chat_message("assistant"):
        with st.spinner("Searching & Thinking..."):
            # A. Internet Search
            try:
                results = DDGS().text(prompt, max_results=3)
                context = ""
                if results:
                    for r in results:
                        context += f"[{r['title']}]({r['href']}): {r['body']}\n"
            except:
                context = "No internet results found."

            # B. Prepare Prompt
            full_prompt = f"""
            You are a smart AI assistant. 
            User Question: {prompt}
            Internet Data: {context}
            
            Answer in Hinglish (Hindi+English). Be friendly and accurate.
            Do not mention 'According to internet data' repeatedly.
            """

            # C. Generate Stream Response
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )
            
            # D. Typewriter Effect
            response = st.write_stream(stream)
            
    # Save AI Message
    st.session_state.messages.append({"role": "assistant", "content": response})

# --- SIDEBAR FOR CLEAR CHAT ---
with st.sidebar:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.info("Built by Code Crafter Divyanshu")
