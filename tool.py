import streamlit as st
from duckduckgo_search import DDGS
from groq import Groq

# --- 1. CONFIG (Wide Layout for better view) ---
st.set_page_config(page_title="Divyanshu's Super AI", page_icon="🤖", layout="wide")

# --- 2. STYLE (Better Look) ---
st.markdown("""
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 700;
        background: -webkit-linear-gradient(left, #4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-title {
        text-align: center;
        color: #555;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }
    .stImage img {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown('<div class="main-title">🤖 Divyanshu\'s Super AI Search</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Text, Images & Videos - Powered by Groq & DuckDuckGo</div>', unsafe_allow_html=True)

# --- 4. SECRETS CHECK ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ GROQ_API_KEY not found in Secrets!")
    st.stop()

client = Groq(api_key=api_key)

# --- 5. CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 6. DISPLAY HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "images" in message and message["images"]:
            st.write("*Images:*")
            cols = st.columns(len(message["images"]))
            for i, img_url in enumerate(message["images"]):
                with cols[i]:
                    st.image(img_url, use_column_width=True)
        if "videos" in message and message["videos"]:
            st.write("*Videos:*")
            for video_url in message["videos"]:
                # YouTube videos को एम्बेड करें, बाकियों का लिंक दें
                if "youtube.com" in video_url or "youtu.be" in video_url:
                    st.video(video_url)
                else:
                    st.markdown(f"- [Watch Video]({video_url})")


# --- 7. MAIN LOGIC ---
if prompt := st.chat_input("Ask anything... (e.g., 'funny cats', 'how to make tea')"):

    # A. User Msg Show
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # B. AI Processing
    with st.chat_message("assistant"):
        with st.spinner("Searching everything..."):
            ddgs = DDGS()
            
            # 1. Image Search (4 Photos)
            image_urls = []
            try:
                img_results = ddgs.images(prompt, max_results=4)
                if img_results:
                    # Thumbnails का उपयोग करें क्योंकि वे हमेशा लोड होते हैं
                    image_urls = [img['thumbnail'] for img in img_results]
            except Exception as e:
                pass

            # 2. Video Search (2 Videos)
            video_urls = []
            try:
                video_results = ddgs.videos(prompt, max_results=2)
                if video_results:
                    video_urls = [vid['content'] for vid in video_results]
            except Exception as e:
                pass

            # 3. Text Search
            text_context = ""
            try:
                txt_results = ddgs.text(prompt, max_results=3)
                if txt_results:
                    for r in txt_results:
                        text_context += f"Info: {r['body']}\n"
            except Exception as e:
                text_context = "No text info found."

            # 4. Display Images first
            if image_urls:
                st.write("*Images:*")
                cols = st.columns(len(image_urls))
                for i, img_url in enumerate(image_urls):
                    with cols[i]:
                        st.image(img_url, use_column_width=True)

            # 5. Display Videos next
            if video_urls:
                st.write("*Videos:*")
                for video_url in video_urls:
                    if "youtube.com" in video_url or "youtu.be" in video_url:
                        st.video(video_url)
                    else:
                        st.markdown(f"- [Watch Video]({video_url})")

            # 6. Generate & Display Text Answer
            full_prompt = f"""
            User Question: {prompt}
            Internet Info: {text_context}
            Answer in Hinglish (Hindi+English). Be helpful and concise. Do not mention about images or videos in the text response, they are already displayed.
            """

            # Stream Response (Typewriter effect)
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

    # Save to History
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "images": image_urls,
        "videos": video_urls
    })

# --- SIDEBAR FOR CLEAR CHAT ---
with st.sidebar:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    st.info("Built by Code Crafter Divyanshu. Now with Text, Image, and Video Search!")
