import os
import google.generativeai as genai
import streamlit as st

# ==========================================
# ⚙️ PAGE & SYSTEM CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Autonomous Executive AI Human Agent",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# 🎨 ULTRA-PREMIUM CINEMATIC UI & HUMAN AVATAR CSS
# ==========================================
st.markdown(
    """
    <style>
    .main { 
        background: radial-gradient(circle at top, #0f172a 0%, #020617 100%); 
        color: #f8fafc; 
        font-family: 'Inter', sans-serif; 
    }
    
    .avatar-hero-container {
        position: relative;
        width: 100%;
        max-width: 900px;
        margin: 0 auto 30px auto;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
        border-radius: 28px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 30px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), inset 0 0 30px rgba(56, 189, 248, 0.1);
        backdrop-filter: blur(16px);
    }

    .neural-face-wrapper {
        position: relative;
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: radial-gradient(circle, #38bdf8 0%, #0284c7 50%, #0369a1 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 50px rgba(56, 189, 248, 0.8), 0 0 100px rgba(14, 165, 233, 0.4);
        animation: neural-pulse 3.5s infinite ease-in-out;
    }

    @keyframes neural-pulse {
        0% { transform: scale(0.97); box-shadow: 0 0 35px rgba(56, 189, 248, 0.6); }
        50% { transform: scale(1.03); box-shadow: 0 0 65px rgba(56, 189, 248, 0.9); }
        100% { transform: scale(0.97); box-shadow: 0 0 35px rgba(56, 189, 248, 0.6); }
    }

    .anchor-avatar-img {
        width: 168px;
        height: 168px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid rgba(255, 255, 255, 0.8);
        box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
    }

    .neural-badge {
        margin-top: 15px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        padding: 6px 20px;
        border-radius: 30px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1px;
        display: flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.3);
    }

    .live-dot {
        width: 8px;
        height: 8px;
        background-color: #34d399;
        border-radius: 50%;
        box-shadow: 0 0 8px #34d399;
        animation: blink-dot 1s infinite alternate;
    }

    @keyframes blink-dot {
        0% { opacity: 0.3; }
        100% { opacity: 1; }
    }

    .avatar-speech-box {
        margin-top: 15px;
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 14px 30px;
        border-radius: 20px;
        font-size: 15px;
        color: #e2e8f0;
        text-align: center;
        max-width: 700px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #0b0f19;
        padding: 12px;
        border-radius: 16px;
        border: 1px solid #1e293b;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #111827;
        border-radius: 12px;
        color: #94a3b8;
        font-weight: 600;
        padding: 12px 24px;
        border: 1px solid #1f2937;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0284c7, #2563eb) !important;
        color: white !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.5);
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #0f172a !important;
        color: white !important;
        border-radius: 12px !important;
        border: 1px solid #334155 !important;
        padding: 12px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# ⚡ GEMINI API SETUP (Using latest gemini-3.8-flash)
# ==========================================
api_ready = False
model = None

try:
  if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
  else:
    st.sidebar.title("⚙️ System Config")
    k_input = st.sidebar.text_input("Enter Gemini API Key", type="password")
    if k_input:
      genai.configure(api_key=k_input)

  # Directly targeting the newly recommended model
  model = genai.GenerativeModel("gemini-3.8-flash")
  api_ready = True
except Exception as e:
  api_ready = False

# ==========================================
# 👩‍💼 CINEMATIC HUMAN AVATAR HERO HEADER (TOP)
# ==========================================
st.markdown(
    """
    <div class="avatar-hero-container">
        <div class="neural-face-wrapper">
            <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80" class="anchor-avatar-img" alt="Human AI Manager">
        </div>
        <div class="neural-badge">
            <div class="live-dot"></div> NEURAL EXECUTIVE AVATAR: ONLINE & ACTIVE
        </div>
        <div class="avatar-speech-box">
            "नमस्ते बॉस! मैं आपका ऑटोनॉमस एआई मैनेजर हूँ। आपकी सोशल मीडिया ग्रोथ, ट्रेंड रिसर्च, और म्यूजिक मैनेजमेंट पूरी तरह से संभाल रही हूँ। बताइए, आज क्या करना है?"
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 🗂️ SLIDE & EXPLORE MODULE TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💬 Executive Voice & Chat",
        "🔥 Viral Trend & Reel Hunter",
        "🎵 Audio & Music Maestro",
        "📱 Social Media Command",
        "🏷️ SEO & Viral Hashtags",
    ]
)

# --- TAB 1: FAST EXECUTIVE CHAT ---
with tab1:
  st.subheader("💬 Super-Fast Neural Chat with Executive Agent")
  if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

  for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if user_input := st.chat_input("एजेंट से कुछ भी कहें (जैसे: हेलो, कैसे हो?)..."):
    st.session_state.chat_messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
      st.markdown(user_input)

    with st.chat_message("assistant"):
      if not api_ready or model is None:
        reply = "⚠️ कृपया `.streamlit/secrets.toml` में या साइडबार में अपनी सही Gemini API Key सेट करें।"
      else:
        try:
          with st.spinner("⚡ AI Agent thinking instantly..."):
            sys_prompt = (
                "You are an elite, professional, human-like virtual executive"
                " manager. Reply extremely fast, smartly, and conversationally"
                " in natural Hinglish/Hindi."
            )
            response = model.generate_content(
                f"{sys_prompt}\nUser: {user_input}"
            )
            reply = response.text
        except Exception as e:
          reply = f"Connection Error: {str(e)}"

      st.markdown(reply)
      st.session_state.chat_messages.append(
          {"role": "assistant", "content": reply}
      )

# --- TAB 2: TREND & REEL GENERATOR ---
with tab2:
  st.subheader("🔥 Viral Trend Hunter & Reel Idea Engine")
  niche_choice = st.selectbox(
      "अपनी निच (Niche) चुनें:",
      [
          "Tech & Artificial Intelligence",
          "Entertainment & Comedy",
          "Business & Startup Strategy",
          "Lifestyle & Daily Vlogs",
          "Gaming & Streaming",
      ],
  )
  if st.button("🚀 तुरंत ट्रेंड्स और रील्स आइडिया खोजें"):
    if api_ready and model:
      with st.spinner("Trend Hunter इंटरनेट स्कैन कर रहा है..."):
        prompt_t = (
            f"As a viral growth expert, give 3 top trending topics, viral hooks,"
            f" and script framework for: {niche_choice}"
        )
        res = model.generate_content(prompt_t)
        st.success("✅ वायरल ग्रोथ स्ट्रेटेजी तैयार है:")
        st.markdown(res.text)
    else:
      st.error("API Key उपलब्ध नहीं है।")

# --- TAB 3: MUSIC & SONG PLAYER ---
with tab3:
  st.subheader("🎵 Audio & Music Maestro Agent")
  song_input = st.text_input("जो गाना या म्यूज़िक सुनना हो उसका नाम लिखें:")
  if st.button("🎧 गाना तुरंत खोजें"):
    if song_input:
      st.success(f"🎵 '{song_input}' के लिए डायरेक्ट लिंक्स तैयार हैं:")
      encoded_s = song_input.replace(" ", "+")
      yt_url = f"https://www.youtube.com/results?search_query={encoded_s}"
      spotify_url = f"https://open.spotify.com/search/{encoded_s}"

      st.markdown(
          f"""
            <div style="background: #0f172a; padding: 22px; border-radius: 14px; border: 1px solid #38bdf8; margin-top: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                <p style="margin-bottom: 15px; font-size: 16px; color:#38bdf8;"><b>म्यूज़िक प्लेयर लिंक्स:</b></p>
                <a href="{yt_url}" target="_blank" style="display: inline-block; background: #ef4444; color: white; padding: 12px 24px; text-decoration: none; border-radius: 10px; font-weight: bold; margin-right: 15px; box-shadow: 0 4px 12px rgba(239,68,68,0.4);">▶ YouTube पर सुनें</a>
                <a href="{spotify_url}" target="_blank" style="display: inline-block; background: #22c55e; color: white; padding: 12px 24px; text-decoration: none; border-radius: 10px; font-weight: bold; box-shadow: 0 4px 12px rgba(34,197,94,0.4);">🎧 Spotify पर सुनें</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
    else:
      st.error("कृपया गाने का नाम दर्ज करें।")

# --- TAB 4: SOCIAL MEDIA COMMAND ---
with tab4:
  st.subheader("📱 Multi-Platform Social Media Manager")
  platform_sel = st.selectbox(
      "प्लेटफॉर्म चुनें:",
      [
          "YouTube Studio Optimization & Description",
          "Instagram Reel & Post Caption",
          "Facebook Page Engagement Manager",
      ],
  )
  post_q = st.text_input("किस टॉपिक या वीडियो के लिए पोस्ट तैयार करनी है?")
  if st.button("✨ पोस्ट और कैप्शन जनरेट करें"):
    if api_ready and model and post_q:
      with st.spinner("Social Manager पोस्ट तैयार कर रहा है..."):
        prompt_s = (
            f"Create a high-engagement viral post and strategy for"
            f" {platform_sel} about: {post_q}"
        )
        res = model.generate_content(prompt_s)
        st.info(res.text)
        st.success("✅ सोशल मीडिया पोस्ट तैयार है!")
    else:
      st.error("कृपया API Key और टॉपिक दर्ज करें।")

# --- TAB 5: VIRAL SEO & HASHTAGS ---
with tab5:
  st.subheader("🏷️ SEO & Viral Hashtag Generator")
  tag_kw = st.text_input("अपने वीडियो का मुख्य कीवर्ड लिखें:")
  if st.button("🔍 वायरल हैशटैग्स बनाएं"):
    if api_ready and model and tag_kw:
      with st.spinner("SEO Agent हैशटैग्स खोज रहा है..."):
        prompt_h = (
            f"Generate 30 top-ranking viral hashtags and SEO keywords for"
            f" YouTube Shorts and Instagram Reels for: {tag_kw}"
        )
        res = model.generate_content(prompt_h)
        st.success("✅ वायरल हैशटैग्स तैयार हैं:")
        st.markdown(res.text)
    else:
      st.error("कृपया कीवर्ड दर्ज करें।")
