import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Autonomous Executive AI Human Agent",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# ⚡ SMART AUTO-MODEL DISCOVERY & BACKEND SETUP
# ==========================================
api_ready = False
model = None

try:
  if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
  else:
    st.sidebar.title("⚙️ System Configuration")
    k_input = st.sidebar.text_input("Enter Gemini API Key", type="password")
    if k_input:
      genai.configure(api_key=k_input)

  # ऑटोमैटिकली चेक करेगा कि आपकी की के लिए कौन सा मॉडल सपोर्टेड है
  try:
    for m in genai.list_models():
      if "generateContent" in m.supported_generation_methods:
        model = genai.GenerativeModel(m.name)
        api_ready = True
        break
  except Exception:
    pass

  # अगर लिस्टिंग से न मिले, तो सुरक्षित विकल्पों को बारी-बारी ट्राई करेगा
  if not model:
    for model_name in ["gemini-pro", "gemini-1.5-flash", "gemini-1.5-pro"]:
      try:
        model = genai.GenerativeModel(model_name)
        api_ready = True
        break
      except Exception:
        continue

  if not model:
    api_ready = False

except Exception as e:
  api_ready = False

# ==========================================
# 🎨 CINEMATIC UI & STYLING
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
        margin: 0 auto 20px auto;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.95));
        border-radius: 24px;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 25px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        box-shadow: 0 20px 50px rgba(0,0,0,0.8);
        backdrop-filter: blur(12px);
    }

    .neural-face-wrapper {
        position: relative;
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: radial-gradient(circle, #38bdf8 0%, #0284c7 60%, #0369a1 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 40px rgba(56, 189, 248, 0.8);
        animation: pulse-glow 3s infinite ease-in-out;
    }

    @keyframes pulse-glow {
        0% { transform: scale(0.98); box-shadow: 0 0 30px rgba(56, 189, 248, 0.5); }
        50% { transform: scale(1.04); box-shadow: 0 0 60px rgba(56, 189, 248, 0.9); }
        100% { transform: scale(0.98); box-shadow: 0 0 30px rgba(56, 189, 248, 0.5); }
    }

    .anchor-avatar-img {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid rgba(255, 255, 255, 0.9);
    }

    .neural-badge {
        margin-top: 12px;
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .live-dot {
        width: 7px;
        height: 7px;
        background-color: #34d399;
        border-radius: 50%;
        animation: blink-dot 1s infinite alternate;
    }

    @keyframes blink-dot {
        0% { opacity: 0.3; }
        100% { opacity: 1; }
    }

    .avatar-speech-box {
        margin-top: 12px;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 12px 20px;
        border-radius: 16px;
        font-size: 14px;
        color: #e2e8f0;
        text-align: center;
        max-width: 650px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 👩‍💼 CINEMATIC HERO HEADER WITH AVATAR
# ==========================================
st.markdown(
    """
    <div class="avatar-hero-container">
        <div class="neural-face-wrapper">
            <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80" class="anchor-avatar-img" alt="Human AI Manager">
        </div>
        <div class="neural-badge">
            <div class="live-dot"></div> AUTO-DETECT MODEL EXECUTIVE ACTIVE
        </div>
        <div class="avatar-speech-box">
            "नमस्ते बॉस! सिस्टम पूरी तरह तैयार है। बताइए, आज क्या करना है?"
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 🗂️ ALL MODULE TABS
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💬 Executive Chat",
        "🔥 Trend & Reels",
        "🎵 Music & Audio",
        "📱 Social Media",
        "🏷️ SEO & Hashtags",
    ]
)

# --- TAB 1: CHAT ---
with tab1:
  st.subheader("💬 Direct Neural Chat with Executive Agent")
  if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

  for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if user_input := st.chat_input("एजेंट से कुछ भी कहें (जैसे: हैलो)..."):
    st.session_state.chat_messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
      st.markdown(user_input)

    with st.chat_message("assistant"):
      if not api_ready or model is None:
        reply = "⚠️ कृपया अपनी सही Gemini API Key सेट करें।"
      else:
        try:
          with st.spinner("⚡ जवाब आ रहा है..."):
            sys_prompt = (
                "You are an elite, human-like virtual executive manager. Reply"
                " smartly and conversationally in natural Hinglish/Hindi."
            )
            response = model.generate_content(
                f"{sys_prompt}\nUser: {user_input}"
            )
            reply = response.text
        except Exception as e:
          reply = f"⚠️ Error: {str(e)}"

      st.markdown(reply)
      st.session_state.chat_messages.append(
          {"role": "assistant", "content": reply}
      )

# --- TAB 2: TRENDS ---
with tab2:
  st.subheader("🔥 Viral Trend & Reel Idea Generator")
  niche_choice = st.selectbox(
      "अपनी निच (Niche) चुनें:",
      [
          "Tech & Artificial Intelligence",
          "Entertainment & Comedy",
          "Business & Startup Strategy",
          "Lifestyle & Daily Vlogs",
      ],
  )
  if st.button("🚀 ट्रेंड्स और रील्स आइडिया खोजें"):
    if api_ready and model:
      with st.spinner("स्कैन हो रहा है..."):
        try:
          res = model.generate_content(
              f"Give 3 top trending topics, viral hooks, and strategy for: {niche_choice}"
          )
          st.success("✅ वायरल स्ट्रेटेजी तैयार है:")
          st.markdown(res.text)
        except Exception as e:
          st.error(f"Error: {str(e)}")
    else:
      st.error("API Key उपलब्ध नहीं है।")

# --- TAB 3: MUSIC ---
with tab3:
  st.subheader("🎵 Audio & Music Maestro Agent")
  song_input = st.text_input("जो गाना सुनना हो उसका नाम लिखें:")
  if st.button("🎧 गाना खोजें"):
    if song_input:
      st.success(f"🎵 '{song_input}' के लिए लिंक्स तैयार हैं:")
      enc = song_input.replace(" ", "+")
      st.markdown(
          f"""
            <div style="background: #0f172a; padding: 15px; border-radius: 10px; border: 1px solid #38bdf8;">
                <a href="https://www.youtube.com/results?search_query={enc}" target="_blank" style="color: #ef4444; font-weight: bold; margin-right: 20px; text-decoration: none;">▶ YouTube पर सुनें</a>
                <a href="https://open.spotify.com/search/{enc}" target="_blank" style="color: #22c55e; font-weight: bold; text-decoration: none;">🎧 Spotify पर सुनें</a>
            </div>
            """,
          unsafe_allow_html=True,
      )
    else:
      st.error("कृपया गाने का नाम लिखें।")

# --- TAB 4: SOCIAL MEDIA ---
with tab4:
  st.subheader("📱 Multi-Platform Social Media Manager")
  platform_sel = st.selectbox(
      "प्लेटफॉर्म चुनें:",
      [
          "YouTube Studio Strategy & Description",
          "Instagram Reel & Post Caption",
          "Facebook Page Engagement Post",
      ],
  )
  post_q = st.text_input("किस टॉपिक पर पोस्ट तैयार करनी है?")
  if st.button("✨ पोस्ट और कैप्शन बनाएं"):
    if api_ready and model and post_q:
      with st.spinner("तैयार हो रहा है..."):
        try:
          res = model.generate_content(
              f"Create an expert engaging post and strategy for {platform_sel} about: {post_q}"
          )
          st.info(res.text)
          st.success("✅ पोस्ट तैयार है!")
        except Exception as e:
          st.error(f"Error: {str(e)}")
    else:
      st.error("कृपया टॉपिक दर्ज करें।")

# --- TAB 5: SEO ---
with tab5:
  st.subheader("🏷️ SEO & Viral Hashtag Generator")
  tag_kw = st.text_input("अपने वीडियो का मुख्य कीवर्ड लिखें:")
  if st.button("🔍 वायरल हैशटैग्स बनाएं"):
    if api_ready and model and tag_kw:
      with st.spinner("खोजा जा रहा है..."):
        try:
          res = model.generate_content(
              f"Generate 30 high-ranking viral hashtags and SEO keywords for YouTube Shorts & Instagram Reels for: {tag_kw}"
          )
          st.success("✅ वायरल हैशटैग्स तैयार हैं:")
          st.markdown(res.text)
        except Exception as e:
          st.error(f"Error: {str(e)}")
    else:
      st.error("कृपया कीवर्ड दर्ज करें।")
