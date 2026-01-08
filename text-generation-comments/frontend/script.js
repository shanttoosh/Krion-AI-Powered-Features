const API_URL = "http://localhost:8002/api/v1";

// --- State ---
let currentProjectId = null;
let currentReviewId = null;
let currentWorkflowId = null;
let threadHistory = [];
let replyingToComment = null;

// --- DOM Elements ---
const views = {
    projectList: document.getElementById('view-project-list'),
    reviewExecution: document.getElementById('view-review-execution')
};
const sidebars = {
    global: document.querySelector('.sidebar-global'),
    project: document.getElementById('sidebar-project')
};
const breadcrumb = document.getElementById('breadcrumb-text');
const projectTableBody = document.getElementById('project-list-body');
const reviewTitle = document.getElementById('review-title');
const reviewDesc = document.getElementById('review-desc');
const reviewStepper = document.getElementById('review-stepper');
const commentsContainer = document.getElementById('comments-container');
const replyContext = document.getElementById('replying-to');
const replyText = document.getElementById('reply-to-text');
const commentInput = document.getElementById('comment-text');
const userNameInput = document.getElementById('user-name');
const suggestionPopup = document.getElementById('suggestion-popup');
const suggestionList = document.getElementById('suggestion-list');
const toast = document.getElementById('toast');

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    loadProjects();
});

// --- Routing / View Switching ---
function switchView(viewName) {
    // Hide all views
    Object.values(views).forEach(el => el.classList.add('hidden'));

    if (viewName === 'project-list') {
        views.projectList.classList.remove('hidden');
        sidebars.project.classList.add('hidden');
        breadcrumb.textContent = "Home / Projects";
    }
    else if (viewName === 'review-execution') {
        views.reviewExecution.classList.remove('hidden');
        sidebars.project.classList.remove('hidden'); // Ensure project sidebar is visible
        breadcrumb.textContent = "Home / Project / Reviews / Execution";
    }
}

function exitReview() {
    // For now, go back to project list since we don't have a review list yet
    currentReviewId = null;
    switchView('project-list');
}

// --- Project Logic ---
async function loadProjects() {
    try {
        const res = await fetch(`${API_URL}/projects`);
        const projects = await res.json();
        renderProjectList(projects);
    } catch (err) {
        console.error("Failed to load projects", err);
        projectTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:red">Failed to load projects. Is API running?</td></tr>`;
    }
}

function renderProjectList(projects) {
    projectTableBody.innerHTML = projects.map(p => `
        <tr onclick="enterProject(${p.id}, '${p.code}', '${p.name}')">
            <td><strong>${p.code}</strong></td>
            <td>${p.name}</td>
            <td><span class="status-badge status-${p.status.toLowerCase().replace(' ', '')}">${p.status}</span></td>
            <td>${p.location || '-'}</td>
            <td>${p.owner || '-'}</td>
            <td><button class="btn-secondary" style="padding:4px 10px; font-size:11px">Open</button></td>
        </tr>
    `).join('');
}

async function enterProject(id, code, name) {
    currentProjectId = id;

    // Update Sidebar Info
    document.querySelector('.project-code').textContent = code;
    document.querySelector('.project-name').textContent = name;

    // Show Sidebar
    sidebars.project.classList.remove('hidden');

    // For demo purposes, auto-load the first review if available, or just stay on list
    // Let's assume user wants to go to Reviews immediately for this task
    alert(`Entering Project: ${name}\nOnly "Review Execution" is fully implemented in this demo.`);

    // Fetch reviews for this project (Hardcoded to ID 1 for demo since specific endpoint not built yet)
    // In real app: fetch /api/v1/projects/${id}/reviews
    if (id === 1) {
        enterReview(1); // Skyline Tower has review ID 1
    } else {
        alert("No reviews found for this project in seed data.");
        switchView('project-list');
    }
}

// --- Review Logic ---
async function enterReview(reviewId) {
    currentReviewId = reviewId;
    switchView('review-execution');

    // 1. Fetch Details
    try {
        const res = await fetch(`${API_URL}/reviews/${reviewId}`);
        if (!res.ok) throw new Error("Review not found");
        const review = await res.json();

        // Render Details
        reviewTitle.innerHTML = `${review.name} <span class="sub-text" style="font-weight:400; font-size:14px; margin-left:10px">${review.code}</span>`;
        reviewDesc.textContent = review.description || "No description provided.";

        // Update Stepper (Mock for now, waiting on Workflow API enrichment)
        // We know it's a 3-step workflow from seed data
        renderStepper(review.current_step);

        // 2. Load Comments
        loadComments();

    } catch (err) {
        console.error(err);
        views.reviewExecution.innerHTML = `<div style="padding:20px; color:red">Error loading review: ${err.message}</div>`;
    }
}

function renderStepper(currentStep) {
    // Hardcoded steps based on "3-Step Structural Approval" seed
    const steps = ["Initial Review", "Technical Check", "Final Sign-off"];

    reviewStepper.innerHTML = steps.map((s, idx) => {
        const stepNum = idx + 1;
        let status = '';
        if (stepNum < currentStep) status = 'completed';
        else if (stepNum === currentStep) status = 'active';

        return `
            <div class="step-item ${status}">
                <div class="step-circle">${stepNum}</div>
                <div class="step-label" style="font-size:11px">${s}</div>
                ${idx < steps.length - 1 ? '<div class="step-line"></div>' : ''}
            </div>
        `;
    }).join('');
}

// --- Comment System (Ported & Adapted) ---
async function loadComments() {
    if (!currentReviewId) return;

    commentsContainer.innerHTML = '<div style="text-align:center; padding:20px; color:#999"><i class="fas fa-circle-notch fa-spin"></i> Loading context...</div>';

    try {
        const res = await fetch(`${API_URL}/review-comments/list/${currentReviewId}`);
        const data = await res.json();
        if (data.success) {
            renderComments(data.comments);
        } else {
            commentsContainer.innerHTML = '<div style="text-align:center; padding:20px">No comments yet.</div>';
        }
    } catch (err) {
        commentsContainer.innerHTML = '<div style="text-align:center; color:red">Failed to load comments</div>';
    }
}

function renderComments(comments) {
    if (!comments || comments.length === 0) {
        commentsContainer.innerHTML = '<div style="text-align:center; padding:20px; color:#bbb">Start the conversation...</div>';
        return;
    }
    commentsContainer.innerHTML = comments.map(c => renderCommentNode(c, 0)).join('');
}

function renderCommentNode(c, level) {
    const isReply = level > 0;
    const indent = level * 20;
    const time = new Date(c.created_at).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

    let html = `
        <div class="comment-node ${isReply ? 'depth-' + level : ''}" style="margin-left:${indent}px">
            <div class="comment-card">
                <div class="c-header">
                    <span class="user-badge">${escapeHtml(c.user_name)}</span>
                    <span class="time-badge">${time}</span>
                </div>
                <div class="c-body">${escapeHtml(c.text)}</div>
                <div class="c-actions">
                    <span class="step-badge">Step ${c.workflow_step}</span>
                    <button class="btn-reply" onclick="replyTo(${c.id}, '${escapeHtml(c.user_name)}')"><i class="fas fa-reply"></i> Reply</button>
                </div>
            </div>
        </div>
    `;

    if (c.replies && c.replies.length > 0) {
        html += c.replies.map(r => renderCommentNode(r, level + 1)).join('');
    }
    return html;
}

function replyTo(id, user) {
    replyingToComment = id;
    replyContext.classList.remove('hidden');
    replyText.textContent = `Replying to @${user}`;
    commentInput.focus();

    // Fetch context for AI
    fetch(`${API_URL}/review-comments/thread/${id}`)
        .then(r => r.json())
        .then(data => { if (data.success) threadHistory = data.thread; });
}

function clearReply() {
    replyingToComment = null;
    threadHistory = [];
    replyContext.classList.add('hidden');
}

async function submitComment() {
    const text = commentInput.value.trim();
    if (!text) return showToast("Please enter a comment");

    const payload = {
        review_id: currentReviewId,
        workflow_step: 2, // Hardcoded to current step for now
        user_name: userNameInput.value || "Reviewer",
        status: "Comment",
        text: text,
        parent_id: replyingToComment
    };

    try {
        const res = await fetch(`${API_URL}/review-comments/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (data.success) {
            commentInput.value = '';
            clearReply();
            loadComments();
            showToast("Comment posted successfully");
        } else {
            showToast("Error posting comment");
        }
    } catch (err) {
        showToast("Server error");
    }
}

// --- AI Rephraser ---
async function triggerRephrase() {
    const text = commentInput.value.trim();
    if (!text) return showToast("Type something first!");

    suggestionPopup.classList.remove('hidden');
    suggestionList.innerHTML = '<div style="padding:10px; color:#666"><i class="fas fa-spinner fa-spin"></i> Thinking...</div>';

    try {
        const res = await fetch(`${API_URL}/rephrase-comment`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                input: text,
                status: "Comment",
                thread_history: threadHistory,
                parent_comment_id: replyingToComment
            })
        });
        const data = await res.json();

        if (data.success) {
            suggestionList.innerHTML = data.suggestions.map(s => `
                <div class="suggestion-item" onclick="applySuggestion('${escapeHtml(s.text)}')">
                    <div style="font-weight:600; font-size:11px; color:#008060; margin-bottom:2px">${s.style}</div>
                    <div>${s.text}</div>
                </div>
            `).join('');
        }
    } catch (err) {
        suggestionList.innerHTML = '<div style="color:red; padding:10px">AI Service Unavailable</div>';
    }
}

function applySuggestion(text) {
    commentInput.value = text; // In real app, unescape HTML
    closeSuggestions();
    showToast("Suggestion applied");
}

function closeSuggestions() {
    suggestionPopup.classList.add('hidden');
}

// --- Utils ---
function showToast(msg) {
    toast.textContent = msg;
    toast.classList.remove('hidden');
    setTimeout(() => toast.classList.add('hidden'), 3000);
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
