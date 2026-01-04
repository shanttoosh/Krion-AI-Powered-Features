const API_URL = "http://localhost:8002/api/v1";

// DOM Elements
const commentInput = document.getElementById('review-comment');
const statusSelect = document.getElementById('review-status');
const suggestionsPopup = document.getElementById('ai-suggestions');
const suggestionsList = document.getElementById('suggestions-list');
const typingStatus = document.getElementById('typing-status');
const toneIndicator = document.getElementById('tone-indicator');

// Event Listeners
// removed handleTyping and updateToneIndicator

async function triggerRephrase() {
    const text = commentInput.value.trim();
    if (!text) {
        alert("Please enter a short comment first!");
        return;
    }

    // Determine mode for loading message
    const mode = text.length > 50 ? "improving paragraph" : "polishing comment";

    // Show loading state
    showSuggestions();
    suggestionsList.innerHTML = `
        <div class="loading-item">
            <div class="spinner-sm"></div> AI is ${mode}...
        </div>
    `;

    try {
        const response = await fetch(`${API_URL}/rephrase-comment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                input: text,
                status: statusSelect.value,
                num_suggestions: 3
            })
        });

        const data = await response.json();

        if (data.success) {
            renderSuggestions(data.suggestions);

            // Show correction info if any
            if (data.corrections.terms_expanded.length > 0) {
                const terms = data.corrections.terms_expanded.join(", ");
                typingStatus.textContent = `Expanded: ${terms}`;
            }
        } else {
            suggestionsList.innerHTML = `<div class="suggestion-item">Error: ${data.error || 'Failed to generate'}</div>`;
        }

    } catch (error) {
        console.error("API Error:", error);
        suggestionsList.innerHTML = `<div class="suggestion-item" style="color:red">Server error. Check if API is running on port 8002.</div>`;
    }
}

function renderSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) {
        suggestionsList.innerHTML = '<div class="suggestion-item">No suggestions found.</div>';
        return;
    }

    suggestionsList.innerHTML = suggestions.map(s => `
        <div class="suggestion-item" onclick="applySuggestion('${escapeHtml(s.text)}')">
            <div class="suggestion-header">
                <span class="suggestion-style style-${s.style.toLowerCase()}">${s.style}</span>
            </div>
            <div class="suggestion-text">${s.text}</div>
        </div>
    `).join('');
}

function applySuggestion(text) {
    commentInput.value = text;
    closeSuggestions();
    typingStatus.textContent = "AI suggestion applied ✨";

    // Highlight effect
    commentInput.style.backgroundColor = "#fffde7";
    setTimeout(() => {
        commentInput.style.backgroundColor = "white";
    }, 500);
}

function showSuggestions() {
    suggestionsPopup.classList.add('active');
}

function closeSuggestions() {
    suggestionsPopup.classList.remove('active');
}

function submitForm() {
    const status = statusSelect.value;
    const comment = commentInput.value;

    if (!comment) {
        alert("Please enter a comment.");
        return;
    }

    alert(`Review ${status.toUpperCase()} with comment:\n\n"${comment}"\n\n(This would send to backend in real app)`);
}

// Utility
function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
