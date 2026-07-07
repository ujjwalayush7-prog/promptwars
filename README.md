# 🇮🇳 Smart Bharat – AI-Powered Civic Companion

> Built for the PromptWars Hackathon 2026 by Ujjwal Ayush

## 📌 Project Description

**Smart Bharat** is a multilingual, GenAI-powered web platform designed to help citizens across India access government services, report public issues, and receive personalized civic assistance. 

Navigating government bureaucracy can be overwhelming due to complex jargon, scattered information, and language barriers. Smart Bharat solves this by acting as an intelligent bridge between citizens and public services.

### ✨ Key Features:
1. **💬 Multilingual AI Assistant**: Chat in 12+ Indian languages (Hindi, Tamil, Bengali, etc.) to get instant answers about government services.
2. **🏛️ Smart Scheme Recommender**: Input your demographic details (age, income, occupation) and let the AI find government schemes you are eligible for.
3. **📢 Civic Issue Reporter**: Describe a civic issue (e.g., broken road, power cut) and the AI will categorize it, identify the responsible authority, generate a tracking ID, and guide you on where to formally file the complaint.
4. **📄 Document Requirement Checker**: Get comprehensive, accurate checklists of mandatory and supporting documents needed for any government application.

## 🚀 Live Demo

🔗 **[Live App (Vercel)](https://promptwars-delta.vercel.app/)**

## 🛠️ Tech Stack & Architecture

- **Frontend**: Custom HTML5, CSS3 (Glassmorphism design), Vanilla JS
- **Backend**: Python (Serverless Functions on Vercel)
- **AI Model**: Google Gemini 2.5 Pro 
- **Security**: Input sanitization, XSS prevention, Rate limiting via payload size

### 🎯 Judging Criteria Checklist:
- ✅ **Code Quality**: Modular architecture, Type hints, Comprehensive docstrings.
- ✅ **Security**: API keys secured in env, strict payload validation, HTML escaping.
- ✅ **Efficiency**: Serverless execution, minimal dependencies, lightning-fast DOM updates.
- ✅ **Testing**: 16 unit tests covering boundary conditions, type errors, and sanitization logic.
- ✅ **Accessibility (A11y)**: ARIA labels, semantic HTML, keyboard navigation support (Skip Nav, Focus rings).
- ✅ **Google Services**: Powered entirely by the Google Gemini API.

## 🧠 Prompt Workflow / Strategy

Smart Bharat uses a **Multi-Modal Contextual Prompting Strategy**. Instead of a single generic prompt, the frontend routes the user's intent to one of four specialized system prompts on the backend.

### 1. Contextual Routing
When a user interacts with a specific tab (Chat, Schemes, Complaints, Documents), the frontend tags the payload with a `mode`. The backend dynamically selects a heavily engineered system prompt optimized for that exact domain.

### 2. The Prompt Strategies

**A. Chat Mode Strategy:**
- **Role-playing**: Defines the AI as "Smart Bharat AI, a knowledgeable civic companion".
- **Boundaries**: Strictly scopes the AI to government services, schemes, and civic duties to prevent hallucination or off-topic responses.
- **Formatting**: Mandates step-by-step instructions and bullet points.

**B. Scheme Recommender Strategy:**
- **Zero-Shot Classification**: Analyzes demographic parameters (Age, Income, Occupation) injected into the prompt to filter the vast database of Indian schemes down to the Top 5 most relevant.
- **Structured Output Requirements**: Forces the AI to return data in a strict format: Name -> Description -> Benefits -> Eligibility -> How to Apply.

**C. Complaint Triage Strategy:**
- **Entity Extraction**: Analyzes unstructured citizen complaints to extract the "Issue Type" and "Location".
- **Institutional Mapping**: The prompt instructs the AI to identify the exact local authority responsible (e.g., "Jal Board" for water, "PWD" for roads).
- **Empathy Instruction**: Explicitly tells the AI to acknowledge frustration and be empathetic, improving user experience.

**D. Language Localization (Dynamic Injection)**
Every prompt is dynamically appended with:
`[LANGUAGE: Respond in {User_Selected_Language}. Language code: {lang_code}]`
This ensures the AI doesn't just translate, but generates native-feeling responses in local languages.

## 🏃 How to Run Locally

```bash
# Clone the repo
git clone https://github.com/ujjwalayush7-prog/promptwars.git
cd promptwars

# Set up your API key
# Create a .env file and add: GOOGLE_API_KEY=your_key_here

# Install test dependencies (optional)
pip install pytest
python -m pytest tests/test_api.py -v

# Note: To run the full app locally, use Vercel CLI (vercel dev)
```

## 👤 Developer
- **Ujjwal Ayush** ([@ujjwalayush7-prog](https://github.com/ujjwalayush7-prog))

## 📄 License
This project is open source.
