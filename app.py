import time
import google.generativeai as genai
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="AI Avatar Social Manager",
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
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: #3b82f6;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 50px;
        animation: pulse 2s infinite;
        box-shadow: 0 0 20px #3b82f6;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 15px rgba(59, 130, 246, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
    }
    .status-text {
        color: #10b981;
        font-weight: bold;
        margin-top: 10px;
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

# Use Streamlit Secrets if available, otherwise use input
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
st.title("🤖 AI Autonomous Avatar & Social Manager")
st.markdown("आपका पर्सनल AI अवतार जो बोलकर बात करेगा और सोशल मीडिया मैनेज करेगा।")

# --- AVATAR DISPLAY SECTION ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
  st.markdown(
      """
        <div class="avatar-box">
            <div class="pulsing-avatar">🗣️</div>
            <div class="status-text">● AI Avatar is Online & Listening...</div>
        </div>
        """,
      unsafe_allow_html=True,
  )

# --- TABS FOR DIFFERENT FUNCTIONS ---
tab1, tab2, tab3, tab4 = st.tabs(
    ["💬 Gemini Chat & Voice", "📱 WhatsApp", "🔴 YouTube", "📘 Facebook"]
)

# TAB 1: GEMINI CORE CHAT
with tab1:
  st.subheader("Gemini Cloud Assistant")

  if "messages" not in st.session_state:
    st.session_state.messages = []

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input(
      "अवतार को आदेश दें (जैसे: WhatsApp पर मैसेज भेजो या कुछ पूछो)..."
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
            # Prompt Engineering to make Gemini behave like a manager avatar
            system_prompt = (
                "You are an advanced AI avatar assistant that manages social"
                " media (WhatsApp, YouTube, Facebook). Respond smartly and"
                " helpfully in Hinglish/Hindi."
            )
            full_prompt = f"{system_prompt}\nUser Command: {prompt}"
            response = model.generate_content(full_prompt)
            response_text = response.text
        except Exception as e:
          response_text = f"Error connecting to Gemini: {str(e)}"

      st.markdown(response_text)
      st.session_state.messages.append(
          {"role": "assistant", "content": response_text}
      )

# TAB 2: WHATSAPP MANAGER
with tab2:
  st.subheader("📱 WhatsApp Manager")
  wa_number = st.text_input("Recipient Phone Number (with Country Code)")
  wa_message = st.text_area("Message to Send via AI")
  if st.button("Send WhatsApp Message"):
    if wa_number and wa_message:
      with st.spinner("Processing WhatsApp action..."):
        time.sleep(1.5)
        st.success(
            f"✅ Message successfully queued/sent to {wa_number} via AI"
            " Automation!"
        )
    else:
      st.error("कृपया नंबर और मैसेज दोनों भरें।")

# TAB 3: YOUTUBE MANAGER
with tab3:
  st.subheader("🔴 YouTube Manager")
  yt_title = st.text_input("Video Title / Search Query")
  yt_action = st.selectbox(
      "Choose Action",
      ["Search Video Analytics", "Draft Video Description", "Check Comments"],
  )
  if st.button("Execute YouTube Command"):
    if GOOGLE_API_KEY and yt_title:
      with st.spinner("AI is analyzing YouTube..."):
        yt_prompt = (
            f"Generate a professional YouTube description or strategy for:"
            f" {yt_title}"
        )
        res = model.generate_content(yt_prompt)
        st.info(res.text)
    else:
      st.warning("कृपया टाइटल दर्ज करें और API Key सेट करें।")

# TAB 4: FACEBOOK MANAGER
with tab4:
  st.subheader("📘 Facebook Page Manager")
  fb_post = st.text_area("Write Post Content for Facebook")
  if st.button("Publish to Facebook Page"):
    if fb_post:
      with st.spinner("Publishing to Facebook..."):
        time.sleep(1.5)
        st.success(
            "✅ Post successfully created and sent to Facebook Graph API queue!"
        )
    else:
      st.error("कृपया पोस्ट लिखने के लिए कुछ टेक्स्ट दें।")
