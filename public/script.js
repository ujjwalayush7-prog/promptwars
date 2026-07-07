// ============================================
// 📑 TAB MANAGEMENT
// ============================================
function switchTab(tabId) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(t => {
        t.classList.remove('active');
        t.setAttribute('aria-selected', 'false');
    });
    const activeTab = document.getElementById(`tab-${tabId}`);
    activeTab.classList.add('active');
    activeTab.setAttribute('aria-selected', 'true');

    // Update panels
    document.querySelectorAll('.panel').forEach(p => p.style.display = 'none');
    document.getElementById(`panel-${tabId}`).style.display = 'block';
}

// ============================================
// 💬 CHAT ASSISTANT
// ============================================
const chatArea = document.getElementById('chat-area');
const chatInput = document.getElementById('chat-input');
let isTyping = false;

function addMessage(content, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-message ${isUser ? 'user' : 'bot'}`;
    
    // Convert markdown to HTML for bot messages
    let htmlContent = content;
    if (!isUser) {
        try {
            htmlContent = marked.parse(content);
        } catch (e) {
            htmlContent = `<p>${content}</p>`;
        }
    } else {
        htmlContent = `<p>${content}</p>`;
    }

    msgDiv.innerHTML = `
        <div class="msg-avatar" aria-hidden="true">${isUser ? '👤' : '🤖'}</div>
        <div class="msg-content">${htmlContent}</div>
    `;
    
    chatArea.appendChild(msgDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function quickAction(text) {
    chatInput.value = text;
    chatInput.focus();
}

async function sendChat() {
    const text = chatInput.value.trim();
    if (!text || isTyping) return;

    // Add user message
    addMessage(text, true);
    chatInput.value = '';
    isTyping = true;
    
    const sendBtn = document.getElementById('chat-send-btn');
    sendBtn.disabled = true;
    sendBtn.innerHTML = '<span class="spinner"></span>';

    try {
        const lang = document.getElementById('language-select').value;
        const res = await callApi(text, 'chat', lang);
        addMessage(res);
    } catch (err) {
        addMessage("❌ Sorry, I encountered an error connecting to the server. Please try again.");
    } finally {
        isTyping = false;
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<span class="send-icon">➤</span>';
        chatInput.focus();
    }
}

// Allow Enter to send, Shift+Enter for newline
chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChat();
    }
});

// ============================================
// 🏛️ SERVICES FINDER
// ============================================
async function findSchemes(e) {
    e.preventDefault();
    
    const age = document.getElementById('svc-age').value;
    const gender = document.getElementById('svc-gender').value;
    const income = document.getElementById('svc-income').value;
    const state = document.getElementById('svc-state').value;
    const category = document.getElementById('svc-category').value;
    const occupation = document.getElementById('svc-occupation').value;
    
    const prompt = `Find schemes for: Age ${age}, Gender ${gender}, Income ₹${income}, State ${state}, Category ${category}, Occupation ${occupation}`;
    
    await handleFormSubmit('scheme-btn', 'services-result', prompt, 'services');
}

// ============================================
// 📢 COMPLAINT REPORTER
// ============================================
let complaints = JSON.parse(localStorage.getItem('smart_bharat_complaints') || '[]');

function renderComplaints() {
    const list = document.getElementById('complaint-list');
    if (complaints.length === 0) {
        list.innerHTML = '<p style="color:var(--text-secondary);font-size:0.9rem;">No complaints filed yet.</p>';
        return;
    }
    
    list.innerHTML = complaints.reverse().map(c => `
        <div class="complaint-card">
            <div class="cmp-meta">
                <span class="cmp-id">${c.id}</span>
                <span class="cmp-date">${c.date}</span>
            </div>
            <div class="cmp-title"><strong>${c.type}</strong> at ${c.location}</div>
            <div style="margin-top:0.5rem;"><span class="cmp-status">Filed successfully</span></div>
        </div>
    `).join('');
}

// Initial render
renderComplaints();

async function fileComplaint(e) {
    e.preventDefault();
    
    const type = document.getElementById('cmp-type').value;
    const loc = document.getElementById('cmp-location').value;
    const desc = document.getElementById('cmp-description').value;
    
    const prompt = `Issue Type: ${type}\nLocation: ${loc}\nDetails: ${desc}`;
    
    const result = await handleFormSubmit('complaint-btn', 'complaint-result', prompt, 'complaint');
    
    if (result && result.complaint_id) {
        // Save to local storage
        complaints.push({
            id: result.complaint_id,
            type: type,
            location: loc,
            date: new Date().toLocaleDateString()
        });
        localStorage.setItem('smart_bharat_complaints', JSON.stringify(complaints));
        renderComplaints();
        
        // Reset form
        document.getElementById('complaint-form').reset();
    }
}

// ============================================
// 📄 DOCUMENT CHECKER
// ============================================
async function checkDocuments(e) {
    e.preventDefault();
    const service = document.getElementById('doc-service').value;
    if (!service) return;
    
    const prompt = `What are the exact document requirements to apply for: ${service}`;
    await handleFormSubmit('docs-btn', 'docs-result', prompt, 'documents');
}

// ============================================
// 🌐 API CALLER UTILITY
// ============================================
async function handleFormSubmit(btnId, resultId, prompt, mode) {
    const btn = document.getElementById(btnId);
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    const resultArea = document.getElementById(resultId);
    const lang = document.getElementById('language-select').value;
    
    // Show loading
    if(btn) btn.disabled = true;
    if(btnText) btnText.style.display = 'none';
    if(btnLoader) btnLoader.style.display = 'inline';
    if(resultArea) resultArea.style.display = 'none';
    
    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ input: prompt, mode: mode, language: lang, temperature: 0.7 })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Server error');
        }
        
        const textRes = data.result;
        
        // Format markdown to HTML
        let htmlContent = textRes;
        if (typeof marked !== 'undefined') {
            htmlContent = marked.parse(textRes);
        }
            
        if(resultArea) {
            resultArea.innerHTML = htmlContent;
            
            if (mode === 'complaint' && data.complaint_id) {
                resultArea.innerHTML += `<div style="margin-top:1rem;padding:0.75rem;background:rgba(16, 185, 129, 0.1);border:1px solid #10b981;border-radius:8px;color:#10b981;"><strong>✅ Complaint Registered</strong><br>Your Tracking ID is: <code>${data.complaint_id}</code></div>`;
            }
            
            resultArea.style.display = 'block';
            resultArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        
        return data;
        
    } catch (err) {
        console.error(err);
        if(resultArea) {
            resultArea.innerHTML = `<div style="color:#ef4444;padding:1rem;background:rgba(239,68,68,0.1);border-radius:8px;">❌ Error: ${err.message}</div>`;
            resultArea.style.display = 'block';
        }
        return null;
    } finally {
        if(btn) btn.disabled = false;
        if(btnText) btnText.style.display = 'inline';
        if(btnLoader) btnLoader.style.display = 'none';
    }
}

async function callApi(input, mode, language) {
    const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            input: input,
            mode: mode,
            language: language,
            temperature: 0.7
        })
    });
    
    const data = await response.json();
    
    if (data.success) {
        return data.result;
    } else {
        throw new Error(data.error || 'Server error');
    }
}
