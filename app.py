import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Advanced Human-Like AI Avatar & Social Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Realistic Human-Like Avatar & Modern UI
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .human-avatar-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #1f2937, #111827);
        padding: 15px;
        border-radius: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.6);
        border: 2px solid #3b82f6;
        margin-bottom: 20px;
    }
    .video-frame {
        width: 100%;
        max-width: 320px;
        height: 200px;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .status-badge {
        background-color: #10b981;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        margin-top: 10px;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #1f2937;
        color: white;
        border-radius: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Sidebar for API Configuration & Permanent Session
st.sidebar.header("⚙️ Settings & API Key")
if "api_key" not in st.session_state:
  st.session_state.api_key = st.secrets.get("GEMINI_API_KEY", "")

api_key_input = st.sidebar.text_input(
    "Enter Gemini API Key",
    value=st.session_state.api_key,
    type="password",
    help="Get key from Google AI Studio",
)
if api_key_input:
  st.session_state.api_key = api_key_input
  genai.configure(api_key=st.session_state.api_key)
  model = genai.GenerativeModel("gemini-1.5-flash")

# App Header
st.title("🤖 Human-Like AI Avatar & Social Media Manager")
st.markdown(
    "आपका पर्सनल ह्यूमन-लाइक एआई एजेंट जो ट्रेंडिंग खोजेगा, गाने बजाएगा और"
    " सोशल मीडिया मैनेज करेगा।"
)

# --- REALISTIC HUMAN-LIKE AVATAR SECTION ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
  st.markdown(
      """
        <div class="human-avatar-container">
            <div class="video-frame">
                <!-- Real Human Video Anchor Loop to look like a talking human face -->
                <video width="100%" height="100%" autoplay loop muted playsinline>
                    <source src="https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-a-woman-with-neon-lights-41270-large.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            <div class="status-badge">● Live Human-Like Assistant Active</div>
        </div>
        """,
      unsafe_allow_html=True,
  )

# --- TABS FOR ALL FEATURES ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💬 AI Voice & Chat",
        "🔥 Trends & Reel Ideas",
        "🎵 Song & Music Search",
        "📱 Social Media Manager",
        "🏷️ Viral Hashtags",
    ]
)

# TAB 1: GEMINI CORE CHAT
with tab1:
  st.subheader("💬 AI Assistant Chat")
  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input(
      "अवतार से बात करें (जैसे: आज क्या ट्रेंड कर रहा है?)..."
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      if not st.session_state.get("api_key"):
        response_text = "कृपया पहले साइडबार में अपनी Gemini API Key दर्ज करें।"
      else:
        try:
          with st.spinner("Avatar is thinking..."):
            system_prompt = (
                "You are an advanced, friendly human-like AI avatar manager."
                " Help the user with social media, trending topics, song"
                " suggestions, and content creation in Hinglish/Hindi."
            )
            full_prompt = f"{system_prompt}\nUser: {prompt}"
            response = model.generate_content(full_prompt)
            response_text = response.text
        except Exception as e:
          response_text = f"Error: {str(e)}"

      st.markdown(response_text)
      st.session_state.messages.append(
          {"role": "assistant", "content": response_text}
      )

# TAB 2: TRENDS & REEL IDEAS
with tab2:
  st.subheader("🔥 Viral Trends & Reel / Video Ideas")
  st.markdown(
      "इंटरनेट पर अभी कौन सा टॉपिक सबसे ज्यादा चल रहा है, यहाँ पता करें:"
  )

  category = st.selectbox(
      "चुनें किस विषय पर ट्रेंड देखना है:",
      [
          "Tech & AI Innovation",
          "Entertainment & Comedy",
          "Finance & Startup",
          "Lifestyle & Vlogs",
          "Gaming",
      ],
  )

  if st.button("ट्रेंडिंग टॉपिक्स और रील्स आइडिया खोजें"):
    if st.session_state.get("api_key"):
      with st.spinner("इंटरनेट ट्रेंड्स खंगाले जा रहे हैं..."):
        trend_query = (
            f"Act as a professional viral growth manager. For category"
            f" '{category}', give 3 current high-view trending concepts, hooks"
            " for reels, and strategy."
        )
        res = model.generate_content(trend_query)
        st.success("✅ आपके लिए वायरल ट्रेंडिंग टॉपिक्स:")
        st.markdown(res.text)
    else:
        st.warning("कृपया पहले साइडबार में API Key डालें।")

# TAB 3: SONG & MUSIC SEARCH (Dynamic Song Player)
with tab3:
  st.subheader("🎵 Song & Music Player")
  st.markdown("आप जो गाना सुनना चाहें उसका नाम यहाँ लिखें:")

  song_name = st.text_input(
      "गाने या कलाकार का नाम लिखें (जैसे: Kesariya song या Lofi beats)"
  )

  if st.button("गाना खोजें और बजाएं"):
    if song_name:
      st.success(f"🎵 आपके लिए '{song_name}' खोजा गया:")
      # Embedding a dynamic youtube search/player view for the requested song
      query_encoded = song_name.replace(" ", "+")
      st.markdown(
          f"""
            <iframe width="100%" height="315" src="https://www.youtube.com/embed?listType=search&list={query_encoded}" 
            title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
            </iframe>
            """,
          unsafe_allow_html=True,
      )
    else:
      st.error("कृपया किसी गाने का नाम दर्ज करें।")

# TAB 4: SOCIAL MEDIA MANAGER (YouTube, FB, Insta, Twitter)
with tab4:
  st.subheader("📱 Social Media & Multi-Platform Manager")
  platform = st.selectbox(
      "प्लेटफॉर्म चुनें:",
      [
          "YouTube Studio & Video Ideas",
          "Instagram Reel & Post",
          "Facebook Page Manager",
          "Twitter / X Post",
      ],
  )
  content_topic = st.text_input("किस टॉपिक पर पोस्ट या वीडियो बनाना है?")

  if st.button("कंटेंट और स्ट्रैटेजी जनरेट करें"):
    if st.session_state.get("api_key") and content_topic:
      with st.spinner(f"{platform} के लिए बेस्ट कंटेंट तैयार हो रहा है..."):
        social_prompt = (
            f"Create an expert viral post/script, caption, and schedule"
            f" strategy for {platform} about: {content_topic}"
        )
        res = model.generate_content(social_prompt)
        st.info(res.text)
        st.success(f"✅ {platform} के लिए कंटेंट तैयार है!")
    else:
        st.warning("कृपया API Key और टॉपिक दोनों दर्ज करें।")

# TAB 5: VIRAL HASHTAGS
with tab5:
  st.subheader("🏷️ Viral Hashtag Generator")
  hashtag_topic = st.text_input("अपने वीडियो या पोस्ट का मुख्य शब्द लिखें:")

  if st.button("बेस्ट हैशटैग बनाएं"):
    if st.session_state.get("api_key") and hashtag_topic:
      with st.spinner("वायरल हैशटैग्स खोजे जा रहे हैं..."):
        hash_prompt = (
            f"Generate 30 high-ranking viral hashtags for Instagram, YouTube"
            f" Shorts, and TikTok for the topic: {hashtag_topic}"
        )
        res = model.generate_content(hash_prompt)
        st.success("✅ ये रहे आपके वायरल हैशटैग्स:")
        st.markdown(res.text)
    else:
        st.warning("कृपया टॉपिक दर्ज करें।")
