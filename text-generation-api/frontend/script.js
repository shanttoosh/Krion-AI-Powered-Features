// Krion Consulting - Text Generation Frontend

const API_URL = 'http://127.0.0.1:8000/api/v1';

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        // Update active nav
        document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
        item.classList.add('active');

        // Update section
        const section = item.dataset.section;
        document.querySelectorAll('.form-section').forEach(s => s.classList.remove('active'));
        document.getElementById(`${section}-section`).classList.add('active');

        // Update title
        const titles = {
            'review': 'Create Review',
            'rfa': 'Create Request for Approval'
        };
        document.getElementById('page-title').textContent = titles[section];
    });
});

// Generate Description
async function generateDescription(entityType) {
    const loadingOverlay = document.getElementById('loading-overlay');
    loadingOverlay.classList.add('active');

    try {
        let fields = {};
        let generationMode = '';

        if (entityType === 'review') {
            fields = {
                name: document.getElementById('review-name').value,
                start_date: document.getElementById('review-start-date').value,
                due_date: document.getElementById('review-due-date').value,
                workflow: document.getElementById('review-workflow').value,
                priority: document.getElementById('review-priority').value
            };

            // Optional fields
            const parentReview = document.getElementById('review-parent').value;
            if (parentReview) fields.parent_review = parentReview;

            const estimatedCost = document.getElementById('review-estimated-cost').value;
            if (estimatedCost) fields.estimated_cost = parseInt(estimatedCost);

            const actualCost = document.getElementById('review-actual-cost').value;
            if (actualCost) fields.actual_cost = parseInt(actualCost);

            const checklist = document.getElementById('review-checklist').value;
            if (checklist) fields.checklist = checklist.split(',').map(item => item.trim()).filter(item => item);

            generationMode = document.getElementById('review-generation-mode').value;

        } else if (entityType === 'rfa') {
            fields = {
                name: document.getElementById('rfa-name').value,
                request_date: document.getElementById('rfa-request-date').value,
                due_date: document.getElementById('rfa-due-date').value,
                workflow: document.getElementById('rfa-workflow').value,
                priority: document.getElementById('rfa-priority').value
            };

            const checklist = document.getElementById('rfa-checklist').value;
            if (checklist) fields.checklist = checklist.split(',').map(item => item.trim()).filter(item => item);

            generationMode = document.getElementById('rfa-generation-mode').value;
        }

        const requestBody = {
            entity_type: entityType,
            generation_mode: generationMode,
            fields: fields
        };

        console.log('Sending request:', requestBody);

        const response = await fetch(`${API_URL}/generate-description`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();
        console.log('Response:', data);

        if (data.success) {
            const textarea = document.getElementById(`${entityType}-description`);
            textarea.value = data.generated_description;

            // Add animation
            textarea.style.background = 'rgba(16, 185, 129, 0.1)';
            setTimeout(() => {
                textarea.style.background = '';
            }, 1000);
        } else {
            alert('Failed to generate description: ' + (data.error || 'Unknown error'));
        }

    } catch (error) {
        console.error('Error:', error);
        alert('Failed to connect to API. Make sure the server is running on http://127.0.0.1:8000');
    } finally {
        loadingOverlay.classList.remove('active');
    }
}

// Initialize with today's date
function initDates() {
    const today = new Date().toISOString().split('T')[0];
    const futureDate = new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];

    // Don't override default values if they exist
}

document.addEventListener('DOMContentLoaded', initDates);
