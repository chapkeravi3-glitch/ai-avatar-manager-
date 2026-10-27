import os
import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Human-Like AI Avatar Executive",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 🎨 IMMERSIVE FULL-SCREEN HUMAN AVATAR CSS
# ==========================================
st.markdown(
    """
    <style>
    .main { background-color: #090a0f; color: #ffffff; font-family: 'Inter', sans-serif; }
    
    .avatar-hero-fullscreen {
        position: relative;
        width: 100%;
        height: 380px;
        background: linear-gradient(180deg, rgba(15,23,42,0.8) 0%, rgba(9,10,15,1) 100%),
                    radial-gradient(circle at center, #1e3a8a 0%, #090a0f 70%);
        border-radius: 24px;
        border: 1px solid rgba(59, 130, 246, 0.3);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        margin-bottom: 30px;
        overflow: hidden;
    }
    
    .human-face-glow {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 40px rgba(59, 130, 246, 0.6), inset 0 0 20px rgba(255,255,255,0.4);
        animation: face-pulse 3s infinite ease-in-out;
        position: relative;
    }
    
    @keyframes face-pulse {
        0% { transform: scale(1); box-shadow: 0 0 30px rgba(59, 130, 246, 0.5); }
        50% { transform: scale(1.04); box-shadow: 0 0 50px rgba(139, 92, 246, 0.8); }
        100% { transform: scale(1); box-shadow: 0 0 30px rgba(59, 130, 246, 0.5); }
    }

    .face-emoji {
        font-size: 80px;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));
    }

    .avatar-speech-bubble {
        margin-top: 20px;
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 12px 25px;
        border-radius: 30px;
        font-size: 16px;
        color: #93c5fd;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        backdrop-filter: blur(10px);
        letter-spacing: 0.5px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #12131a;
        padding: 10px;
        border-radius: 15px;
        border: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1c29;
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 600;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #12131a !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid #334155 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- GEMINI API CONFIGURATION ---
api_ready = False
if "GEMINI_API_KEY" in st.secrets:
  genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
  model = genai.GenerativeModel("gemini-1.5-flash")
  api_ready = True
else:
  st.sidebar.title("⚙️ Config")
  k_input = st.sidebar.text_input("Gemini API Key", type="password")
  if k_input:
    genai.configure(api_key=k_input)
    model = genai.GenerativeModel("gemini-1.5-flash")
    api_ready = True

# ==========================================
# 👤 FULL-SCREEN HUMAN-LIKE AVATAR HERO DISPLAY
# ==========================================
st.markdown(
    """
    <div class="avatar-hero-fullscreen">
        <div class="human-face-glow">
            <div class="face-emoji">👩‍💼</div>
        </div>
        <div class="avatar-speech-bubble">
            ✨ Namaste! I am your Autonomous Executive Human-Like AI Agent. Ready to manage your empire.
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 🗂️ TABS FOR ALL FEATURES
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💬 Executive Chat",
        "🔥 Trend & Reel Generator",
        "🎵 Music & Audio Maestro",
        "📱 Social Media Control",
        "🏷️ Viral SEO & Hashtags",
    ]
)

with tab1:
  st.subheader("💬 Direct Voice & Text Chat with Human Agent")
  if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

  for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if user_input := st.chat_input("एजेंट से कुछ भी पूछें या कमांड दें..."):
    st.session_state.chat_messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
      st.markdown(user_input)

    with st.chat_message("assistant"):
      if not api_ready:
        reply = "⚠️ कृपया `.streamlit/secrets.toml` में या साइडबार में अपनी Gemini API Key सेट करें।"
      else:
        try:
          with st.spinner("Agent is processing your command..."):
            sys_prompt = (
                "You are an advanced, human-like virtual executive manager."
                " Help the user manage social media, find trends, suggest"
                " music, and grow online. Reply smartly in Hinglish/Hindi."
            )
            response = model.generate_content(
                f"{sys_prompt}\nUser: {user_input}"
            )
            reply = response.text
        except Exception as e:
          reply = f"Error: {str(e)}"

      st.markdown(reply)
      st.session_state.chat_messages.append(
          {"role": "assistant", "content": reply}
      )

with tab2:
  st.subheader("🔥 Viral Trend Hunter & Reel Idea Generator")
  niche = st.selectbox(
      "अपनी कैटेगरी चुनें:",
      [
          "Tech & AI",
          "Entertainment & Comedy",
          "Business & Startup",
          "Lifestyle & Vlogs",
          "Gaming",
      ],
  )
  if st.button("ट्रेंडिंग टॉपिक्स और रील्स आइडिया खोजें"):
    if api_ready:
      with st.spinner("Trend Hunter इंटरनेट खंगाल रहा है..."):
        res = model.generate_content(
            f"As a viral growth expert, give 3 trending topics, high-view reel"
            f" hooks, and strategy for: {niche}"
        )
        st.success("✅ वायरल ट्रेंडिंग टॉपिक्स:")
        st.markdown(res.text)
    else:
      st.warning("API Key सेट नहीं है।")

with tab3:
  st.subheader("🎵 Dynamic Music & Song Search")
  song_q = st.text_input("जो गाना सुनना है उसका नाम लिखें:")
  if st.button("गाना ढूंढें और प्ले करें"):
    if song_q:
      st.success(f"🎵 आपके लिए '{song_q}' के लिंक्स तैयार हैं:")
      enc = song_q.replace(" ", "+")
      yt = f"https://www.youtube.com/results?search_query={enc}"
      sp = f"https://open.spotify.com/search/{enc}"
      st.markdown(
          f"""
            <div style="background: #12131a; padding: 20px; border-radius: 12px; border: 1px solid #1e293b; margin-top: 15px;">
                <p style="margin-bottom: 15px;"><b>चुनें आप कहाँ सुनना चाहते हैं:</b></p>
                <a href="{yt}" target="_blank" style="display: inline-block; background: #ef4444; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; margin-right: 15px;">▶ YouTube पर सुनें</a>
                <a href="{sp}" target="_blank" style="display: inline-block; background: #22c55e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold;">🎧 Spotify पर सुनें</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
    else:
      st.error("गाने का नाम दर्ज करें।")

with tab4:
  st.subheader("📱 Multi-Platform Social Media Manager")
  plat = st.selectbox(
      "प्लेटफॉर्म चुनें:",
      [
          "YouTube Studio Strategy",
          "Instagram Reel Optimizer",
          "Facebook Page Manager",
          "Twitter / X Thread Creator",
      ],
  )
  topic = st.text_input("किस टॉपिक पर पोस्ट तैयार करनी है?")
  if st.button("कंटेंट और स्ट्रैटेजी बनाएं"):
    if api_ready and topic:
      with st.spinner("Social Manager पोस्ट तैयार कर रहा है..."):
        res = model.generate_content(
            f"Create expert viral post, caption, and schedule strategy for"
            f" {plat} about: {topic}"
        )
        st.info(res.text)
        st.success("✅ कंटेंट तैयार है!")
    else:
      st.warning("API Key और टॉपिक दर्ज करें।")

with tab5:
  st.subheader("🏷️ SEO & Hashtag Generator")
  ht_keyword = st.text_input("मुख्य कीवर्ड लिखें:")
  if st.button("वायरल हैशटैग्स जनरेट करें"):
    if api_ready and ht_keyword:
      with st.spinner("SEO Agent हैशटैग्स खोज रहा है..."):
        res = model.generate_content(
            f"Generate 30 high-ranking viral hashtags and SEO keywords for"
            f" YouTube Shorts and Instagram Reels for: {ht_keyword}"
        )
        st.success("✅ वायरल हैशटैग्स:")
        st.markdown(res.text)
    else:
      st.warning("कीवर्ड दर्ज करें।")
