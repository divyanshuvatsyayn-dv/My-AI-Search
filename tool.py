import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq

# --- 1. CONFIG ---
st.set_page_config(page_title="Divyanshu Super AI", page_icon="🎯", layout="wide")

# --- 2. STYLE ---
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(left, #000046, #1CB5E0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .sub-title {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<div class="main-title">🎯 Divyanshu\'s Accurate AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">High Accuracy Mode | Text, Images & Videos</div>', unsafe_allow_html=True)

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
                if "youtube.com" in vid or "youtu.be" in vid:
                    st.video(vid)
                else:
                    st.markdown(f"[Watch Video]({vid})")

# --- 6. MAIN LOGIC ---
if prompt := st.chat_input("Sahi jaankari puchiye... (Ex: Govindganj vidhansabha kaha hai?)"):

    # User Msg
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI Processing
    with st.chat_message("assistant"):
        with st.spinner("Checking facts carefully..."):
            ddgs = DDGS()
            
            # 1. Text Search (More Results = Better Accuracy)
            text_context = ""
            try:
                # --- FIX: Increased results to 6 for better context ---
                txt_results = ddgs.text(prompt, max_results=6)
                if txt_results:
                    for r in txt_results:
                        text_context += f"Fact: {r['body']}\n"
            except:
                text_context = "No text info found."

            # 2. Image Search
            image_urls = []
            try:
                img_results = ddgs.images(prompt, max_results=3)
                if img_results:
                    image_urls = [img['thumbnail'] for img in img_results]
            except:
                pass

            # 3. Video Search
            video_urls = []
            try:
                vid_results = ddgs.videos(prompt, max_results=1)
                if vid_results:
                    video_urls = [v['content'] for v in vid_results]
            except:
                pass

            # 4. Show Media
            if image_urls:
                cols = st.columns(len(image_urls))
                for i, img in enumerate(image_urls):
                    with cols[i]:
                        st.image(img, use_container_width=True)
            
            if video_urls:
                for vid in video_urls:
                    if "youtube.com" in vid or "youtu.be" in vid:
                        st.video(vid)

            # 5. Strict Prompt for Accuracy
            full_prompt = f"""
            Role: You are a strictly factual AI assistant.
            User Question: {prompt}
            
            Verified Internet Facts:
            {text_context}
            
            Instructions:
            1. Use ONLY the 'Verified Internet Facts' above to answer.
            2. If the facts mention the district, state it clearly.
            3. Do not guess. If the district is not mentioned in facts, say "Mujhe pakka nahi pata" or search results check karne ko kahein.
            4. Answer in Hinglish (Hindi+English).
            """

            # --- FIX: Low Temperature (0.2) reduces hallucinations ---
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.2, 
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
