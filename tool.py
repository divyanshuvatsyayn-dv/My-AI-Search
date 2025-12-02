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
    .image-box {
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<div class="main-title">🤖 Divyanshu AI Pro</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">With Image Search & Live Answers</div>', unsafe_allow_html=True)
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
        # Show images if stored in history
        if "images" in message and message["images"]:
            cols = st.columns(len(message["images"]))
            for i, img_url in enumerate(message["images"]):
                with cols[i]:
                    st.image(img_url, use_container_width=True)

# --- 6. MAIN LOGIC ---
if prompt := st.chat_input("Kuch puchiye... (Ex: Show me Ferrari car images)"):
    
    # A. User Msg Show
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # B. AI Processing
    with st.chat_message("assistant"):
        
        # 1. Image Search (New Feature) 🖼️
        image_urls = []
        with st.status("Searching Internet & Images...", expanded=True) as status:
            try:
                # Fetch Images
                img_results = DDGS().images(prompt, max_results=3)
                if img_results:
                    image_urls = [img['image'] for img in img_results]
                
                # Fetch Text
                txt_results = DDGS().text(prompt, max_results=3)
                context = ""
                if txt_results:
                    for r in txt_results:
                        context += f"Info: {r['body']}\n"
                
                status.update(label="Found results!", state="complete", expanded=False)
            except:
                context = "No results found."

        # 2. Display Images First
        if image_urls:
            cols = st.columns(len(image_urls))
            for i, img_url in enumerate(image_urls):
                with cols[i]:
                    st.image(img_url, use_container_width=True)

        # 3. Generate Answer
        full_prompt = f"""
        User Question: {prompt}
        Internet Info: {context}
        Answer in Hinglish (Hindi+English). Be helpful.
        """
        
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": full_prompt}],
            stream=True
        )
        
        # Typewriter Effect
        response_placeholder = st.empty()
        full_response = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                full_response += content
                response_placeholder.markdown(full_response + "▌")
        
        response_placeholder.markdown(full_response)
            
    # Save to History
    st.session_state.messages.append({
        "role": "assistant", 
        "content": full_response,
        "images": image_urls  # Saving images to history
    })
