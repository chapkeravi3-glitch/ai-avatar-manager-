"""
Executive AI Human Agent  (Streamlit + Gemini)

requirements.txt:
    streamlit>=1.39
    google-generativeai
    edge-tts

KEY: सिर्फ़ एक - GEMINI_API_KEY (https://aistudio.google.com/apikey से फ्री मिलती है)
     Streamlit Cloud में: Settings -> Secrets ->  GEMINI_API_KEY = "आपकी_की"
     या ऐप खुलने पर स्क्रीन पर पेस्ट कर दें।
"""
import asyncio
import base64
import hashlib
import json
import re
import urllib.parse

import google.generativeai as genai
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Executive AI Agent",
    page_icon="👑",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DEFAULT_FACE = "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=500&q=80"

# ============================================================
# 🎨 STYLE
# ============================================================
st.markdown(
    """
<style>
.stApp { background: radial-gradient(circle at top, #0f172a 0%, #020617 100%); color:#f8fafc; }
.block-container { padding-top: 1rem; padding-bottom: 6rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# 🔑 API KEY + FAST MODEL PICK
# ============================================================
api_key = st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
if not api_key:
    api_key = st.session_state.get("api_key", "")
if not api_key:
    k = st.text_input("🔑 अपनी Gemini API Key यहाँ पेस्ट करें", type="password")
    if k:
        st.session_state.api_key = k
        api_key = k
        st.rerun()


@st.cache_resource(show_spinner=False)
def pick_model_name(key: str) -> str:
    """सबसे तेज़ (flash) मॉडल अपने-आप चुनता है; एक बार ही चेक करता है।"""
    genai.configure(api_key=key)
    try:
        names = [
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        bad = ("preview", "exp", "thinking", "image", "tts", "live", "lite", "embedding", "vision", "learn")
        flash = [n for n in names if "flash" in n and not any(b in n for b in bad)]
        for pref in ("2.5-flash", "2.0-flash", "1.5-flash"):
            for n in flash:
                if pref in n:
                    return n
        if flash:
            return flash[0]
        if names:
            return names[0]
    except Exception:
        pass
    return "gemini-2.0-flash"


SYS_PROMPT = (
    "तुम एक स्मार्ट, गर्मजोश, इंसान जैसे पर्सनल एग्ज़ीक्यूटिव असिस्टेंट हो। "
    "यूज़र जिस भाषा में बोले (हिंदी/हिंग्लिश/English) उसी में जवाब दो। "
    "जवाब बोले जाने के लिए है: छोटे, सीधे, बातचीत वाले वाक्य, ज़्यादातर 2-4 वाक्य। "
    "markdown, बुलेट, इमोजी या लिंक मत लिखो, जब तक यूज़र लंबा या लिस्ट न मांगे।"
)


def chat_model():
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        pick_model_name(api_key),
        system_instruction=SYS_PROMPT,
        generation_config={"max_output_tokens": 500, "temperature": 0.8},
    )


def plain_model():
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        pick_model_name(api_key),
        generation_config={"max_output_tokens": 2000, "temperature": 0.9},
    )


def stream_gen(model, contents):
    resp = model.generate_content(contents, stream=True)
    for ch in resp:
        try:
            if ch.text:
                yield ch.text
        except Exception:
            continue


# ============================================================
# 🔊 VOICE (इंसानी आवाज़)
# ============================================================
def speech_clean(t: str) -> str:
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"[*_#`>~|]", "", t)
    t = re.sub(r"[\U00010000-\U0010ffff\u2600-\u27bf]", "", t)
    return re.sub(r"\s+", " ", t).strip()[:700]


async def _edge(text, voice):
    import edge_tts

    data = b""
    async for ch in edge_tts.Communicate(text, voice).stream():
        if ch["type"] == "audio":
            data += ch["data"]
    return data


def edge_b64(text, voice):
    try:
        return base64.b64encode(asyncio.run(_edge(text, voice))).decode()
    except Exception:
        return None


# ============================================================
# 👤 TALKING FACE
# ============================================================
AVATAR_TPL = """
<style>
 body{margin:0;background:transparent;font-family:sans-serif;color:#e2e8f0;text-align:center}
 .wrap{padding:8px 0}
 .ring{width:170px;height:170px;margin:0 auto;border-radius:50%;padding:5px;
   background:radial-gradient(circle,#38bdf8,#0369a1);box-shadow:0 0 30px rgba(56,189,248,.6)}
 .face{position:relative;width:100%;height:100%;border-radius:50%;overflow:hidden;background:#0f172a}
 .face img{width:100%;height:100%;object-fit:cover;display:block}
 .mouth{position:absolute;left:50%;top:__MY__%;width:17%;height:8%;border-radius:50%;
   background:radial-gradient(ellipse,#2a0508 0%,#5a1218 60%,rgba(90,18,24,0) 100%);
   transform:translate(-50%,-50%) scaleY(.1);opacity:0;filter:blur(1.2px)}
 .bars{display:flex;gap:4px;justify-content:center;align-items:flex-end;height:28px;margin-top:10px}
 .bars i{width:5px;height:4px;border-radius:3px;background:#38bdf8;display:block}
 #st{margin-top:6px;font-size:13px;color:#34d399;font-weight:700}
 button{margin-top:8px;background:#0ea5e9;color:#fff;border:0;border-radius:20px;padding:8px 18px;font-size:14px;display:none}
</style>
<div class="wrap">
 <div class="ring" id="ring"><div class="face" id="face">
   <img src="__FACE__"><div class="mouth" id="mouth"></div></div></div>
 <div class="bars" id="bars"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
 <div id="st">● सुन रहा हूँ</div>
 <button id="btn">🔊 सुनिए</button>
</div>
<script>
const P = __PAYLOAD__;
const mouth=document.getElementById('mouth'), face=document.getElementById('face'),
      ring=document.getElementById('ring'), st=document.getElementById('st'),
      btn=document.getElementById('btn'), bars=[...document.querySelectorAll('#bars i')];
let speaking=false, amp=0, t=0;
function setSpeak(v){ speaking=v; st.textContent = v ? '🗣 बोल रहा हूँ…' : '● सुन रहा हूँ'; }
function loop(){
  t+=0.016;
  const target = speaking ? (0.3+0.7*Math.abs(Math.sin(t*11))*(0.55+0.45*Math.random())) : 0;
  amp += (target-amp)*0.35;
  mouth.style.opacity = speaking ? (0.55+amp*0.4) : 0;
  mouth.style.transform = 'translate(-50%,-50%) scaleY('+(0.12+amp*1.5)+')';
  const breathe = 1+0.004*Math.sin(t*1.6);
  face.style.transform = 'scale('+(breathe+amp*0.012)+') rotate('+(speaking?Math.sin(t*3)*0.5:0)+'deg)';
  ring.style.boxShadow = '0 0 '+(30+amp*40)+'px rgba(56,189,248,'+(0.5+amp*0.4)+')';
  bars.forEach((b,i)=>{ b.style.height = (4+amp*24*(0.5+0.5*Math.abs(Math.sin(t*9+i)))) + 'px'; });
  requestAnimationFrame(loop);
}
loop();
function speakBrowser(){
  if(!P.text) return;
  speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(P.text); u.lang='hi-IN'; u.rate=1.05;
  const v=speechSynthesis.getVoices().find(v=>v.lang.replace('_','-').toLowerCase().startsWith('hi'));
  if(v) u.voice=v;
  u.onstart=()=>setSpeak(true); u.onend=u.onerror=()=>setSpeak(false);
  speechSynthesis.speak(u);
}
function speakAudio(){
  window._a = new Audio('data:audio/mp3;base64,'+P.audio);
  window._a.onplay=()=>setSpeak(true); window._a.onended=window._a.onpause=()=>setSpeak(false);
  window._a.play().catch(()=>{ st.textContent='▶ नीचे बटन दबाएँ'; });
}
function go(){ P.audio ? speakAudio() : speakBrowser(); }
if(P.text){ btn.style.display='inline-block'; btn.onclick=go; setTimeout(go,250); }
</script>
"""


def render_avatar(slot, face_src, mouth_y, text="", audio_b64=None):
    html = (
        AVATAR_TPL.replace("__FACE__", face_src)
        .replace("__MY__", str(mouth_y))
        .replace("__PAYLOAD__", json.dumps({"text": text, "audio": audio_b64}))
    )
    with slot.container():
        components.html(html, height=290)


# ============================================================
# 📱 APP LAUNCHER (बैंकिंग/पेमेंट ऐप ब्लॉक)
# ============================================================
BLOCK = (
    "bank", "बैंक", "upi", "यूपीआई", "pay", "paytm", "पेटीएम", "phonepe", "फोनपे", "फोन-पे",
    "gpay", "जीपे", "bhim", "भीम", "sbi", "hdfc", "icici", "axis", "kotak", "yono", "cred",
    "wallet", "वॉलेट", "mobikwik", "freecharge", "navi", "groww", "zerodha", "नेट-बैंकिंग",
)

APPS = {
    "YouTube": (["youtube", "यूट्यूब", "यूटूब", "यु-ट्यूब"], "https://www.youtube.com/", "https://www.youtube.com/results?search_query={q}"),
    "Spotify": (["spotify", "स्पॉटिफाई", "स्पोटीफाई"], "https://open.spotify.com/", "https://open.spotify.com/search/{q}"),
    "JioSaavn": (["jiosaavn", "saavn", "सावन", "जियोसावन"], "https://www.jiosaavn.com/", "https://www.jiosaavn.com/search/{q}"),
    "Instagram": (["instagram", "इंस्टाग्राम", "इंस्टा", "insta"], "https://www.instagram.com/", "https://www.instagram.com/explore/search/keyword/?q={q}"),
    "WhatsApp": (["whatsapp", "व्हाट्सएप", "वॉट्सऐप", "व्हाट्सऐप", "वॉट्सएप"], "https://wa.me/", "https://wa.me/?text={q}"),
    "Facebook": (["facebook", "फेसबुक", "फ़ेसबुक"], "https://www.facebook.com/", "https://www.facebook.com/search/top?q={q}"),
    "X (Twitter)": (["twitter", "ट्विटर"], "https://x.com/", "https://x.com/search?q={q}"),
    "Telegram": (["telegram", "टेलीग्राम"], "https://t.me/", "https://t.me/"),
    "Snapchat": (["snapchat", "स्नैपचैट"], "https://www.snapchat.com/", "https://www.snapchat.com/"),
    "LinkedIn": (["linkedin", "लिंक्डइन"], "https://www.linkedin.com/", "https://www.linkedin.com/search/results/all/?keywords={q}"),
    "Google Maps": (["maps", "मैप", "मैप्स", "gmaps"], "https://www.google.com/maps", "https://www.google.com/maps/search/{q}"),
    "Gmail": (["gmail", "जीमेल"], "https://mail.google.com/", "https://mail.google.com/mail/u/0/#search/{q}"),
    "Google": (["google", "गूगल", "chrome", "क्रोम"], "https://www.google.com/", "https://www.google.com/search?q={q}"),
    "Play Store": (["playstore", "प्लेस्टोर", "प्ले-स्टोर"], "https://play.google.com/store", "https://play.google.com/store/search?q={q}&c=apps"),
    "Amazon": (["amazon", "अमेज़न", "अमेजन"], "https://www.amazon.in/", "https://www.amazon.in/s?k={q}"),
    "Flipkart": (["flipkart", "फ्लिपकार्ट"], "https://www.flipkart.com/", "https://www.flipkart.com/search?q={q}"),
}
VERB_STEMS = ("खोल", "open", "चला", "play", "सुना", "सुन", "लगा", "launch", "चालू", "दिखा", "start", "बजा")
MUSIC_WORDS = ("गाना", "गाने", "song", "songs", "music", "म्यूजिक", "म्यूज़िक", "सॉन्ग", "भजन", "ग़ज़ल")
FILLER = {
    "पर", "में", "का", "की", "के", "को", "से", "मेरा", "मेरे", "मुझे", "ऐप", "एप", "app", "on", "in",
    "the", "a", "please", "प्लीज", "जरा", "ज़रा", "अब", "यार", "और", "फिर", "दो", "दे", "दीजिए", "ओपन",
    "कर", "करो", "करके", "जाकर", "अंदर", "वहाँ", "वहां", "में।",
}


def tokens_of(text):
    return [w for w in re.split(r"[\s,।.!?]+", text.lower()) if w]


def handle_command(text, default_music):
    """ऐप खोलने/गाना चलाने वाला कमांड हो तो dict लौटाता है, वरना None।"""
    toks = tokens_of(text)
    if not any(any(v in w for v in VERB_STEMS) for w in toks):
        return None

    app_found = None
    for name, (aliases, _, _) in APPS.items():
        if any(w in aliases for w in toks):
            app_found = name
            break

    is_music = any(w in MUSIC_WORDS for w in toks)
    blocked = any(w.startswith(b) for w in toks for b in BLOCK)
    if blocked and not app_found:
        return {"msg": "माफ़ कीजिए, मैं बैंकिंग और पेमेंट वाले ऐप नहीं खोलता। आपके पैसों की सुरक्षा के लिए इन्हें आप खुद ही खोलिए।"}
    if not app_found and not is_music:
        return None
    if not app_found:
        app_found = default_music

    aliases = APPS[app_found][0]
    q_toks = [
        w for w in toks
        if w not in aliases and w not in FILLER and not any(v in w for v in VERB_STEMS)
    ]
    q = " ".join(q_toks).strip()
    _, home, search = APPS[app_found]
    url = search.format(q=urllib.parse.quote_plus(q)) if q else home
    if q:
        msg = f"ठीक है, {app_found} पर \"{q}\" लगा रहा हूँ। नीचे वाला बटन दबाइए।"
    else:
        msg = f"ठीक है, {app_found} खोल रहा हूँ। नीचे वाला बटन दबाइए।"
    return {"msg": msg, "label": f"▶ {app_found} खोलें", "url": url}


# ============================================================
# ⚙️ SETTINGS
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = ""

with st.expander("⚙️ सेटिंग (चेहरा, आवाज़)"):
    up = st.file_uploader("अपना चेहरा/फोटो लगाएँ (सीधी, साफ़ फ्रंट फोटो)", type=["png", "jpg", "jpeg"])
    mouth_y = st.slider("मुँह की ऊँचाई (फोटो के हिसाब से सेट करें)", 55, 85, 72)
    voice_mode = st.radio("आवाज़", ["⚡ तेज़ (फोन की आवाज़)", "🎙 ज़्यादा इंसानी (थोड़ा धीमा)"], index=0)
    gender = st.radio("आवाज़ का प्रकार (इंसानी मोड में)", ["पुरुष", "महिला"], horizontal=True)
    default_music = st.selectbox("गाना चलाने के लिए डिफ़ॉल्ट ऐप", ["YouTube", "Spotify", "JioSaavn"])

if up is not None:
    face_src = "data:{};base64,{}".format(up.type, base64.b64encode(up.getvalue()).decode())
else:
    face_src = DEFAULT_FACE
EDGE_VOICE = "hi-IN-MadhurNeural" if gender == "पुरुष" else "hi-IN-SwaraNeural"

st.markdown("<h3 style='text-align:center;margin:0'>👑 Executive AI Agent</h3>", unsafe_allow_html=True)
avatar_slot = st.empty()
render_avatar(avatar_slot, face_src, mouth_y)

tab_chat, tab_music, tab_social, tab_trend = st.tabs(
    ["💬 चैट", "🎵 म्यूज़िक", "📱 सोशल मीडिया", "🔥 ट्रेंड & SEO"]
)

# ============================================================
# 💬 CHAT (आवाज़ + टाइप, दोनों पर बोलकर जवाब)
# ============================================================
with tab_chat:
    audio_val = None
    if hasattr(st, "audio_input"):
        audio_val = st.audio_input("🎤 बोलकर पूछें (रिकॉर्ड दबाएँ, बात करें, रोकें)")
    else:
        st.caption("आवाज़ से पूछने के लिए Streamlit अपडेट करें: pip install -U streamlit")

    typed = st.chat_input("यहाँ टाइप करें… (जैसे: यूट्यूब पर अरिजीत के गाने चलाओ)")

    for i, m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            if m.get("url"):
                st.link_button(m["label"], m["url"], key=f"old{i}")

    user_text, audio_bytes, audio_mime = None, None, None
    if typed:
        user_text = typed
    elif audio_val is not None:
        raw = audio_val.getvalue()
        h = hashlib.md5(raw).hexdigest()
        if h != st.session_state.last_audio:
            st.session_state.last_audio = h
            audio_bytes, audio_mime = raw, (audio_val.type or "audio/wav")
            user_text = "🎤 (आवाज़ में पूछा)"

    if user_text:
        if not api_key:
            st.error("पहले ऊपर Gemini API Key डालें।")
        else:
            st.session_state.messages.append({"role": "user", "content": user_text})
            with st.chat_message("user"):
                st.markdown(user_text)

            cmd = handle_command(user_text, default_music) if not audio_bytes else None
            reply, link = "", None
            with st.chat_message("assistant"):
                if cmd:
                    reply = cmd["msg"]
                    st.markdown(reply)
                    if cmd.get("url"):
                        link = {"label": cmd["label"], "url": cmd["url"]}
                        st.link_button(link["label"], link["url"], key=f"new{len(st.session_state.messages)}")
                else:
                    history = []
                    for m in st.session_state.messages[-9:-1]:
                        history.append({"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]})
                    if audio_bytes:
                        last = {"role": "user", "parts": [
                            {"mime_type": audio_mime, "data": audio_bytes},
                            "यूज़र ने आवाज़ में सवाल पूछा है। उसे सुनकर सीधे जवाब दो।",
                        ]}
                    else:
                        last = {"role": "user", "parts": [user_text]}
                    try:
                        reply = st.write_stream(stream_gen(chat_model(), history + [last]))
                    except Exception as e:
                        reply = f"⚠️ दिक्कत आई: {e}"
                        st.markdown(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply, **(link or {})})

            spoken = speech_clean(reply)
            audio_b64 = None
            if spoken and voice_mode.startswith("🎙"):
                audio_b64 = edge_b64(spoken, EDGE_VOICE)
            render_avatar(avatar_slot, face_src, mouth_y, text=spoken, audio_b64=audio_b64)

    if st.session_state.messages and st.button("🗑 चैट साफ़ करें"):
        st.session_state.messages = []
        st.rerun()

# ============================================================
# 🎵 MUSIC
# ============================================================
with tab_music:
    st.subheader("🎵 म्यूज़िक")
    song = st.text_input("गाने / आर्टिस्ट का नाम")
    if song:
        q = urllib.parse.quote_plus(song)
        c1, c2, c3 = st.columns(3)
        c1.link_button("▶ YouTube", f"https://www.youtube.com/results?search_query={q}")
        c2.link_button("🎧 Spotify", f"https://open.spotify.com/search/{q}")
        c3.link_button("🎶 JioSaavn", f"https://www.jiosaavn.com/search/{q}")
    st.markdown("**ऐप के अंदर ही चलाएँ**")
    yt = st.text_input("YouTube वीडियो का लिंक पेस्ट करें")
    if yt:
        st.video(yt)
    mp3 = st.file_uploader("या अपना गाना (mp3/wav) डालें", type=["mp3", "wav", "m4a", "ogg"])
    if mp3:
        st.audio(mp3)

# ============================================================
# 📱 SOCIAL MEDIA
# ============================================================
with tab_social:
    st.subheader("📱 सोशल मीडिया मैनेजर")
    plat = st.selectbox("प्लेटफ़ॉर्म", ["YouTube (Title + Description)", "Instagram Reel/Post", "Facebook Page", "X (Twitter)", "LinkedIn"])
    topic = st.text_input("टॉपिक क्या है?")
    tone = st.selectbox("टोन", ["मज़ेदार", "प्रोफेशनल", "इमोशनल", "जोशीला"])
    lang = st.radio("भाषा", ["हिंदी", "Hinglish", "English"], horizontal=True)
    what = st.radio("क्या बनाना है?", ["पोस्ट + कैप्शन + हैशटैग", "7 दिन का कंटेंट कैलेंडर", "कमेंट के जवाब (5 नमूने)"])
    if st.button("✨ तैयार करो", key="gen_social"):
        if not api_key or not topic:
            st.error("API Key और टॉपिक दोनों चाहिए।")
        else:
            prompts = {
                "पोस्ट + कैप्शन + हैशटैग": f"Write a ready-to-post {plat} post about '{topic}'. Include hook, caption, CTA, 15 hashtags and the best posting time.",
                "7 दिन का कंटेंट कैलेंडर": f"Make a 7-day content calendar for {plat} about '{topic}': day, idea, hook, format, posting time.",
                "कमेंट के जवाब (5 नमूने)": f"Write 5 friendly reply templates for comments on a {plat} post about '{topic}'.",
            }
            try:
                st.write_stream(stream_gen(plain_model(), f"{prompts[what]} Tone: {tone}. Language: {lang}."))
            except Exception as e:
                st.error(f"Error: {e}")
    st.markdown("**सीधे खोलें**")
    a, b, c = st.columns(3)
    a.link_button("YouTube Studio", "https://studio.youtube.com")
    b.link_button("Instagram", "https://www.instagram.com/")
    c.link_button("Meta Business", "https://business.facebook.com/")

# ============================================================
# 🔥 TRENDS & SEO
# ============================================================
with tab_trend:
    st.subheader("🔥 ट्रेंड, रील आइडिया और हैशटैग")
    niche = st.selectbox("निच", ["Tech & AI", "Entertainment & Comedy", "Business & Startup", "Lifestyle & Vlogs", "Devotional", "News & Knowledge"])
    if st.button("🚀 वायरल आइडिया दो", key="gen_trend"):
        if not api_key:
            st.error("API Key चाहिए।")
        else:
            try:
                st.write_stream(stream_gen(plain_model(), f"Give 5 viral reel ideas with hooks, scripts (30 sec) and strategy for niche: {niche}. Answer in Hinglish."))
            except Exception as e:
                st.error(f"Error: {e}")
    kw = st.text_input("वीडियो का मुख्य कीवर्ड")
    if st.button("🏷 हैशटैग + SEO बनाओ", key="gen_seo"):
        if not api_key or not kw:
            st.error("API Key और कीवर्ड चाहिए।")
        else:
            try:
                st.write_stream(stream_gen(plain_model(), f"Generate 30 viral hashtags, 10 SEO keywords and 3 title options for YouTube Shorts & Instagram Reels about: {kw}"))
            except Exception as e:
                st.error(f"Error: {e}")
