import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Divyanshu Smart AI", page_icon="🧠", layout="wide")

# --- 2. STYLING ---
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(left, #6a11cb, #2575fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .sub-title {
        text-align: center;
        color: #555;
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<div class="main-title">🧠 Divyanshu\'s Smart AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Search + Internal Knowledge | Images & Videos</div>', unsafe_allow_html=True)

# --- 4. SECRETS ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ GROQ_API_KEY nahi mili! Secrets check karein.")
    st.stop()

client = Groq(api_key=api_key)

# --- 5. HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "images" in message and message["images"]:
            cols = st.columns(len(message["images"]))
            for i, img in enumerate(message["images"]):
                with cols[i]:
                    st.image(img, use_container_width=True)
        if "videos" in message and message["videos"]:
            for vid in message["videos"]:
                if "http" in vid:
                    st.video(vid)

# --- 6. MAIN LOGIC ---
if prompt := st.chat_input("Puchiye... (Ex: Govindganj vidhansabha kaha hai?)"):

    # User Msg
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Processing
    with st.chat_message("assistant"):
        with st.spinner("Thinking & Searching..."):
            ddgs = DDGS()
            
            # 1. Search Logic
            text_context = ""
            image_urls = []
            video_urls = []

            try:
                # Text Search (Broad search)
                txt_results = ddgs.text(prompt, max_results=5)
                if txt_results:
                    for r in txt_results:
                        text_context += f"Info: {r['body']}\n"
                
                # Image Search
                img_results = ddgs.images(prompt, max_results=3)
                if img_results:
                    image_urls = [img['thumbnail'] for img in img_results]

                # Video Search
                vid_results = ddgs.videos(prompt, max_results=1)
                if vid_results:
                    video_urls = [v['content'] for v in vid_results]

            except Exception as e:
                text_context = "Search failed, using internal knowledge."

            # 2. Show Media
            if image_urls:
                cols = st.columns(len(image_urls))
                for i, img in enumerate(image_urls):
                    with cols[i]:
                        st.image(img, use_container_width=True)
            
            if video_urls:
                for vid in video_urls:
                    st.video(vid)

            # 3. SMART PROMPT (Hybrid Mode)
            full_prompt = f"""
            You are a helpful and smart AI assistant.
            User Question: {prompt}
            
            Internet Search Results:
            {text_context}
            
            INSTRUCTIONS:
            1. First, check the 'Internet Search Results' above. If the answer is there, use it.
            2. IF the answer is NOT in the search results, use your own INTERNAL KNOWLEDGE to answer correctly.
            3. Do not say "I don't know" unless it is impossible to answer.
            4. Answer in Hinglish (Hindi + English).
            """

            # 4. Generate Answer (Balanced Temperature)
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.6, # Thoda creative, thoda strict
                stream=True
            )

            # Stream Output
            response_placeholder = st.empty()
            full_response = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

    # Save
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "images": image_urls,
        "videos": video_urls
    })
