async function sendMessage() {
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Add user message
    chatBox.innerHTML += `
        <div class="message user-message">
            ${message}
        </div>
    `;
    
    // Show typing indicator
    const typingIndicator = `
        <div class="message bot-message" id="typing-indicator">
            <em>Fetching data...</em>
        </div>
    `;
    chatBox.innerHTML += typingIndicator;
    
    try {
        const response = await fetch('http://localhost:5000/get_insight', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        // Remove typing indicator
        document.getElementById('typing-indicator').remove();
        
        const data = await response.json();
        chatBox.innerHTML += `
            <div class="message bot-message">
                ${data.response}
            </div>
        `;
    } catch (error) {
        document.getElementById('typing-indicator').remove();
        chatBox.innerHTML += `
            <div class="message bot-message negative">
                Error: Could not fetch stock data. Please try again.
            </div>
        `;
    }
    
    userInput.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Enter key handler
document.getElementById('user-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});