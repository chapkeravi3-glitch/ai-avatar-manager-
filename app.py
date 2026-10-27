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
k_input = st.sidebar.text_input("Enter Gemini API Key", type="password", value=api_key)
if k_input:
  api_key = k_input

# ==========================================
# 🎨 ULTRA-FAST CINEMATIC UI & TALKING AVATAR HTML/JS
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
        body { background: radial-gradient(circle at top, #0f172a 0%, #020617 100%); color: #f8fafc; min-height: 100vh; padding: 20px; }
        
        .container { max-width: 900px; margin: 0 auto; display: flex; flex-direction: column; gap: 20px; }

        /* Cinematic Talking Avatar Hero */
        .avatar-hero {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.95));
            border-radius: 24px;
            border: 1px solid rgba(56, 189, 248, 0.4);
            padding: 25px;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: 0 20px 50px rgba(0,0,0,0.8), inset 0 0 25px rgba(56, 189, 248, 0.1);
            backdrop-filter: blur(12px);
        }

        .neural-face {
            position: relative;
            width: 150px;
            height: 150px;
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
            width: 140px;
            height: 140px;
            border-radius: 50%;
            object-fit: cover;
            border: 3px solid rgba(255,255,255,0.9);
        }

        .status-badge {
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

        .dot { width: 7px; height: 7px; background: #34d399; border-radius: 50%; animation: blink 1s infinite alternate; }
        @keyframes blink { 0% { opacity: 0.3; } 100% { opacity: 1; } }

        .speech-bubble {
            margin-top: 12px;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 12px 20px;
            border-radius: 16px;
            font-size: 14px;
            color: #e2e8f0;
            text-align: center;
            max-width: 600px;
        }

        /* Chat Window */
        .chat-box {
            background: #0b0f19;
            border: 1px solid #1e293b;
            border-radius: 20px;
            padding: 20px;
            height: 350px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            box-shadow: inset 0 4px 15px rgba(0,0,0,0.5);
        }

        .message {
            padding: 12px 18px;
            border-radius: 14px;
            max-width: 80%;
            font-size: 14px;
            line-height: 1.5;
        }

        .user-msg { background: #0284c7; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .ai-msg { background: #1e293b; color: #f8fafc; align-self: flex-start; border-bottom-left-radius: 2px; border: 1px solid #334155; }

        .input-area {
            display: flex;
            gap: 10px;
        }

        input[type="text"] {
            flex: 1;
            background: #0f172a;
            border: 1px solid #334155;
            color: white;
            padding: 14px;
            border-radius: 12px;
            font-size: 15px;
            outline: none;
        }
        input[type="text"]:focus { border-color: #38bdf8; box-shadow: 0 0 10px rgba(56,189,248,0.3); }

        button {
            background: linear-gradient(135deg, #0284c7, #2563eb);
            color: white;
            border: none;
            padding: 0 25px;
            border-radius: 12px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }
        button:hover { opacity: 0.9; transform: scale(1.02); }
    </style>
</head>
<body>

    <div class="container">
        <!-- Cinematic Hero -->
        <div class="avatar-hero">
            <div class="neural-face" id="neuralFace">
                <img src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80" class="avatar-img" alt="AI Manager">
            </div>
            <div class="status-badge">
                <div class="dot"></div> ULTRA-FAST NEURAL EXECUTIVE ACTIVE
            </div>
            <div class="speech-bubble" id="speechText">
                "नमस्ते बॉस! बोलिए, आज आपके लिए क्या किया जाए?"
            </div>
        </div>

        <!-- Chat Interface -->
        <div class="chat-box" id="chatBox">
            <div class="message ai-msg">नमस्ते! मैं आपकी ऑटोनॉमस एआई मैनेजर हूँ। आप मुझसे कुछ भी पूछ सकते हैं, जवाब बिल्कुल तुरंत मिलेगा।</div>
        </div>

        <!-- Input Box -->
        <div class="input-area">
            <input type="text" id="userInput" placeholder="यहाँ अपना संदेश या कमांड लिखें (जैसे: हेलो)..." onkeydown="if(event.key === 'Enter') sendMessage()">
            <button onclick="sendMessage()">भेजें 🚀</button>
        </div>
    </div>

    <script>
        const apiKey = "__API_KEY_PLACEHOLDER__";

        async function sendMessage() {
            const inputField = document.getElementById("userInput");
            const chatBox = document.getElementById("chatBox");
            const speechText = document.getElementById("speechText");
            const neuralFace = document.getElementById("neuralFace");
            
            const text = inputField.value.trim();
            if(!text) return;

            if(!apiKey) {
                alert("कृपया पहले साइडबार में अपनी Gemini API Key दर्ज करें!");
                return;
            }

            // Append User Message
            chatBox.innerHTML += `<div class="message user-msg">${text}</div>`;
            inputField.value = "";
            chatBox.scrollTop = chatBox.scrollHeight;

            // Show Thinking state
            speechText.innerText = "⚡ सोचने और प्रोसेस करने में एक सेकंड...";
            neuralFace.style.boxShadow = "0 0 60px #eab308";

            try {
                const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=${apiKey}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: [{
                            parts: [{ text: "You are an elite, human-like virtual executive manager. Reply instantly, smartly, and conversationally in natural Hinglish/Hindi. User: " + text }]
                        }]
                    })
                });

                const data = await response.json();
                
                if(data.candidates && data.candidates[0].content.parts[0].text) {
                    const reply = data.candidates[0].content.parts[0].text;
                    chatBox.innerHTML += `<div class="message ai-msg">${reply}</div>`;
                    speechText.innerText = `"${reply.substring(0, 90)}..."`;
                    neuralFace.style.boxShadow = "0 0 50px rgba(56, 189, 248, 0.8)";
                } else {
                    chatBox.innerHTML += `<div class="message ai-msg">⚠️ API Error: अमान्य रिस्पॉन्स मिला। कृपया API Key जाँचें।</div>`;
                    speechText.innerText = "⚠️ कनेक्शन एरर!";
                }
            } catch (error) {
                chatBox.innerHTML += `<div class="message ai-msg">⚠️ Network Error: ${error.message}</div>`;
                speechText.innerText = "⚠️ नेटवर्क में समस्या है।";
            }
            
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

# Inject API Key safely without f-string bracket crashes
html_code = html_template.replace("__API_KEY_PLACEHOLDER__", api_key)

# Render in Streamlit using components.html
import streamlit.components.v1 as components

components.html(html_code, height=650, scrolling=True)
