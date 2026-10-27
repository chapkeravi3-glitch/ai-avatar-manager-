import time
import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="AI Multi-Agent Studio",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Gemini/Claude Like Clean & Modern UI with Agent Status Dots
st.markdown(
    """
    <style>
    .main { background-color: #131314; color: #e3e3e3; }
    .stSidebar { background-color: #1e1f20; }
    
    /* Top Header Card */
    .hero-card {
        background: linear-gradient(135deg, #1f2022, #2d2e30);
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #444746;
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 25px;
    }
    .avatar-circle {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #8ab4f8, #c58af9);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 38px;
        box-shadow: 0 0 20px rgba(138, 180, 248, 0.4);
    }
    
    /* Multi-Agent Status Board styling */
    .agent-board {
        background-color: #1e1f20;
        border: 1px solid #333537;
        padding: 15px;
        border-radius: 12px;
        margin-top: 15px;
        margin-bottom: 20px;
    }
    .agent-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        border-bottom: 1px solid #2d2e30;
    }
    .agent-item:last-child { border-bottom: none; }
    
    /* Pulsing Status Dot */
    .dot-live {
        height: 10px;
        width: 10px;
        background-color: #34a853;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 8px #34a853;
        animation: pulse-dot 1.5s infinite;
    }
    @keyframes pulse-dot {
        0% { transform: scale(0.9); opacity: 0.7; }
        50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 12px #34a853; }
        100% { transform: scale(0.9); opacity: 0.7; }
    }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #1e1f20 !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #444746 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Sidebar Configuration
st.sidebar.title("⚙️ Multi-Agent Control")
if "api_key" not in st.session_state:
  st.session_state.api_key = st.secrets.get("GEMINI_API_KEY", "")

api_key_input = st.sidebar.text_input(
    "Gemini API Key", value=st.session_state.api_key, type="password"
)
if api_key_input:
  st.session_state.api_key = api_key_input
  genai.configure(api_key=st.session_state.api_key)
  model = genai.GenerativeModel("gemini-1.5-flash")

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Active Sub-Agents")
st.sidebar.markdown(
    """
- 🔍 **Trend Hunter Agent**: <span style='color:#34a853;'>● Online</span>
- 📱 **Social Manager Agent**: <span style='color:#34a853;'>● Online</span>
- 🎵 **Audio & Music Agent**: <span style='color:#34a853;'>● Online</span>
- 🏷️ **SEO & Hashtag Agent**: <span style='color:#34a853;'>● Online</span>
""",
    unsafe_allow_html=True,
)

# Main Header with Clean Avatar Look
st.markdown(
    """
    <div class="hero-card">
        <div class="avatar-circle">🤖</div>
        <div>
            <h2 style="margin:0; color:#f1f3f4;">AI Executive Avatar & Multi-Agent Hub</h2>
            <p style="margin:5px 0 0 0; color:#9aa0a6;">आपका डिजिटल ह्यूमन-लाइक असिस्टेंट जो रील्स, ट्रेंड्स और सोशल मीडिया को अलग-अलग एआई एजेंट्स के जरिए मैनेज करता है।</p>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- LIVE MULTI-AGENT STATUS BOARD (Showing agents working behind the scenes) ---
st.markdown(
    """
<div class="agent-board">
    <strong style="color: #8ab4f8;">⚡ Live Multi-Agent Swarm Status:</strong>
    <div class="agent-item">
        <span>🔍 Trend & Video Research Agent (Scanning internet for viral topics)</span>
        <span><span class="dot-live"></span> Active</span>
    </div>
    <div class="agent-item">
        <span>📱 Social Media Orchestrator (Managing YouTube, Instagram, FB)</span>
        <span><span class="dot-live"></span> Ready</span>
    </div>
    <div class="agent-item">
        <span>🎵 Audio & Music Player Agent (Fetching & playing requested songs)</span>
        <span><span class="dot-live"></span> Standby</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# --- TABS FOR ALL MODULES ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💬 Executive Chat",
        "🔥 Trend & Reel Generator",
        "🎵 Music & Song Player",
        "📱 Social Media Manager",
        "🏷️ Viral Hashtags",
    ]
)

# TAB 1: EXECUTIVE CHAT
with tab1:
  st.subheader("💬 Chat with AI Manager Avatar")
  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input("एजेंट से कुछ भी पूछें..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      if not st.session_state.get("api_key"):
        response_text = "कृपया पहले साइडबार में अपनी Gemini API Key दर्ज करें।"
      else:
        try:
          with st.spinner("Multi-Agent system is processing..."):
            sys_prompt = (
                "You are an advanced multi-agent AI assistant manager. Answer"
                " intelligently in Hinglish/Hindi."
            )
            response = model.generate_content(f"{sys_prompt}\nUser: {prompt}")
            response_text = response.text
        except Exception as e:
          response_text = f"Error: {str(e)}"

      st.markdown(response_text)
      st.session_state.messages.append(
          {"role": "assistant", "content": response_text}
      )

# TAB 2: TREND & REEL GENERATOR
with tab2:
  st.subheader("🔥 Trend Hunter & Reel Idea Agent")
  niche = st.selectbox(
      "अपनी कैटेगरी चुनें:",
      [
          "Tech & AI",
          "Entertainment & Comedy",
          "Finance & Business",
          "Lifestyle & Vlogs",
      ],
  )

  if st.button("ट्रेंड्स और रील्स आइडिया खोजें"):
    if st.session_state.get("api_key"):
      with st.spinner("Trend Hunter Agent काम कर रहा है..."):
        res = model.generate_content(
            f"Act as Trend Hunter Agent. For '{niche}', give 3 viral topics,"
            " high-view reel hooks, and viral strategy in Hindi/Hinglish."
        )
        st.success("✅ ट्रेंडिंग टॉपिक्स तैयार हैं:")
        st.markdown(res.text)
    else:
      st.warning("कृपया API Key दर्ज करें।")

# TAB 3: MUSIC & SONG PLAYER
with tab3:
  st.subheader("🎵 Audio & Music Player Agent")
  song_query = st.text_input(
      "कौन सा गाना या म्यूजिक सुनना है? (जैसे: Lofi beats या Kesariya song)"
  )

  if st.button("गाना चलाएं"):
    if song_query:
      st.success(
          f"🎵 Audio Agent ने आपके लिए '{song_query}' ढूंढ लिया है और प्ले कर"
          " रहा है:"
      )
      q_enc = song_query.replace(" ", "+")
      st.markdown(
          f"""
            <iframe width="100%" height="315" src="https://www.youtube.com/embed?listType=search&list={q_enc}" 
            title="Music Player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
            </iframe>
            """,
          unsafe_allow_html=True,
      )
    else:
      st.error("कृपया गाने का नाम दर्ज करें।")

# TAB 4: SOCIAL MEDIA MANAGER
with tab4:
  st.subheader("📱 Social Media Manager Agent")
  plat = st.selectbox(
      "प्लेटफॉर्म चुनें:",
      [
          "YouTube Studio Strategy",
          "Instagram Reel Manager",
          "Facebook Page Post",
      ],
  )
  topic = st.text_input("किस टॉपिक पर पोस्ट तैयार करनी है?")

  if st.button("कंटेंट और स्ट्रैटेजी बनाएं"):
    if st.session_state.get("api_key") and topic:
      with st.spinner("Social Manager Agent पोस्ट तैयार कर रहा है..."):
        res = model.generate_content(
            f"Create expert social post, caption, and schedule strategy for"
            f" {plat} about: {topic}"
        )
        st.info(res.text)
        st.success(f"✅ {plat} के लिए कंटेंट तैयार है!")
    else:
      st.warning("कृपया API Key और टॉपिक भरें।")

# TAB 5: VIRAL HASHTAGS
with tab5:
  st.subheader("🏷️ SEO & Hashtag Agent")
  ht_topic = st.text_input("कीवर्ड या टॉपिक लिखें:")

  if st.button("वायरल हैशटैग्स जनरेट करें"):
    if st.session_state.get("api_key") and ht_topic:
      with st.spinner("SEO Agent हैशटैग्स खोज रहा है..."):
        res = model.generate_content(
            f"Generate 30 top viral hashtags for YouTube Shorts and Instagram"
            f" Reels for: {ht_topic}"
        )
        st.success("✅ वायरल हैशटैग्स:")
        st.markdown(res.text)
    else:
      st.warning("कृपया टॉपिक दर्ज करें।")
