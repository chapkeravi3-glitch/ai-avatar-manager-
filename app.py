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
import os
import re
import time
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
    """चालू मॉडल: पहले flash (नए से पुराने), फिर lite, फिर बैकअप नाम। हर मॉडल की फ्री लिमिट अलग होती है।"""
    genai.configure(api_key=key)
    flash, lite = [], []
    try:
        bad = ("preview", "exp", "thinking", "image", "tts", "live", "embedding", "vision", "learn", "audio")
        for m in genai.list_models():
            if "generateContent" not in m.supported_generation_methods:
                continue
            n = m.name.replace("models/", "")
            if "flash" not in n or any(b in n for b in bad):
                continue
            mm = re.search(r"gemini-(\d+(?:\.\d+)?)", n)
            item = (float(mm.group(1)) if mm else 0.0, n)
            (lite if "lite" in n else flash).append(item)
    except Exception:
        pass
    order = lambda L: [n for _, n in sorted(L, key=lambda x: (-x[0], len(x[1])))]
    names = order(flash) + order(lite)
    for extra in ("gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3.8-flash", "gemini-3-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"):
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
    """404 (बंद मॉडल) या 429 (लिमिट खत्म) आए तो अपने-आप अगला मॉडल आज़माता है।"""
    genai.configure(api_key=api_key)
    names = list(model_candidates(api_key))
    good = st.session_state.get("good_model")
    if good in names:
        names.remove(good)
        names.insert(0, good)
    dead = st.session_state.setdefault("dead_models", {})
    now = time.time()
    last, quota_hit = None, False
    for name in names:
        if now - dead.get(name, 0) < 900:
            quota_hit = quota_hit or dead.get(name) is not None
            continue
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
            if any(k in msg for k in ("429", "quota", "resource_exhausted", "rate limit")):
                quota_hit = True
                dead[name] = time.time()
                continue
            if any(k in msg for k in ("404", "no longer available", "not found", "not supported", "deprecated", "unavailable")):
                dead[name] = time.time()
                continue
            raise
    if quota_hit:
        raise RuntimeError(
            "आज की फ्री लिमिट सभी मॉडलों पर खत्म हो गई है (फ्री में हर मॉडल पर रोज़ सिर्फ़ ~20 रिक्वेस्ट मिलती हैं)। "
            "कल दोबारा चलेगा, या Google AI Studio में billing चालू करें, या नए प्रोजेक्ट की नई Key बनाएँ।"
        )
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


PHOTO_TPL = """
<style>
 body{margin:0;background:transparent;font-family:sans-serif;color:#e2e8f0;text-align:center}
 canvas{width:230px;border-radius:24px;border:1px solid rgba(56,189,248,.5);box-shadow:0 0 28px rgba(56,189,248,.35);margin-top:6px}
 .bars{display:flex;gap:4px;justify-content:center;align-items:flex-end;height:26px;margin-top:8px}
 .bars i{width:5px;height:4px;border-radius:3px;background:#38bdf8;display:block}
 #st{margin-top:4px;font-size:13px;color:#34d399;font-weight:700}
 button{margin-top:6px;background:#0ea5e9;color:#fff;border:0;border-radius:20px;padding:8px 18px;font-size:14px;display:none}
</style>
<canvas id="cv"></canvas>
<div class="bars" id="bars"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
<div id="st">● सुन रहा हूँ</div>
<button id="btn">🔊 सुनिए</button>
<script>
const P=__PAYLOAD__, F=__PHOTO__;
const $=id=>document.getElementById(id);
const cv=$('cv'), ctx=cv.getContext('2d'), off=document.createElement('canvas'), octx=off.getContext('2d');
const bars=[...document.querySelectorAll('#bars i')];
let speaking=false, amp=0, t=0, thinking=(P.mode==='think'), W=480, H=600;
function setSpeak(v){ speaking=v; $('st').textContent = v ? '🗣 बोल रहा हूँ…' : '● सुन रहा हूँ'; }
if(thinking) $('st').textContent='🤔 सोच रहा हूँ…';
const img=new Image();
img.onload=()=>{ H=Math.min(640,Math.round(W*img.height/img.width)); cv.width=W; cv.height=H; off.width=W; off.height=H; frame(); };
img.onerror=()=>{ $('st').textContent='⚠️ फोटो लोड नहीं हुई, दूसरी JPG फोटो डालें'; };
img.src=F.src;
function frame(){
  t+=0.016;
  const target = speaking ? (0.25+0.75*Math.abs(Math.sin(t*10.5))*(0.5+0.5*Math.abs(Math.sin(t*3.1+1)))) : 0;
  amp += (target-amp)*0.4;
  const sway=Math.sin(t*0.8)*0.5+(thinking?2.5:0), bob=speaking?Math.sin(t*3.2)*1.6*(0.4+amp):Math.sin(t*1.1)*1.2;
  ctx.clearRect(0,0,W,H); ctx.save();
  ctx.translate(W/2,H*0.6); ctx.rotate(sway*Math.PI/180); ctx.scale(1.04,1.04); ctx.translate(-W/2,-H*0.6+bob);
  ctx.drawImage(img,0,0,W,H);
  const mx=F.mx*W, my=F.my*H, mw=F.mw*W, open=amp*mw*0.22;
  if(open>0.8){
    octx.globalCompositeOperation='source-over'; octx.clearRect(0,0,W,H);
    octx.drawImage(img,0,open,W,H);
    octx.globalCompositeOperation='destination-in';
    let g=octx.createLinearGradient(0,my-3,0,my+4); g.addColorStop(0,'rgba(0,0,0,0)'); g.addColorStop(1,'rgba(0,0,0,1)');
    octx.fillStyle=g; octx.fillRect(0,0,W,H);
    octx.globalCompositeOperation='destination-in';
    const R=mw*1.7; let rg=octx.createRadialGradient(mx,my+mw*0.8,R*0.35,mx,my+mw*0.8,R);
    rg.addColorStop(0,'rgba(0,0,0,1)'); rg.addColorStop(1,'rgba(0,0,0,0)');
    octx.fillStyle=rg; octx.fillRect(0,0,W,H);
    // पहले मुँह का अंदर (गैप), फिर नीचे का जबड़ा
    ctx.fillStyle='#3a0b10'; ctx.beginPath(); ctx.ellipse(mx,my+open*0.5,mw*0.46,open*0.62+1,0,0,Math.PI*2); ctx.fill();
    ctx.fillStyle='rgba(245,240,235,'+Math.min(.9,open/9)+')'; ctx.beginPath(); ctx.ellipse(mx,my+open*0.18,mw*0.36,Math.max(1,open*0.2),0,0,Math.PI*2); ctx.fill();
    ctx.drawImage(off,0,0);
  }
  if(F.guide){ ctx.strokeStyle='#ef4444'; ctx.lineWidth=2; ctx.strokeRect(mx-mw/2,my-6,mw,12); ctx.beginPath(); ctx.moveTo(mx-12,my); ctx.lineTo(mx+12,my); ctx.moveTo(mx,my-12); ctx.lineTo(mx,my+12); ctx.stroke(); }
  ctx.restore();
  bars.forEach((b,i)=>{ b.style.height=(4+amp*22*(0.5+0.5*Math.abs(Math.sin(t*9+i))))+'px'; });
  requestAnimationFrame(frame);
}
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


EXTRA_TPL = """
<style>
#mic{margin-top:8px;width:210px;background:#16a34a;color:#fff;border:0;border-radius:24px;padding:12px;font-size:16px;font-weight:700}
.act{display:block;width:186px;margin:8px auto 0;background:#f59e0b;color:#111;text-decoration:none;border-radius:24px;padding:12px;font-size:16px;font-weight:700}
</style>
<button id="mic">🎤 बोलिए</button>
<div id="acts"></div>
<script>
(function(){
  const L=__LINKS__;
  const ANDROID=/Android/i.test(navigator.userAgent);
  function target(l){
    if(!ANDROID||!l.pkg) return l.url;
    const x=new URL(l.url);
    return 'intent://'+x.host+x.pathname+x.search+x.hash+'#Intent;scheme='+x.protocol.replace(':','')+';package='+l.pkg+';S.browser_fallback_url='+encodeURIComponent(l.url)+';end';
  }
  const box=document.getElementById('acts');
  L.forEach(l=>{ const a=document.createElement('a'); a.className='act'; a.textContent=l.label; a.href=target(l); a.target='_blank'; a.rel='noopener'; box.appendChild(a); });
  if(L.length===1){ try{ const d=window.parent.document, a=d.createElement('a'); a.href=target(L[0]); a.target='_blank'; d.body.appendChild(a); a.click(); a.remove(); }catch(e){} }

  const b=document.getElementById('mic');
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){ b.textContent='🎤 Chrome ब्राउज़र में खोलें'; b.disabled=true; return; }
  const rec=new SR(); rec.lang='hi-IN'; rec.interimResults=false; rec.maxAlternatives=1;
  let on=false;
  b.onclick=()=>{ if(on){ rec.stop(); return; } try{ speechSynthesis.cancel(); }catch(e){} try{ rec.start(); }catch(e){} };
  rec.onstart=()=>{ on=true; b.textContent='🔴 सुन रहा हूँ… बोलिए'; };
  rec.onend=()=>{ on=false; if(b.textContent.indexOf('सुन रहा')>=0) b.textContent='🎤 बोलिए'; };
  rec.onerror=(e)=>{ on=false; b.textContent='🎤 माइक की अनुमति दें ('+e.error+')'; };
  rec.onresult=(e)=>{
    const text=e.results[0][0].transcript; b.textContent='✅ '+text;
    try{
      const d=window.parent.document;
      const ta=d.querySelector('textarea[data-testid="stChatInputTextArea"]')||d.querySelector('[data-testid="stChatInput"] textarea');
      const setter=Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype,'value').set;
      setter.call(ta,text); ta.dispatchEvent(new window.parent.Event('input',{bubbles:true}));
      setTimeout(()=>{ const s=d.querySelector('[data-testid="stChatInputSubmitButton"]'); if(s) s.click(); },200);
    }catch(err){ b.textContent='चैट बॉक्स में खुद टाइप करें: '+text; }
  };
})();
</script>
"""


def render_avatar(slot, gender, text="", audio_b64=None, mode="idle", links=None):
    links = links or []
    payload = json.dumps({"text": text, "audio": audio_b64, "mode": mode}).replace("</", "<\\/")
    if PHOTO:
        html = PHOTO_TPL.replace("__PAYLOAD__", payload).replace("__PHOTO__", json.dumps(PHOTO))
        height = 560
    else:
        html = AVATAR_TPL.replace("__G__", "f" if gender == "महिला" else "m").replace("__PAYLOAD__", payload)
        height = 420
    html += EXTRA_TPL.replace("__LINKS__", json.dumps(links).replace("</", "<\\/"))
    with slot.container():
        components.html(html, height=height + 62 * len(links))


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


PKG = {
    "YouTube": "com.google.android.youtube", "Spotify": "com.spotify.music", "JioSaavn": "com.jio.media.jiobeats",
    "Instagram": "com.instagram.android", "WhatsApp": "com.whatsapp", "Facebook": "com.facebook.katana",
    "X (Twitter)": "com.twitter.android", "Telegram": "org.telegram.messenger", "Snapchat": "com.snapchat.android",
    "LinkedIn": "com.linkedin.android", "Google Maps": "com.google.android.apps.maps", "Gmail": "com.google.android.gm",
    "Google": "com.google.android.googlequicksearchbox", "Play Store": "com.android.vending",
    "Amazon": "in.amazon.mShop.android.shopping", "Flipkart": "com.flipkart.android",
}
JOIN = (
    ("यू ट्यूब", "यूट्यूब"), ("you tube", "youtube"), ("face book", "facebook"), ("फेस बुक", "फेसबुक"),
    ("insta gram", "instagram"), ("whats app", "whatsapp"), ("व्हाट्स एप", "व्हाट्सएप"),
    ("इंस्टा ग्राम", "इंस्टाग्राम"), ("प्ले स्टोर", "प्लेस्टोर"), ("गूगल मैप", "मैप"),
)


def tokens_of(text):
    low = text.lower()
    for a, b in JOIN:
        low = low.replace(a, b)
    return [w for w in re.split(r"[\s,।.!?]+", low) if w]


def handle_command(text, default_music):
    """ऐप खोलने/गाना चलाने वाला कमांड हो तो dict लौटाता है, वरना None।"""
    toks = tokens_of(text)
    if not any(any(v in w for v in VERB_STEMS) for w in toks):
        return None

    found = [name for name, (al, _, _) in APPS.items() if any(w in al for w in toks)]
    is_music = any(w in MUSIC_WORDS for w in toks)
    blocked = any(w.startswith(b) for w in toks for b in BLOCK)
    note = " बैंकिंग और पेमेंट वाले ऐप मैं नहीं खोलता।" if blocked else ""
    if blocked and not found:
        return {"msg": "माफ़ कीजिए, मैं बैंकिंग और पेमेंट वाले ऐप नहीं खोलता। आपके पैसों की सुरक्षा के लिए इन्हें आप खुद ही खोलिए।", "links": []}
    if not found and not is_music:
        return None
    if not found:
        found = [default_music]

    all_alias = {a for n in found for a in APPS[n][0]}
    q = " ".join(
        w for w in toks
        if w not in all_alias and w not in FILLER and not any(v in w for v in VERB_STEMS)
        and not any(w.startswith(x) for x in BLOCK)
    ).strip()
    if len(found) > 1:
        q = ""
    links = []
    for n in found:
        _, home, search = APPS[n]
        url = search.format(q=urllib.parse.quote_plus(q)) if q else home
        links.append({"label": f"▶ {n} खोलें", "url": url, "pkg": PKG.get(n, "")})
    names = " और ".join(found)
    if q:
        msg = f"ठीक है, {names} पर {q} लगा रहा हूँ। स्क्रीन पर नारंगी बटन दबाइए।"
    else:
        msg = f"ठीक है, {names} खोल रहा हूँ। स्क्रीन पर नारंगी बटन दबाइए।"
    return {"msg": msg + note, "links": links}


# ============================================================
# ⚙️ SETTINGS
# ============================================================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_audio" not in st.session_state:
    st.session_state.last_audio = ""

with st.expander("⚙️ सेटिंग (आवाज़, चेहरा)", expanded=True):
    voice_mode = st.radio("आवाज़", ["⚡ तेज़ (फोन की आवाज़)", "🎙 ज़्यादा इंसानी (थोड़ा धीमा)"], index=0)
    gender = st.radio("चेहरा और आवाज़", ["पुरुष", "महिला"], horizontal=True)
    default_music = st.selectbox("गाना चलाने के लिए डिफ़ॉल्ट ऐप", ["YouTube", "Spotify", "JioSaavn"])
    up = st.file_uploader("👤 असली इंसानी चेहरा: किसी आदमी की सामने से, साफ़ फोटो डालें (अपनी या जिसकी अनुमति हो)", type=["png", "jpg", "jpeg"])
    mx = st.slider("मुँह की जगह: बाएँ-दाएँ", 0, 100, 50)
    my = st.slider("मुँह की जगह: ऊपर-नीचे", 0, 100, 68)
    mw = st.slider("मुँह की चौड़ाई", 5, 40, 18)
    show_guide = st.checkbox("लाल निशान दिखाओ (मुँह पर ठीक बिठाने के लिए)")

EDGE_VOICE = "hi-IN-MadhurNeural" if gender == "पुरुष" else "hi-IN-SwaraNeural"
FACE_FILE = next((p for p in ("face.jpg", "face.jpeg", "face.png") if os.path.exists(p)), None)
PHOTO = None
if up is not None or FACE_FILE:
    try:
        import io
        from PIL import Image
        im = Image.open(up if up is not None else FACE_FILE).convert("RGB")
        im.thumbnail((640, 800))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=85)
        PHOTO = {"src": "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(),
                 "mx": mx / 100, "my": my / 100, "mw": mw / 100, "guide": show_guide}
    except Exception:
        PHOTO = None
        st.warning("फोटो पढ़ नहीं पाया। JPG या PNG की दूसरी फोटो डालिए।")

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
        with st.expander("🎙 बैकअप: रिकॉर्ड करके पूछें (सिर्फ़ सवाल-जवाब, ऐप खोलने के लिए ऊपर हरा 🎤 बटन दबाएँ)"):
            audio_val = st.audio_input("रिकॉर्ड दबाएँ, बात करें, रोकें")

    typed = st.chat_input("यहाँ टाइप करें… (जैसे: यूट्यूब पर अरिजीत के गाने चलाओ)")

    for i, m in enumerate(st.session_state.messages):
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
            for j, l in enumerate(m.get("links", [])):
                st.link_button(l["label"], l["url"], key=f"old{i}_{j}")

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
            reply, links = "", []
            with st.chat_message("assistant"):
                if cmd:
                    reply = cmd["msg"]
                    st.markdown(reply)
                    links = cmd.get("links", [])
                    for j, l in enumerate(links):
                        st.link_button(l["label"], l["url"], key=f"new{len(st.session_state.messages)}_{j}")
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
                        reply = f"⚠️ दिक्कत आई: {str(e)[:400]}"
                        st.markdown(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply, **({"links": links} if links else {})})

            spoken = speech_clean(reply)
            audio_b64 = None
            if spoken and voice_mode.startswith("🎙"):
                audio_b64 = edge_b64(spoken, EDGE_VOICE)
            render_avatar(avatar_slot, gender, text=spoken, audio_b64=audio_b64, links=links)

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
