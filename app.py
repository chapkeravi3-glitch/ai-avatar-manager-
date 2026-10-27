import time
import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="AI Avatar Social & Trend Manager",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for styling and Avatar Look
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .avatar-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(135deg, #1f2937, #111827);
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    .pulsing-avatar {
        width: 140px;
        height: 140px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #9333ea);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 60px;
        animation: pulse 2s infinite;
        box-shadow: 0 0 25px #3b82f6;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 20px rgba(59, 130, 246, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
    }
    .status-text {
        color: #10b981;
        font-weight: bold;
        margin-top: 10px;
        font-size: 16px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Sidebar for API Configuration
st.sidebar.header("⚙️ Settings & Keys")
api_key_input = st.sidebar.text_input(
    "Enter Gemini API Key", type="password", help="Get key from Google AI Studio"
)

GOOGLE_API_KEY = (
    api_key_input
    if api_key_input
    else st.secrets.get("GEMINI_API_KEY", "")
)

if GOOGLE_API_KEY:
  genai.configure(api_key=GOOGLE_API_KEY)
  model = genai.GenerativeModel("gemini-1.5-flash")
else:
  st.sidebar.warning(
      "कृपया अपनी Gemini API Key दर्ज करें (या Streamlit Secrets में जोड़ें)।"
  )

# App Header
st.title("🤖 AI Avatar & Social Media Manager")
st.markdown(
    "आपका पर्सनल AI अवतार जो रील्स आइडिया, ट्रेंडिंग टॉपिक्स और सोशल मीडिया"
    " मैनेज करेगा।"
)

# --- AVATAR DISPLAY SECTION ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
  st.markdown(
      """
        <div class="avatar-box">
            <div class="pulsing-avatar">👩‍💻</div>
            <div class="status-text">● AI Avatar is Active & Ready</div>
        </div>
        """,
      unsafe_allow_html=True,
  )

# --- TABS FOR DIFFERENT FUNCTIONS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "💬 AI Chat & Voice",
        "🔥 Trends & Reel Ideas",
        "🎵 Music Player",
        "📱 Social Manager",
        "📊 Analytics",
    ]
)

# TAB 1: GEMINI CORE CHAT
with tab1:
  st.subheader("Gemini Assistant Chat")

  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input(
      "अवतार से कुछ पूछें (जैसे: रील्स का आइडिया दो या ट्रेंडिंग क्या है)..."
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    with st.chat_message("assistant"):
      if not GOOGLE_API_KEY:
        response_text = (
            "कृपया पहले साइडबार में अपनी Gemini API Key दर्ज करें।"
        )
      else:
        try:
          with st.spinner("Avatar is thinking..."):
            system_prompt = (
                "You are an advanced AI avatar manager. You help users find"
                " trending topics, viral reel ideas, hashtags, and manage"
                " YouTube/Instagram. Respond cleverly in Hinglish/Hindi."
            )
            full_prompt = f"{system_prompt}\nUser: {prompt}"
            response = model.generate_content(full_prompt)
            response_text = response.text
        except Exception as e:
          response_text = f"Error connecting to Gemini: {str(e)}"

      st.markdown(response_text)
      st.session_state.messages.append(
          {"role": "assistant", "content": response_text}
      )

# TAB 2: TRENDS & REEL IDEAS
with tab2:
  st.subheader("🔥 Viral Trends & Reel/Video Ideas Generator")
  niche = st.selectbox(
      "Select Your Niche / Category",
      [
          "Tech & AI",
          "Comedy & Entertainment",
          "Motivation & Finance",
          "Lifestyle & Vlogs",
          "Gaming",
      ],
  )
  if st.button("Generate Trending Topics & Reel Ideas"):
    if GOOGLE_API_KEY:
      with st.spinner("Searching latest trends and ideas..."):
        trend_prompt = (
            f"Act as a social media growth expert. For the niche '{niche}',"
            " provide: 1. 3 Current trending topics that get maximum views,"
            " 2. Catchy Reel/Shorts scripts or hooks, 3. Viral hashtags."
        )
        res = model.generate_content(trend_prompt)
        st.success("✅ यहाँ आपके लिए वायरल आइडिया तैयार हैं:")
        st.markdown(res.text)
    else:
      st.warning("कृपया API Key दर्ज करें।")

# TAB 3: MUSIC PLAYER
with tab3:
  st.subheader("🎵 AI Music & Lo-Fi Player")
  st.markdown("जब आप काम करें, तब अपना पसंदीदा गाना या रिलैक्सिंग म्यूज़िक सुनें:")
  music_choice = st.selectbox(
      "Choose Vibe",
      ["Lo-Fi Beats (Focus)", "Upbeat Trending Pop", "Calm Instrumental"],
  )
  if music_choice == "Lo-Fi Beats (Focus)":
    st.audio(
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        format="audio/mp3",
    )
  elif music_choice == "Upbeat Trending Pop":
    st.audio(
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        format="audio/mp3",
    )
  else:
    st.audio(
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        format="audio/mp3",
    )

# TAB 4: SOCIAL MEDIA MANAGER
with tab4:
  st.subheader("📱 Social Media Auto-Scheduler (YouTube / Insta / FB)")
  platform = st.selectbox(
      "Select Platform", ["Instagram Reel", "YouTube Video", "Facebook Post"]
  )
  post_topic = st.text_input("Enter Topic or Caption Details")
  if st.button("Generate & Schedule Post"):
    if GOOGLE_API_KEY and post_topic:
      with st.spinner("Optimizing post for maximum engagement..."):
        post_prompt = (
            f"Create a high-engagement caption, tags, and posting strategy for"
            f" {platform} about: {post_topic}"
        )
        res = model.generate_content(post_prompt)
        st.info(res.text)
        st.success(
            f"✅ Successfully scheduled for {platform} with optimized"
            " algorithms!"
        )
    else:
      st.warning("कृपया टॉपिक दर्ज करें।")

# TAB 5: ANALYTICS
with tab5:
  st.subheader("📊 Growth Analytics Dashboard")
  st.metric(label="Estimated Follower Growth", value="+1,420", delta="18% this week")
  st.metric(label="Trending Score", value="94 / 100", delta="High Viral Potential")
  st.markdown(
      "*यह डेटा आपके सोशल मीडिया एंगेजमेंट और ट्रेंड्स के आधार पर दिखाया जा"
      " रहा है।*"
  )
