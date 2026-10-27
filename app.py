import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Autonomous Executive AI Human Agent",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# API Key Check from Streamlit Secrets or Sidebar
api_key = ""
if "GEMINI_API_KEY" in st.secrets:
  api_key = st.secrets["GEMINI_API_KEY"]

st.sidebar.title("⚙️ System Configuration")
k_input = st.sidebar.text_input(
    "Enter Gemini API Key", type="password", value=api_key
)
if k_input:
  api_key = k_input

# ==========================================
# 🎨 ULTIMATE CINEMATIC UI & TALKING AVATAR HTML/JS
# ==========================================
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Executive Agent</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: radial-gradient(circle at top, #0f172a 0%, #020617 100%); color: #f8fafc; min-height: 100vh; padding: 15px; }
        
        .container { max-width: 950px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }

        /* Cinematic Talking Avatar Hero */
        .avatar-hero {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.85), rgba(15, 23, 42, 0.95));
            border-radius: 24px;
            border: 1px solid rgba(56, 189, 248, 0.4);
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.8), inset 0 0 25px rgba(56, 189, 248, 0.1);
            backdrop-filter: blur(12px);
        }

        .neural-face {
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

        .avatar-img {
            width: 130px;
            height: 130px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid rgba(255,255,255,0.9);
        }

        /* Speaking Waveform Animation */
        .sound-waves {
            display: flex;
            gap: 4px;
            margin-top: 10px;
            height: 20px;
            align-items: center;
        }
        .wave {
            width: 4px;
            height: 8px;
            background: #38bdf8;
            border-radius: 2px;
            animation: wave-anim 1s infinite ease-in-out;
        }
        .wave:nth-child(2) { animation-delay: 0.2s; }
        .wave:nth-child(3) { animation-delay: 0.4s; }
        .wave:nth-child(4) { animation-delay: 0.6s; }

        @keyframes wave-anim {
            0%, 100% { height: 6px; background: #38bdf8; }
            50% { height: 22px; background: #34d399; box-shadow: 0 0 12px #34d399; }
        }

        .status-badge {
            margin-top: 8px;
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid #10b981;
            color: #34d399;
            padding: 4px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .dot { width: 6px; height: 6px; background: #34d399; border-radius: 50%; animation: blink 1s infinite alternate; }
        @keyframes blink { 0% { opacity: 0.3; } 100% { opacity: 1; } }

        .speech-bubble {
            margin-top: 10px;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 10px 18px;
            border-radius: 14px;
            font-size: 13px;
            color: #e2e8f0;
            text-align: center;
            max-width: 650px;
        }

        /* Navigation Tabs */
        .tabs-header {
            display: flex;
            gap: 8px;
            background: #0b0f19;
            padding: 10px;
            border-radius: 14px;
            border: 1px solid #1e293b;
            overflow-x: auto;
        }
        .tab-btn {
            background: #111827;
            border: 1px solid #1f2937;
            color: #94a3b8;
            padding: 10px 16px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            white-space: nowrap;
            transition: 0.2s;
        }
        .tab-btn.active {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
            border-color: #38bdf8;
            box-shadow: 0 0 12px rgba(2, 132, 199, 0.5);
        }

        .tab-content { display: none; background: #0b0f19; border: 1px solid #1e293b; border-radius: 16px; padding: 20px; min-height: 320px; }
        .tab-content.active { display: flex; flex-direction: column; gap: 15px; }

        /* Chat Window */
        .chat-box {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 15px;
            height: 250px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .message { padding: 10px 14px; border-radius: 12px; max-width: 80%; font-size: 13px; line-height: 1.4; }
        .user-msg { background: #0284c7; color: white; align-self: flex-end; }
        .ai-msg { background: #1e293b; color: #f8fafc; align-self: flex-start; border: 1px solid #334155; }

        /* Inputs & Buttons */
        .input-row { display: flex; gap: 10px; }
        input, select, textarea {
            flex: 1;
            background: #0f172a;
            border: 1px solid #334155;
            color: white;
            padding: 12px;
            border-radius: 10px;
            font-size: 14px;
            outline: none;
        }
        input:focus, select:focus { border-color: #38bdf8; box-shadow: 0 0 8px rgba(56,189,248,0.3); }

        .primary-btn {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
        }
        .primary-btn:hover { opacity: 0.9; }

        .result-box {
            background: #0f172a;
            border: 1px solid #334155;
            padding: 12px;
            border-radius: 10px;
            font-size: 13px;
            color: #cbd5e1;
            max-height: 180px;
            overflow-y: auto;
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- Cinematic Hero with Talking Avatar -->
        <div class="avatar-hero">
            <div class="neural-face" id="neuralFace">
                <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80" class="avatar-img" alt="AI Manager">
            </div>
            <!-- Live Speaking Sound Waves -->
            <div class="sound-waves" id="soundWaves" style="opacity: 0.3;">
                <div class="wave"></div>
                <div class="wave"></div>
                <div class="wave"></div>
                <div class="wave"></div>
            </div>
            <div class="status-badge">
                <div class="dot"></div> REAL-TIME TALKING EXECUTIVE ACTIVE
            </div>
            <div class="speech-bubble" id="speechText">
                "नमस्ते बॉस! मैं आपकी ऑटोनॉमस एआई मैनेजर हूँ। बोलिए, आज क्या बातचीत करनी है?"
            </div>
        </div>

        <!-- Navigation Tabs -->
        <div class="tabs-header">
            <button class="tab-btn active" onclick="switchTab(0)">💬 Executive Chat</button>
            <button class="tab-btn" onclick="switchTab(1)">🔥 Trend & Reels</button>
            <button class="tab-btn" onclick="switchTab(2)">🎵 Music & Audio</button>
            <button class="tab-btn" onclick="switchTab(3)">📱 Social Media</button>
            <button class="tab-btn" onclick="switchTab(4)">🏷️ SEO & Hashtags</button>
        </div>

        <!-- TAB 1: CHAT -->
        <div class="tab-content active" id="tab-0">
            <h3>💬 Direct Neural Chat with Executive Agent (Instant Reply)</h3>
            <div class="chat-box" id="chatBox">
                <div class="message ai-msg">नमस्ते! मैं पूरी तरह तैयार हूँ। मुझसे कुछ भी पूछिए, जवाब तुरंत मिलेगा।</div>
            </div>
            <div class="input-row">
                <input type="text" id="userInput" placeholder="यहाँ कुछ भी टाइप करें (जैसे: हैलो)..." onkeydown="if(event.key === 'Enter') sendChatMessage()">
                <button class="primary-btn" onclick="sendChatMessage()">भेजें 🚀</button>
            </div>
        </div>

        <!-- TAB 2: TRENDS -->
        <div class="tab-content" id="tab-1">
            <h3>🔥 Viral Trend & Reel Idea Generator</h3>
            <select id="nicheSelect">
                <option>Tech & Artificial Intelligence</option>
                <option>Entertainment & Comedy</option>
                <option>Business & Startup Strategy</option>
                <option>Lifestyle & Daily Vlogs</option>
            </select>
            <button class="primary-btn" onclick="generateTrends()">ट्रेंड्स और रील्स आइडिया खोजें</button>
            <div class="result-box" id="trendResult">यहाँ ट्रेंडिंग टॉपिक्स और स्क्रिप्ट आइडिया दिखेंगे...</div>
        </div>

        <!-- TAB 3: MUSIC -->
        <div class="tab-content" id="tab-2">
            <h3>🎵 Audio & Music Maestro Agent</h3>
            <input type="text" id="songInput" placeholder="जो गाना सुनना हो उसका नाम लिखें...">
            <button class="primary-btn" onclick="searchMusic()">गाना तुरंत खोजें</button>
            <div class="result-box" id="musicResult">गाने के YouTube और Spotify लिंक्स यहाँ आएंगे...</div>
        </div>

        <!-- TAB 4: SOCIAL MEDIA -->
        <div class="tab-content" id="tab-3">
            <h3>📱 Multi-Platform Social Media Manager</h3>
            <select id="platformSelect">
                <option>YouTube Studio Strategy & Description</option>
                <option>Instagram Reel & Post Caption</option>
                <option>Facebook Page Engagement Post</option>
            </select>
            <input type="text" id="postTopic" placeholder="किस टॉपिक पर पोस्ट तैयार करनी है?">
            <button class="primary-btn" onclick="generatePost()">पोस्ट और कैप्शन बनाएं</button>
            <div class="result-box" id="postResult">सोशल मीडिया पोस्ट यहाँ जनरेट होगी...</div>
        </div>

        <!-- TAB 5: SEO -->
        <div class="tab-content" id="tab-4">
            <h3>🏷️ SEO & Viral Hashtag Generator</h3>
            <input type="text" id="seoKeyword" placeholder="अपने वीडियो का मुख्य कीवर्ड लिखें...">
            <button class="primary-btn" onclick="generateHashtags()">वायरल हैशटैग्स बनाएं</button>
            <div class="result-box" id="seoResult">वायरल हैशटैग्स और SEO कीवर्ड्स यहाँ आएंगे...</div>
        </div>
    </div>

    <script>
        const apiKey = "__API_KEY_PLACEHOLDER__";

        function switchTab(index) {
            const tabs = document.querySelectorAll('.tab-btn');
            const contents = document.querySelectorAll('.tab-content');
            tabs.forEach((t, i) => {
                t.classList.toggle('active', i === index);
                contents[i].classList.toggle('active', i === index);
            });
        }

        // Text-to-Speech Function to make the Avatar "Speak" aloud like real chat
        function speakText(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel(); // Stop previous speech
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'hi-IN'; // Set to Hindi/Hinglish voice support
                utterance.rate = 1.0;
                
                const soundWaves = document.getElementById("soundWaves");
                utterance.onstart = () => { soundWaves.style.opacity = "1"; };
                utterance.onend = () => { soundWaves.style.opacity = "0.3"; };
                
                window.speechSynthesis.speak(utterance);
            }
        }

        async function callGemini(promptText, resultCallback) {
            if(!apiKey) {
                alert("कृपया पहले साइडबार में अपनी Gemini API Key दर्ज करें!");
                return;
            }

            const speechText = document.getElementById("speechText");
            const soundWaves = document.getElementById("soundWaves");
            
            speechText.innerText = "⚡ सोच रही हूँ...";
            soundWaves.style.opacity = "1";

            try {
                const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=${apiKey}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: [{
                            parts: [{ text: "You are an elite, human-like virtual executive manager. Reply smartly, conversationally, and concisely in natural Hinglish/Hindi. " + promptText }]
                        }]
                    })
                });

                const data = await response.json();
                if(data.candidates && data.candidates[0].content.parts[0].text) {
                    const reply = data.candidates[0].content.parts[0].text;
                    resultCallback(reply);
                    speechText.innerText = `"${reply.substring(0, 90)}..."`;
                    speakText(reply); // Avatar speaks out loud!
                } else {
                    resultCallback("⚠️ API से सही जवाब नहीं मिला।");
                    speechText.innerText = "⚠️ एरर आ गया है।";
                }
            } catch (error) {
                resultCallback("⚠️ Network Error: " + error.message);
                speechText.innerText = "⚠️ नेटवर्क में समस्या है।";
            }
            soundWaves.style.opacity = "0.3";
        }

        function sendChatMessage() {
            const inputField = document.getElementById("userInput");
            const chatBox = document.getElementById("chatBox");
            const text = inputField.value.trim();
            if(!text) return;

            chatBox.innerHTML += `<div class="message user-msg">${text}</div>`;
            inputField.value = "";
            chatBox.scrollTop = chatBox.scrollHeight;

            callGemini("User: " + text, (reply) => {
                chatBox.innerHTML += `<div class="message ai-msg">${reply}</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            });
        }

        function generateTrends() {
            const niche = document.getElementById("nicheSelect").value;
            const resBox = document.getElementById("trendResult");
            resBox.innerHTML = "स्कैन हो रहा है...";
            callGemini(`Give 3 top trending topics, viral hooks, and strategy for: ${niche}`, (reply) => {
                resBox.innerHTML = reply.replace(/\\n/g, '<br>');
            });
        }

        function searchMusic() {
            const song = document.getElementById("songInput").value.trim();
            const resBox = document.getElementById("musicResult");
            if(!song) { resBox.innerHTML = "कृपया गाने का नाम लिखें।"; return; }
            
            const enc = encodeURIComponent(song);
            resBox.innerHTML = `
                <b>🎵 '${song}' के लिए लिंक्स:</b><br><br>
                <a href="https://www.youtube.com/results?search_query=${enc}" target="_blank" style="color: #ef4444; font-weight: bold; margin-right: 15px;">▶ YouTube पर सुनें</a>
                <a href="https://open.spotify.com/search/${enc}" target="_blank" style="color: #22c55e; font-weight: bold;">🎧 Spotify पर सुनें</a>
            `;
            const msg = `आपके लिए ${song} के YouTube और Spotify लिंक्स तैयार हैं।`;
            document.getElementById("speechText").innerText = msg;
            speakText(msg);
        }

        function generatePost() {
            const plat = document.getElementById("platformSelect").value;
            const top = document.getElementById("postTopic").value.trim();
            const resBox = document.getElementById("postResult");
            if(!top) { resBox.innerHTML = "कृपया टॉपिक दर्ज करें।"; return; }

            resBox.innerHTML = "तैयार हो रहा है...";
            callGemini(`Create an expert engaging post and strategy for ${plat} about: ${top}`, (reply) => {
                resBox.innerHTML = reply.replace(/\\n/g, '<br>');
            });
        }

        function generateHashtags() {
            const kw = document.getElementById("seoKeyword").value.trim();
            const resBox = document.getElementById("seoResult");
            if(!kw) { resBox.innerHTML = "कृपया कीवर्ड दर्ज करें।"; return; }

            resBox.innerHTML = "खोजा जा रहा है...";
            callGemini(`Generate 30 high-ranking viral hashtags and SEO keywords for YouTube Shorts & Instagram Reels for: {kw}`, (reply) => {
                resBox.innerHTML = reply.replace(/\\n/g, '<br>');
            });
        }
    </script>
</body>
</html>
"""

# Inject API Key safely
html_code = html_template.replace("__API_KEY_PLACEHOLDER__", api_key)

# Render in Streamlit
import streamlit.components.v1 as components

components.html(html_code, height=750, scrolling=True)
