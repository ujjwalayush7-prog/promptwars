// ============================================
// 🎚️ TEMPERATURE SLIDER
// ============================================
const slider = document.getElementById('temperature-slider');
const tempValue = document.getElementById('temp-value');

slider.addEventListener('input', () => {
    const val = (slider.value / 100).toFixed(1);
    tempValue.textContent = val;
});

// ============================================
// 🚀 GENERATE RESPONSE
// ============================================
async function generateResponse() {
    const input = document.getElementById('user-input').value.trim();
    const temperature = slider.value / 100;
    const btn = document.getElementById('generate-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoader = btn.querySelector('.btn-loader');
    const outputSection = document.getElementById('output-section');
    const resultContent = document.getElementById('result-content');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    // Validate input
    if (!input) {
        errorMessage.style.display = 'block';
        errorText.textContent = 'Please enter some text first!';
        setTimeout(() => { errorMessage.style.display = 'none'; }, 3000);
        return;
    }

    // Show loading state
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    errorMessage.style.display = 'none';
    outputSection.style.display = 'none';

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                input: input,
                temperature: temperature
            })
        });

        const data = await response.json();

        if (data.success) {
            resultContent.textContent = data.result;
            outputSection.style.display = 'block';
            outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } else {
            throw new Error(data.error || 'Something went wrong');
        }
    } catch (error) {
        errorMessage.style.display = 'block';
        errorText.textContent = error.message;
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

// ============================================
// 📋 COPY RESULT
// ============================================
async function copyResult() {
    const resultContent = document.getElementById('result-content');
    const copyBtn = document.getElementById('copy-btn');

    try {
        await navigator.clipboard.writeText(resultContent.textContent);
        copyBtn.textContent = '✅ Copied!';
        setTimeout(() => { copyBtn.textContent = '📋 Copy'; }, 2000);
    } catch {
        copyBtn.textContent = '❌ Failed';
        setTimeout(() => { copyBtn.textContent = '📋 Copy'; }, 2000);
    }
}

// ============================================
// ⌨️ KEYBOARD SHORTCUT
// ============================================
document.getElementById('user-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        generateResponse();
    }
});
