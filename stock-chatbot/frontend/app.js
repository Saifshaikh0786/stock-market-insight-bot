async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const message = userInput.value.trim();
    
    if (!message) return;

    // Hide intro section on first message
    if(document.querySelector('.intro-section')) {
        document.querySelector('.intro-section').remove();
        chatBox.style.display = 'block';
    }
    
    // Add user message
    chatBox.innerHTML += `
        <div class="message user-message">
            ${message}
        </div>
    `;
    
    // Show typing indicator
    const typingIndicator = `
        <div class="message bot-message" id="typing-indicator">
            <em>Analyzing market data...</em>
            <div class="typing-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `;
    chatBox.innerHTML += typingIndicator;
    
    try {
        const response = await fetch('http://localhost:5000/get_insight', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        document.getElementById('typing-indicator').remove();
        
        const data = await response.json();
        chatBox.innerHTML += `
            <div class="message bot-message">
                ${data.response}
                ${data.chart ? `<div class="chart-container">${data.chart}</div>` : ''}
            </div>
        `;
    } catch (error) {
        document.getElementById('typing-indicator').remove();
        chatBox.innerHTML += `
            <div class="message bot-message negative">
                ⚠️ Market data unavailable. Please try again later.
            </div>
        `;
    }
    
    userInput.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Set query from trending topics
function setQuery(topic) {
    const input = document.getElementById('user-input');
    input.value = topic;
    sendMessage();
}

// Enter key handler
document.getElementById('user-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});