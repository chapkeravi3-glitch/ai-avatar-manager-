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
def model_candidates(key: str):
    """चालू (generateContent वाले) flash मॉडल, नए से पुराने क्रम में।"""
    genai.configure(api_key=key)
    found = []
    try:
        bad = ("preview", "exp", "thinking", "image", "tts", "live", "lite", "embedding", "vision", "learn")
        for m in genai.list_models():
            if "generateContent" not in m.supported_generation_methods:
                continue
            n = m.name.replace("models/", "")
            if "flash" in n and not any(b in n for b in bad):
                mm = re.search(r"gemini-(\d+(?:\.\d+)?)", n)
                found.append((float(mm.group(1)) if mm else 0.0, n))
    except Exception:
        pass
    found.sort(key=lambda x: (-x[0], len(x[1])))
    names = [n for _, n in found]
    for extra in ("gemini-flash-latest", "gemini-3.8-flash", "gemini-3-flash", "gemini-2.5-flash", "gemini-2.0-flash"):
        if extra not in names:
            names.append(extra)
    return names


SYS_PROMPT = (
    "तुम एक स्मार्ट, गर्मजोश, इंसान जैसे पर्सनल एग्ज़ीक्यूटिव असिस्टेंट हो। "
    "यूज़र जिस भाषा में बोले (हिंदी/हिंग्लिश/English) उसी में जवाब दो। "
    "जवाब बोले जाने के लिए है: छोटे, सीधे, बातचीत वाले वाक्य, ज़्यादातर 2-4 वाक्य। "
    "markdown, बुलेट, इमोजी या लिंक मत लिखो, जब तक यूज़र लंबा या लिस्ट न मांगे।"
)


def build_model(kind, name):
    if kind == "chat":
        return genai.GenerativeModel(
            name, system_instruction=SYS_PROMPT,
            generation_config={"max_output_tokens": 500, "temperature": 0.8},
        )
    return genai.GenerativeModel(
        name, generation_config={"max_output_tokens": 2000, "temperature": 0.9}
    )


def stream_gen(kind, contents):
    """एक मॉडल 404/बंद निकले तो अपने-आप अगला मॉडल आज़माता है।"""
    genai.configure(api_key=api_key)
    names = list(model_candidates(api_key))
    good = st.session_state.get("good_model")
    if good in names:
        names.remove(good)
    if good:
        names.insert(0, good)
    last = None
    for name in names:
        started = False
        try:
            resp = build_model(kind, name).generate_content(contents, stream=True)
            for ch in resp:
                try:
                    tx = ch.text
                except Exception:
                    continue
                if tx:
                    started = True
                    yield tx
            if started:
                st.session_state.good_model = name
                return
        except Exception as e:
            if started:
                return
            last = e
            msg = str(e).lower()
            if any(k in msg for k in ("404", "no longer available", "not found", "not supported", "deprecated", "unavailable")):
                continue
            raise
    raise last or RuntimeError("कोई चालू मॉडल नहीं मिला। API Key चेक करें।")


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
# 👤 TALKING FACE (SVG - बोलते समय मुँह, आँख, भौंहें, सिर सब चलते हैं)
# ============================================================
AVATAR_TPL = """
<style>
 body{margin:0;background:transparent;font-family:sans-serif;color:#e2e8f0;text-align:center}
 .stage{width:210px;height:230px;margin:6px auto 0;border-radius:26px;overflow:hidden;
   background:radial-gradient(circle at 50% 30%,#1e3a5f,#0b1220);
   border:1px solid rgba(56,189,248,.5);box-shadow:0 0 28px rgba(56,189,248,.35)}
 svg{width:100%;height:100%;display:block}
 .bars{display:flex;gap:4px;justify-content:center;align-items:flex-end;height:26px;margin-top:8px}
 .bars i{width:5px;height:4px;border-radius:3px;background:#38bdf8;display:block}
 #st{margin-top:4px;font-size:13px;color:#34d399;font-weight:700}
 button{margin-top:6px;background:#0ea5e9;color:#fff;border:0;border-radius:20px;padding:8px 18px;font-size:14px;display:none}
</style>
<div class="stage"><svg viewBox="0 0 200 220">
 <defs>
  <clipPath id="mc"><path id="mcp" d=""/></clipPath>
  <radialGradient id="skin" cx="50%" cy="40%" r="70%"><stop offset="0" stop-color="#f6c9a3"/><stop offset="1" stop-color="#e3a77c"/></radialGradient>
 </defs>
 <path d="M18 230 C22 180 68 168 100 168 C132 168 178 180 182 230Z" fill="#1e293b"/>
 <path d="M80 170 L100 206 L120 170Z" fill="#f8fafc"/>
 <path id="tie" d="M100 180 L94 194 L100 216 L106 194Z" fill="#0ea5e9"/>
 <g id="head">
  <g id="hairBack"></g>
  <rect x="86" y="132" width="28" height="42" rx="10" fill="#d99a70"/>
  <ellipse cx="54" cy="98" rx="6" ry="10" fill="#e3a77c"/><ellipse cx="146" cy="98" rx="6" ry="10" fill="#e3a77c"/>
  <ellipse cx="100" cy="95" rx="46" ry="54" fill="url(#skin)"/>
  <g id="hairFront"></g>
  <ellipse cx="70" cy="112" rx="9" ry="5" fill="#f08a8a" opacity=".25"/><ellipse cx="130" cy="112" rx="9" ry="5" fill="#f08a8a" opacity=".25"/>
  <path id="bl" fill="none" stroke="#2a1a12" stroke-width="3.2" stroke-linecap="round"/>
  <path id="br" fill="none" stroke="#2a1a12" stroke-width="3.2" stroke-linecap="round"/>
  <g id="eL" transform="translate(80 92)"><ellipse rx="10" ry="6.5" fill="#fff"/><circle class="ir" r="4.3" fill="#3b2314"/><circle class="ir2" r="1.8" fill="#000"/><path d="M-10 -1 Q0 -9 10 -1" fill="none" stroke="#2a1a12" stroke-width="1.6"/></g>
  <g id="eR" transform="translate(120 92)"><ellipse rx="10" ry="6.5" fill="#fff"/><circle class="ir" r="4.3" fill="#3b2314"/><circle class="ir2" r="1.8" fill="#000"/><path d="M-10 -1 Q0 -9 10 -1" fill="none" stroke="#2a1a12" stroke-width="1.6"/></g>
  <path d="M100 98 Q95 114 99 117 Q104 119 107 115" fill="none" stroke="#c98a62" stroke-width="2" stroke-linecap="round"/>
  <g transform="translate(100 134)">
   <path id="inner" fill="#4a0d14"/>
   <g clip-path="url(#mc)"><rect id="teeth" x="-22" y="-4" width="44" height="4" fill="#fff"/><ellipse id="tongue" cx="0" cy="6" rx="8" ry="4" fill="#c4566a"/></g>
   <path id="lipU" fill="none" stroke="#b8475a" stroke-width="3" stroke-linecap="round"/>
   <path id="lipL" fill="none" stroke="#c9606f" stroke-width="3.6" stroke-linecap="round"/>
  </g>
 </g>
</svg></div>
<div class="bars" id="bars"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
<div id="st">● सुन रहा हूँ</div>
<button id="btn">🔊 सुनिए</button>
<script>
const G='__G__', P=__PAYLOAD__;
const $=id=>document.getElementById(id);
if(G==='f'){
  $('hairBack').innerHTML='<path d="M46 100 C36 30 164 30 154 100 C160 135 160 165 150 186 L50 186 C40 165 40 135 46 100Z" fill="#2b1a12"/>';
  $('hairFront').innerHTML='<path d="M52 94 C44 34 156 34 148 94 C144 64 124 48 98 48 C72 50 56 64 52 94Z" fill="#2b1a12"/><circle cx="53" cy="114" r="3" fill="#facc15"/><circle cx="147" cy="114" r="3" fill="#facc15"/>';
  $('tie').style.display='none';
}else{
  $('hairFront').innerHTML='<path d="M52 92 C44 30 156 30 148 92 C146 66 128 50 100 50 C72 50 54 66 52 92Z" fill="#1c1410"/>';
}
const bars=[...document.querySelectorAll('#bars i')], irs=document.querySelectorAll('.ir'), ir2s=document.querySelectorAll('.ir2');
let speaking=false, amp=0, t=0, blink=0, nextBlink=2, thinking=(P.mode==='think');
function setSpeak(v){ speaking=v; $('st').textContent = v ? '🗣 बोल रहा हूँ…' : '● सुन रहा हूँ'; }
if(thinking) $('st').textContent='🤔 सोच रहा हूँ…';
function frame(){
  t+=0.016;
  const target = speaking ? (0.25+0.75*Math.abs(Math.sin(t*10.5))*(0.5+0.5*Math.abs(Math.sin(t*3.1+1)))) : 0;
  amp += (target-amp)*0.4;
  nextBlink-=0.016; if(nextBlink<0){ blink=1; nextBlink=2+Math.random()*3; }
  blink=Math.max(0,blink-0.12);
  const sy = 1-0.95*(blink>0?Math.sin(blink*Math.PI):0);
  $('eL').setAttribute('transform','translate(80 92) scale(1 '+sy+')');
  $('eR').setAttribute('transform','translate(120 92) scale(1 '+sy+')');
  const gx=Math.sin(t*0.7)*1.8, gy=thinking?-2.6:Math.sin(t*0.5)*0.8;
  irs.forEach(e=>{e.setAttribute('cx',gx);e.setAttribute('cy',gy)}); ir2s.forEach(e=>{e.setAttribute('cx',gx);e.setAttribute('cy',gy)});
  const r=(thinking?4:1.5*amp)+Math.sin(t*0.9)*0.5;
  $('bl').setAttribute('d','M68 '+(79-r)+' Q80 '+(73-r)+' 92 '+(78-r));
  $('br').setAttribute('d','M108 '+(78-r)+' Q120 '+(73-r)+' 132 '+(79-r));
  const h=amp*13, w=14+(speaking?5*Math.sin(t*5.3+1)*amp+3*amp:0), c=-2.5*(1-Math.min(1,amp*2)), yt=-4, yb=yt+2*h+2;
  const inner='M '+(-w)+' '+c+' Q 0 '+yt+' '+w+' '+c+' Q 0 '+yb+' '+(-w)+' '+c+' Z';
  $('inner').setAttribute('d',inner); $('mcp').setAttribute('d',inner);
  $('inner').style.opacity = h>1.2?1:0;
  $('lipU').setAttribute('d','M '+(-w)+' '+c+' Q '+(-w/2)+' '+(yt-1.5)+' 0 '+(yt*0.5+c*0.5-1)+' Q '+(w/2)+' '+(yt-1.5)+' '+w+' '+c);
  $('lipL').setAttribute('d','M '+(-w)+' '+c+' Q 0 '+yb+' '+w+' '+c);
  $('teeth').setAttribute('y',0.5*c+0.5*yt); $('teeth').setAttribute('height',4*Math.min(1,h/4));
  $('tongue').setAttribute('cy',0.5*c+0.5*yb-1.5);
  const nod=speaking?Math.sin(t*3.2)*1.3*(0.5+amp):Math.sin(t*1.1)*0.6, tilt=(thinking?4:0)+Math.sin(t*0.8)*1.2;
  $('head').setAttribute('transform','translate(0 '+nod+') rotate('+tilt+' 100 175)');
  bars.forEach((b,i)=>{ b.style.height=(4+amp*22*(0.5+0.5*Math.abs(Math.sin(t*9+i))))+'px'; });
  requestAnimationFrame(frame);
}
frame();
function speakBrowser(){
  if(!P.text) return;
  let started=false;
  speechSynthesis.cancel();
  const u=new SpeechSynthesisUtterance(P.text); u.lang='hi-IN'; u.rate=1.05;
  const v=speechSynthesis.getVoices().find(v=>v.lang.replace('_','-').toLowerCase().startsWith('hi'));
  if(v) u.voice=v;
  u.onstart=()=>{started=true;setSpeak(true)};
  u.onend=()=>{started=true;setSpeak(false)};
  u.onerror=()=>{started=true;setSpeak(false);$('st').textContent='▶ "सुनिए" बटन दबाएँ'};
  speechSynthesis.speak(u);
  setTimeout(()=>{ if(!started){ setSpeak(true); setTimeout(()=>setSpeak(false), P.text.length*65); } },1200);
}
function speakAudio(){
  window._a=new Audio('data:audio/mp3;base64,'+P.audio);
  window._a.onplay=()=>setSpeak(true);
  window._a.onended=window._a.onpause=()=>setSpeak(false);
  window._a.play().catch(()=>{ $('st').textContent='▶ "सुनिए" बटन दबाएँ'; });
}
function go(){ P.audio ? speakAudio() : speakBrowser(); }
if(P.text){ $('btn').style.display='inline-block'; $('btn').onclick=go; setTimeout(go,250); }
</script>
"""


def render_avatar(slot, gender, text="", audio_b64=None, mode="idle"):
    payload = json.dumps({"text": text, "audio": audio_b64, "mode": mode}).replace("</", "<\\/")
    html = AVATAR_TPL.replace("__G__", "f" if gender == "महिला" else "m").replace("__PAYLOAD__", payload)
    with slot.container():
        components.html(html, height=335)


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

with st.expander("⚙️ सेटिंग (आवाज़, चेहरा)"):
    voice_mode = st.radio("आवाज़", ["⚡ तेज़ (फोन की आवाज़)", "🎙 ज़्यादा इंसानी (थोड़ा धीमा)"], index=0)
    gender = st.radio("चेहरा और आवाज़", ["पुरुष", "महिला"], horizontal=True)
    default_music = st.selectbox("गाना चलाने के लिए डिफ़ॉल्ट ऐप", ["YouTube", "Spotify", "JioSaavn"])

EDGE_VOICE = "hi-IN-MadhurNeural" if gender == "पुरुष" else "hi-IN-SwaraNeural"

st.markdown("<h3 style='text-align:center;margin:0'>👑 Executive AI Agent</h3>", unsafe_allow_html=True)
avatar_slot = st.empty()
render_avatar(avatar_slot, gender)

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

            render_avatar(avatar_slot, gender, mode="think")
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
                        reply = st.write_stream(stream_gen("chat", history + [last]))
                    except Exception as e:
                        reply = f"⚠️ दिक्कत आई: {e}"
                        st.markdown(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply, **(link or {})})

            spoken = speech_clean(reply)
            audio_b64 = None
            if spoken and voice_mode.startswith("🎙"):
                audio_b64 = edge_b64(spoken, EDGE_VOICE)
            render_avatar(avatar_slot, gender, text=spoken, audio_b64=audio_b64)

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
                st.write_stream(stream_gen("plain", f"{prompts[what]} Tone: {tone}. Language: {lang}."))
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
                st.write_stream(stream_gen("plain", f"Give 5 viral reel ideas with hooks, scripts (30 sec) and strategy for niche: {niche}. Answer in Hinglish."))
            except Exception as e:
                st.error(f"Error: {e}")
    kw = st.text_input("वीडियो का मुख्य कीवर्ड")
    if st.button("🏷 हैशटैग + SEO बनाओ", key="gen_seo"):
        if not api_key or not kw:
            st.error("API Key और कीवर्ड चाहिए।")
        else:
            try:
                st.write_stream(stream_gen("plain", f"Generate 30 viral hashtags, 10 SEO keywords and 3 title options for YouTube Shorts & Instagram Reels about: {kw}"))
            except Exception as e:
                st.error(f"Error: {e}")
