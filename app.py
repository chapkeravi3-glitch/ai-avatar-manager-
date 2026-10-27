import os
import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="AI Autonomous Executive Agent & Media Hub",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ADVANCED CUSTOM CSS FOR PREMIUM CLAUDE/GEMINI LOOK ---
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #f3f4f6; font-family: 'Inter', sans-serif; }
    .sidebar .sidebar-content { background-color: #161b22; }
    
    /* Hero Header */
    .hero-box {
        background: linear-gradient(135deg, #1f2937, #111827);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid #374151;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        gap: 25px;
        margin-bottom: 25px;
    }
    .avatar-circle {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #9333ea);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 50px;
        box-shadow: 0 0 25px rgba(59, 130, 246, 0.6);
        animation: pulse-avatar 2s infinite;
    }
    @keyframes pulse-avatar {
        0% { transform: scale(0.98); box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); }
        50% { transform: scale(1.02); box-shadow: 0 0 30px rgba(59, 130, 246, 0.8); }
        100% { transform: scale(0.98); box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); }
    }
    
    /* Agent Status Panel */
    .agent-panel {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 18px;
        border-radius: 15px;
        margin-bottom: 25px;
    }
    .agent-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 6px 0;
        border-bottom: 1px solid #21262d;
    }
    .agent-row:last-child { border-bottom: none; }
    .status-badge {
        background-color: #238636;
        color: white;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    
    /* Input Fields Customization */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #161b22 !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #30363d !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- SIDEBAR CONFIGURATION ---
st.sidebar.title("⚙️ System Configuration")
st.sidebar.markdown(
    "आपकी वही **Gemini API Key** यहाँ काम करेगी जो आपने वीडियो एडिटर ऐप में"
    " इस्तेमाल की है।"
)

# Check for environment variable or session state
if "gemini_key" not in st.session_state:
  st.session_state.gemini_key = os.environ.get("GEMINI_API_KEY", "")

api_key_input = st.sidebar.text_input(
    "Enter Gemini API Key",
    value=st.session_state.gemini_key,
    type="password",
    help="Use your Google AI Studio API Key",
)

if api_key_input:
  st.session_state.gemini_key = api_key_input
  genai.configure(api_key=st.session_state.gemini_key)
  model = genai.GenerativeModel("gemini-1.5-flash")
  st.sidebar.success("✅ API Key Configured Successfully!")
else:
  st.sidebar.warning("⚠️ कृपया अपनी API Key दर्ज करें।")

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Sub-Agent Architecture")
st.sidebar.markdown(
    """
- 🔍 **Trend Hunter**: Active (Scanning Web)
- 📱 **Social Director**: Ready (YT/Insta/FB)
- 🎵 **Audio Maestro**: Standby (Media Player)
- 🏷️ **SEO Optimizer**: Active (Hashtags)
""",
    unsafe_allow_html=True,
)

# --- MAIN HERO HEADER ---
st.markdown(
    """
    <div class="hero-box">
        <div class="avatar-circle">🤖</div>
        <div>
            <h1 style="margin:0; font-size:26px; color:#ffffff;">AI Autonomous Executive Avatar & Social Suite</h1>
            <p style="margin:5px 0 0 0; color:#8b949e;">आपका ऑल-इन-वन डिजिटल ह्यूमन एजेंट जो ट्रेंड्स खोजेगा, रील्स के आइडिया देगा, गाने प्ले करेगा और आपके सोशल मीडिया चैनल्स को मैनेज करेगा।</p>
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# --- LIVE MULTI-AGENT SWARM STATUS BOARD ---
st.markdown(
    """
<div class="agent-panel">
    <strong style="color: #58a6ff; font-size: 16px;">⚡ Multi-Agent Swarm Live Monitoring:</strong>
    <div class="agent-row" style="margin-top: 10px;">
        <span>🔍 <b>Trend & Viral Research Agent:</b> Analyzing high-view topics across internet</span>
        <span class="status-badge">ONLINE</span>
    </div>
    <div class="agent-row">
        <span>📱 <b>Social Media Manager Agent:</b> Managing YouTube, Instagram & Facebook queues</span>
        <span class="status-badge">READY</span>
    </div>
    <div class="agent-row">
        <span>🎵 <b>Music & Audio Player Agent:</b> Handling song search and direct streaming</span>
        <span class="status-badge">STANDBY</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# --- TABS FOR MODULES ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💬 Executive Chat",
        "🔥 Trend & Reel Generator",
        "🎵 Music & Song Player",
        "📱 Social Media Manager",
        "🏷️ Viral SEO & Hashtags",
    ]
)

# TAB 1: EXECUTIVE CHAT
with tab1:
  st.subheader("💬 Chat with your AI Executive Agent")
  if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

  for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if user_input := st.chat_input(
      "एजेंट को आदेश दें (जैसे: आज ट्रेंडिंग क्या है? या कोई आइडिया दो)..."
  ):
    st.session_state.chat_messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
      st.markdown(user_input)

    with st.chat_message("assistant"):
      if not st.session_state.get("gemini_key"):
        reply = "⚠️ कृपया पहले साइडबार में अपनी Gemini API Key दर्ज करें।"
      else:
        try:
          with st.spinner("Executive Agent is processing..."):
            system_instruction = (
                "You are an advanced human-like AI manager agent. You help the"
                " user manage social media, find trends, suggest music, and"
                " grow online. Answer smartly and professionally in"
                " Hinglish/Hindi."
            )
            response = model.generate_content(
                f"{system_instruction}\nUser Command: {user_input}"
            )
            reply = response.text
        except Exception as e:
          reply = f"Error communicating with Gemini: {str(e)}"

      st.markdown(reply)
      st.session_state.chat_messages.append(
          {"role": "assistant", "content": reply}
      )

# TAB 2: TRENDS & REEL IDEAS
with tab2:
  st.subheader("🔥 Viral Trend Hunter & Reel Idea Generator")
  niche_category = st.selectbox(
      "अपनी कंटेंट कैटेगरी चुनें:",
      [
          "Tech & Artificial Intelligence",
          "Entertainment & Comedy",
          "Business & Finance",
          "Lifestyle & Daily Vlogs",
          "Gaming & Streaming",
      ],
  )

  if st.button("ट्रेंडिंग टॉपिक्स और रील्स आइडिया खोजें"):
    if st.session_state.get("gemini_key"):
      with st.spinner("Trend Hunter Agent इंटरनेट खंगाल रहा है..."):
        prompt_trend = (
            f"Act as a professional viral growth expert. For the niche"
            f" '{niche_category}', provide: 1. Top 3 current high-view trending"
            " concepts, 2. Catchy Reel/Shorts hooks, 3. Viral execution"
            " strategy in Hinglish."
        )
        res = model.generate_content(prompt_trend)
        st.success("✅ आपके लिए वायरल ट्रेंडिंग टॉपिक्स और आइडिया तैयार हैं:")
        st.markdown(res.text)
    else:
      st.warning("कृपया पहले अपनी API Key सेट करें।")

# TAB 3: MUSIC & SONG PLAYER
with tab3:
  st.subheader("🎵 Dynamic Music & Song Player Agent")
  st.markdown(
      "जो भी गाना या म्यूज़िक सुनना हो उसका नाम लिखें, एजेंट तुरंत आपके लिए"
      " ढूंढ कर लिंक तैयार कर देगा:"
  )

  song_query = st.text_input(
      "गाने या कलाकार का नाम लिखें (जैसे: Lofi chill beats या Kesariya song)"
  )
  if st.button("गाना खोजें और प्ले करें"):
    if song_query:
      st.success(
          f"🎵 Audio Agent ने '{song_query}' के लिए डायरेक्ट लिंक्स ढूंढ लिए"
          " हैं:"
      )
      encoded_q = song_query.replace(" ", "+")
      yt_url = f"https://www.youtube.com/results?search_query={encoded_q}"
      spotify_url = f"https://open.spotify.com/search/{encoded_q}"

      st.markdown(
          f"""
            <div style="background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; margin-top: 15px;">
                <p style="margin-bottom: 15px; font-size: 16px;"><b>चुनें आप कहाँ सुनना चाहते हैं:</b></p>
                <a href="{yt_url}" target="_blank" style="display: inline-block; background: #ff0000; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-right: 15px; box-shadow: 0 4px 10px rgba(255,0,0,0.3);">▶ YouTube पर सुनें</a>
                <a href="{spotify_url}" target="_blank" style="display: inline-block; background: #1db954; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; box-shadow: 0 4px 10px rgba(29,185,84,0.3);">🎧 Spotify पर सुनें</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
    else:
      st.error("कृपया गाने का नाम दर्ज करें।")

# TAB 4: SOCIAL MEDIA MANAGER
with tab4:
  st.subheader("📱 Multi-Platform Social Media Manager")
  platform = st.selectbox(
      "प्लेटफॉर्म चुनें:",
      [
          "YouTube Studio Strategy & Description",
          "Instagram Reel & Post Optimizer",
          "Facebook Page Engagement Manager",
          "Twitter / X Thread Creator",
      ],
  )
  post_topic = st.text_input("किस टॉपिक पर पोस्ट या वीडियो तैयार करना है?")

  if st.button("कंटेंट और शेड्यूलिंग स्ट्रैटेजी बनाएं"):
    if st.session_state.get("gemini_key") and post_topic:
      with st.spinner("Social Manager Agent पोस्ट तैयार कर रहा है..."):
        prompt_social = (
            f"Create an expert viral post/script, caption, and schedule"
            f" strategy for {platform} about: {post_topic}"
        )
        res = model.generate_content(prompt_social)
        st.info(res.text)
        st.success(f"✅ {platform} के लिए सोशल मीडिया कंटेंट तैयार है!")
    else:
      st.warning("कृपया API Key और टॉपिक दोनों दर्ज करें।")

# TAB 5: VIRAL SEO & HASHTAGS
with tab5:
  st.subheader("🏷️ SEO & Viral Hashtag Generator")
  hashtag_keyword = st.text_input("अपने वीडियो या पोस्ट का मुख्य कीवर्ड लिखें:")

  if st.button("वायरल हैशटैग्स जनरेट करें"):
    if st.session_state.get("gemini_key") and hashtag_keyword:
      with st.spinner("SEO Agent उच्च रैंकिंग वाले हैशटैग्स खोज रहा है..."):
        prompt_hash = (
            f"Generate 30 high-ranking viral hashtags and SEO keywords for"
            f" YouTube Shorts and Instagram Reels for the topic:"
            f" {hashtag_keyword}"
        )
        res = model.generate_content(prompt_hash)
        st.success("✅ आपके लिए वायरल हैशटैग्स तैयार हैं:")
        st.markdown(res.text)
    else:
      st.warning("कृपया कीवर्ड दर्ज करें।")
