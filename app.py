import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Human-Like AI Avatar Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for Premium Gemini/Claude UI & Video Avatar Styling
st.markdown(
    """
    <style>
    .main { background-color: #131314; color: #e3e3e3; font-family: sans-serif; }
    
    /* Top Human-Like Avatar Video Box */
    .avatar-hero-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #1f2022, #2d2e30);
        padding: 20px;
        border-radius: 20px;
        border: 2px solid #8ab4f8;
        box-shadow: 0 10px 30px rgba(0,0,0,0.7);
        margin-bottom: 25px;
    }
    .video-frame {
        width: 100%;
        max-width: 360px;
        height: 220px;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 6px 15px rgba(0,0,0,0.5);
    }
    .avatar-status {
        margin-top: 12px;
        background: #34a853;
        color: white;
        padding: 4px 16px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: white;
        border-radius: 50%;
        animation: blink 1s infinite alternate;
    }
    @keyframes blink {
        0% { opacity: 0.3; }
        100% { opacity: 1; }
    }

    /* Agent Activity Card */
    .agent-card {
        background-color: #1e1f20;
        border: 1px solid #444746;
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #1e1f20 !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #555 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 🔑 अपनी Gemini API Key यहाँ सीधे लिख दें (ताकि बार-बार डालनी न पड़े)
# ==========================================
MY_API_KEY = (  # अपनी असली key यहाँ कोट्स के अंदर पेस्ट कर दें
    "AIzaSy..."
)

if MY_API_KEY and MY_API_KEY != "AIzaSy...":
  genai.configure(api_key=MY_API_KEY)
  model = genai.GenerativeModel("gemini-1.5-flash")
else:
  st.warning(
      "⚠️ कृपया कोड के अंदर 'MY_API_KEY' में अपनी असली Gemini API Key डालें।"
  )

# App Title
st.markdown(
    "<h1 style='text-align: center; color: white;'>🤖 Real Human-Like AI"
    " Executive Agent</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; color: #9aa0a6;'>आपका पर्सनल वर्चुअल"
    " ह्यूमन एजेंट जो ट्रेंड्स, गाने, रील्स और सोशल मीडिया मैनेज करेगा।</p>",
    unsafe_allow_html=True,
)

# --- 1. REAL HUMAN-LIKE AVATAR SECTION (TOP) ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
  st.markdown(
      """
        <div class="avatar-hero-container">
            <div class="video-frame">
                <!-- Human-like AI Anchor Video Loop -->
                <video width="100%" height="100%" autoplay loop muted playsinline>
                    <source src="https://assets.mixkit.co/videos/preview/mixkit-digital-animation-of-a-woman-with-neon-lights-41270-large.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            <div class="avatar-status">
                <div class="pulse-dot"></div> AI Human Avatar Online & Listening
            </div>
        </div>
        """,
      unsafe_allow_html=True,
  )

# --- 2. MULTI-AGENT LIVE ACTION BOARD ---
st.markdown(
    """
<div class="agent-card">
    <h3 style="margin-top:0; color:#8ab4f8; font-size:18px;">⚡ Background Autonomous Agents at Work:</h3>
    <p style="margin:5px 0; font-size:14px; color:#c4c7c5;">🔍 <b>Trend Hunter:</b> Scanning YouTube & Instagram algorithms...</p>
    <p style="margin:5px 0; font-size:14px; color:#c4c7c5;">📱 <b>Social Manager:</b> Ready to queue posts for YouTube, FB & Insta...</p>
    <p style="margin:5px 0; font-size:14px; color:#c4c7c5;">🎵 <b>Music Agent:</b> Standby to search & play requested tracks...</p>
</div>
""",
    unsafe_allow_html=True,
)

# --- 3. TABS FOR ALL FEATURES ---
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "💬 Voice & Text Chat",
        "🔥 Viral Trends & Reel Ideas",
        "🎵 Song Search & Player",
        "📱 Social Media & Hashtags",
    ]
)

# TAB 1: CHAT WITH AGENT
with tab1:
  st.subheader("💬 Talk with your Human-Like AI Agent")
  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input(
      "एजेंट से कहें (जैसे: आज क्या ट्रेंड कर रहा है? या गाना बजाओ)..."
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      if not MY_API_KEY or MY_API_KEY == "AIzaSy...":
        resp = "कृपया कोड में अपनी Gemini API Key सेट करें।"
      else:
        try:
          with st.spinner("AI Agent processing..."):
            res = model.generate_content(
                "You are an advanced human-like AI manager. Reply helpfully"
                f" in Hinglish/Hindi: {prompt}"
            )
            resp = res.text
        except Exception as e:
          resp = f"Error: {e}"
      st.markdown(resp)
      st.session_state.messages.append({"role": "assistant", "content": resp})

# TAB 2: TRENDS & REEL IDEAS
with tab2:
  st.subheader("🔥 Viral Trend & Reel Idea Generator")
  niche_input = st.text_input(
      "अपनी निच (Niche) लिखें (जैसे: Tech, Comedy, Finance, Vlogs)"
  )
  if st.button("ट्रेंडिंग टॉपिक्स खोजें"):
    if MY_API_KEY and niche_input:
      with st.spinner("Trend Agent इंटरनेट खंगाल रहा है..."):
        res = model.generate_content(
            f"As a viral growth expert, give 3 top trending topics, hooks, and"
            f" strategy for: {niche_input}"
        )
        st.success("✅ आपके लिए वायरल आइडिया:")
        st.markdown(res.text)
    else:
      st.error("कृपया निच (Niche) लिखें और API Key सेट करें।")

# TAB 3: SONG & MUSIC PLAYER
with tab3:
  st.subheader("🎵 Dynamic Song Search & Player")
  song_q = st.text_input(
      "जो गाना सुनना है उसका नाम लिखें (जैसे: Lofi songs या कोई भी गाना)"
  )
  if st.button("गाना चलाएं"):
    if song_q:
      st.success(f"🎵 Music Agent ने '{song_q}' ढूंढ लिया है:")
      enc_q = song_q.replace(" ", "+")
      st.markdown(
          f"""
            <iframe width="100%" height="315" src="https://www.youtube.com/embed?listType=search&list={enc_q}" 
            title="Music Player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen>
            </iframe>
            """,
          unsafe_allow_html=True,
      )
    else:
      st.error("कृपया गाने का नाम दर्ज करें।")

# TAB 4: SOCIAL MEDIA & HASHTAGS
with tab4:
  st.subheader("📱 Social Media Manager & Hashtag Generator")
  sm_topic = st.text_input(
      "किस टॉपिक पर पोस्ट या रील्स के लिए हैशटैग चाहिए?"
  )
  if st.button("कंटेंट और हैशटैग बनाएं"):
    if MY_API_KEY and sm_topic:
      with st.spinner("Social Manager Agent काम कर रहा है..."):
        res = model.generate_content(
            f"Generate an Instagram/YouTube caption, strategy, and 30 viral"
            f" hashtags for: {sm_topic}"
        )
        st.info(res.text)
        st.success("✅ कंटेंट और हैशटैग तैयार हैं!")
    else:
      st.error("कृपया टॉपिक दर्ज करें।")
