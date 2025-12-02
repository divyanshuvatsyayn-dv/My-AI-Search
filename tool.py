import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Divyanshu AI", page_icon="📸", layout="centered")

# --- 2. STYLING ---
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: -webkit-linear-gradient(left, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }
    .stImage {
        border-radius: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<div class="main-title">📸 Divyanshu AI Pro</div>', unsafe_allow_html=True)
st.caption("Now with WORKING Image Search & Fast Answers")

# --- 4. SECRETS CHECK ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ API Key not found! Please set GROQ_API_KEY in Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# --- 5. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Show images if they exist in history
        if "images" in message and message["images"]:
            cols = st.columns(len(message["images"]))
            for i, img_url in enumerate(message["images"]):
                with cols[i]:
                    st.image(img_url, use_container_width=True)
        # Show text
        st.markdown(message["content"])

# --- 6. MAIN APP ---
if prompt := st.chat_input("Kuch puchiye... (Ex: Taj Mahal photo)"):
    
    # User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Processing
    with st.chat_message("assistant"):
        
        # A. IMAGE SEARCH (Fixed Logic)
        image_urls = []
        try:
            # We fetch 'thumbnails' because they always load!
            img_results = DDGS().images(prompt, max_results=3)
            if img_results:
                image_urls = [img['thumbnail'] for img in img_results]
        except:
            pass # Agar image fail ho jaye to bhi text chalega

        # B. DISPLAY IMAGES (Right Now)
        if image_urls:
            cols = st.columns(len(image_urls))
            for i, img_url in enumerate(image_urls):
                with cols[i]:
                    st.image(img_url, caption="Search Result", use_container_width=True)

        # C. TEXT SEARCH & ANSWER
        with st.spinner("Writing answer..."):
            try:
                txt_results = DDGS().text(prompt, max_results=3)
                context = ""
                if txt_results:
                    for r in txt_results:
                        context += f"Info: {r['body']}\n"
            except:
                context = "No text info found."

            full_prompt = f"""
            User Question: {prompt}
            Internet Info: {context}
            
            Task: Answer the user's question in Hinglish. 
            Note: I have already shown images to the user, so DO NOT print image links in the text. Just describe the topic.
            """
            
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )
            
            response_placeholder = st.empty()
            full_response = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
    # Save History
    st.session_state.messages.append({
        "role": "assistant", 
        "content": full_response,
        "images": image_urls
    })
