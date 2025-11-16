const API_URL = 'http://127.0.0.1:5000/ask';

const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');

let isLoading = false;

function initializeChat() {
    sendButton.addEventListener('click', handleSendMessage);

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    userInput.addEventListener('input', autoResize);
}

function autoResize() {
    userInput.style.height = 'auto';
    userInput.style.height = userInput.scrollHeight + 'px';
}

function handleSendMessage() {
    const message = userInput.value.trim();

    if (!message || isLoading) {
        return;
    }

    removeWelcomeMessage();

    addUserMessage(message);

    userInput.value = '';
    userInput.style.height = 'auto';

    sendMessageToAPI(message);
}

function removeWelcomeMessage() {
    const welcomeMessage = document.querySelector('.welcome-message');
    if (welcomeMessage) {
        welcomeMessage.remove();
    }
}

function addUserMessage(message) {
    const messageGroup = document.createElement('div');
    messageGroup.className = 'message-group user';

    messageGroup.innerHTML = `
        <div class="message-avatar">You</div>
        <div class="message-content">
            <div class="message-bubble">${escapeHtml(message)}</div>
        </div>
    `;

    chatMessages.appendChild(messageGroup);
    scrollToBottom();
}

function addBotMessage(answer, documents = null) {
    const messageGroup = document.createElement('div');
    messageGroup.className = 'message-group bot';

    let documentsHtml = '';
    if (documents && documents.length > 0) {
        documentsHtml = `
            <div class="documents-section">
                <div class="documents-header" onclick="toggleDocuments(this)">
                    <h3>📄 Referenced Documents (${documents.length})</h3>
                    <span class="documents-toggle">Show</span>
                </div>
                <div class="documents-list">
                    ${documents.map(doc => `
                        <div class="document-item">
                            <strong>Problem:</strong> ${escapeHtml(doc.problem || 'N/A')}
                            <div><strong>Clause:</strong> ${escapeHtml(doc.clause || 'N/A')}</div>
                            <div><strong>Relevance:</strong> ${Math.round((doc.score || 0) * 100)}%</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    messageGroup.innerHTML = `
        <div class="message-avatar">AI</div>
        <div class="message-content">
            <div class="message-bubble">${escapeHtml(answer).replace(/\n/g, "<br>")}</div>
            ${documentsHtml}
        </div>
    `;

    chatMessages.appendChild(messageGroup);
    scrollToBottom();
}

function addTypingIndicator() {
    const messageGroup = document.createElement('div');
    messageGroup.className = 'message-group bot typing-indicator-group';
    messageGroup.id = 'typingIndicator';

    messageGroup.innerHTML = `
        <div class="message-avatar">AI</div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;

    chatMessages.appendChild(messageGroup);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

async function sendMessageToAPI(message) {
    isLoading = true;
    sendButton.disabled = true;

    addTypingIndicator();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: message }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        removeTypingIndicator();

        addBotMessage(data.answer || 'No response received.', data.documents);

    } catch (error) {
        console.error('Error:', error);

        removeTypingIndicator();

        addBotMessage(
            'Sorry, I encountered an error connecting to the backend. Please make sure the API server is running at http://127.0.0.1:5000'
        );
    } finally {
        isLoading = false;
        sendButton.disabled = false;
        userInput.focus();
    }
}

function toggleDocuments(header) {
    const documentsList = header.parentElement.querySelector(".documents-list");
    const toggle = header.querySelector('.documents-toggle');

    if (documentsList.classList.contains('expanded')) {
        documentsList.classList.remove('expanded');
        toggle.textContent = 'Show';
    } else {
        documentsList.classList.add('expanded');
        toggle.textContent = 'Hide';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

initializeChat();
userInput.focus();
