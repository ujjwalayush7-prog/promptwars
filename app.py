import streamlit as st
from google import genai
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure Gemini client
client = genai.Client(api_key=api_key)

# ============================================
# 🎨 PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="PromptWars AI Solution | Ujjwal Ayush",
    page_icon="🤖",
    layout="wide"
)

# ============================================
# 🎨 CUSTOM STYLING
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    .stApp {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
    }

    .main-header h1 {
        color: white !important;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .main-header p {
        color: rgba(255,255,255,0.85);
        font-size: 1.1rem;
    }

    .output-box {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1.5rem;
        color: #e0e0e0;
        font-size: 1rem;
        line-height: 1.7;
        margin-top: 1rem;
    }

    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }

    .sidebar-info {
        background: rgba(102, 126, 234, 0.1);
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# 🏠 HEADER
# ============================================
st.markdown("""
<div class="main-header">
    <h1>🤖 PromptWars AI Solution</h1>
    <p>Powered by Google Gemini 2.5 Pro | Built by Ujjwal Ayush for PromptWars 2026</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# 📝 MAIN APP LOGIC
# ============================================
# 👇 TODO: Customize this section based on the problem statement!

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    temperature = st.slider("Creativity Level", 0.0, 1.0, 0.7, 0.1,
                           help="Higher = more creative, Lower = more precise")
    st.markdown("---")
    st.markdown("""
    <div class="sidebar-info">
        <strong>💡 How to use:</strong><br>
        1. Enter your input below<br>
        2. Click the button<br>
        3. Get AI-powered results!
    </div>
    """, unsafe_allow_html=True)

# Main input area
st.markdown("### 📝 Enter Your Input")
user_input = st.text_area(
    "Type or paste your text here:",
    height=150,
    placeholder="Enter your text here..."
)

# System prompt - THIS IS WHERE THE MAGIC HAPPENS
# 👇 TODO: Change this prompt based on the problem statement!
SYSTEM_PROMPT = """You are a helpful AI assistant. 
Analyze the user's input carefully and provide a detailed, well-structured response.

Instructions:
- Be clear and concise
- Use bullet points where helpful
- Provide actionable insights
"""

if st.button("🚀 Generate Response", use_container_width=True):
    if user_input.strip():
        with st.spinner("✨ AI is thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-pro",
                    contents=SYSTEM_PROMPT + "\n\nUser Input:\n" + user_input,
                    config={
                        "temperature": temperature,
                    }
                )
                st.markdown("### 🎯 Result")
                st.markdown(f'<div class="output-box">{response.text}</div>',
                           unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Oops! Something went wrong: {str(e)}")
    else:
        st.warning("⚠️ Please enter some text first!")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>Built with ❤️ for PromptWars Hackathon</p>",
    unsafe_allow_html=True
)
