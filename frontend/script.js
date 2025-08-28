/**
 * Frontend JavaScript for AI Petition Search
 * Handles user interactions and API communication
 * 
 * Author: Junior Developer
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements - Get references to all the HTML elements we'll be working with
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const stateFilter = document.getElementById('stateFilter');
const minSignatures = document.getElementById('minSignatures');
const resultLimit = document.getElementById('resultLimit');
const loadingIndicator = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');
const resultsTitle = document.getElementById('resultsTitle');
const resultsCount = document.getElementById('resultsCount');
const statsSection = document.getElementById('statsSection');

// Example query buttons
const exampleButtons = document.querySelectorAll('.example-btn');

/**
 * Initialize the application when the page loads
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('AI Petition Search initialized');
    
    // Set up event listeners
    setupEventListeners();
    
    // Load statistics on page load
    loadStatistics();
    
    // Check API health
    checkAPIHealth();
});

/**
 * Set up all event listeners for user interactions
 */
function setupEventListeners() {
    // Search button click
    searchButton.addEventListener('click', performSearch);
    
    // Enter key in search input
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    // Example query buttons
    exampleButtons.forEach(button => {
        button.addEventListener('click', () => {
            searchInput.value = button.getAttribute('data-query');
            performSearch();
        });
    });
    
    // Filter changes trigger new search if there's a query
    stateFilter.addEventListener('change', () => {
        if (searchInput.value.trim()) {
            performSearch();
        }
    });
    
    minSignatures.addEventListener('change', () => {
        if (searchInput.value.trim()) {
            performSearch();
        }
    });
}

/**
 * Check if the API is healthy and running
 */
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            console.log('✅ API is healthy and ready');
        } else {
            console.warn('⚠️ API health check returned:', data);
            showError('The search service may be experiencing issues. Please try again later.');
        }
    } catch (error) {
        console.error('❌ Failed to check API health:', error);
        showError('Cannot connect to the search service. Please ensure the backend is running.');
    }
}

/**
 * Load and display statistics about the petition dataset
 */
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const stats = await response.json();
        
        // Update statistics display
        document.getElementById('totalPetitions').textContent = stats.total_petitions.toLocaleString();
        document.getElementById('openPetitions').textContent = stats.open_petitions.toLocaleString();
        document.getElementById('avgSignatures').textContent = Math.round(stats.average_signatures).toLocaleString();
        document.getElementById('totalSignatures').textContent = stats.total_signatures.toLocaleString();
        
        // Show the statistics section
        statsSection.classList.remove('hidden');
        
    } catch (error) {
        console.error('Failed to load statistics:', error);
        // Don't show error to user, just hide stats section
        statsSection.classList.add('hidden');
    }
}

/**
 * Perform the search when user clicks search button
 */
async function performSearch() {
    // Get the search query
    const query = searchInput.value.trim();
    
    // Validate query
    if (!query) {
        showError('Please enter a search query');
        return;
    }
    
    if (query.length > 500) {
        showError('Query is too long (maximum 500 characters)');
        return;
    }
    
    // Clear previous results and errors
    hideError();
    resultsContainer.innerHTML = '';
    resultsSection.classList.add('hidden');
    
    // Show loading indicator
    showLoading();
    
    // Build the request body
    const requestBody = {
        query: query,
        limit: parseInt(resultLimit.value) || 10,
        filters: {}
    };
    
    // Add filters if set
    if (stateFilter.value) {
        requestBody.filters.state = stateFilter.value;
    }
    
    if (minSignatures.value) {
        requestBody.filters.min_signatures = parseInt(minSignatures.value);
    }
    
    try {
        // Make API request
        console.log('Searching for:', query);
        const response = await fetch(`${API_BASE_URL}/api/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        // Check if response is ok
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Search failed');
        }
        
        // Parse response
        const data = await response.json();
        
        // Hide loading indicator
        hideLoading();
        
        // Display results
        displayResults(data);
        
    } catch (error) {
        console.error('Search error:', error);
        hideLoading();
        showError(`Search failed: ${error.message}`);
    }
}

/**
 * Display search results on the page
 */
function displayResults(data) {
    // Update results header
    resultsTitle.textContent = `Search Results for "${data.query}"`;
    resultsCount.textContent = `Found ${data.count} relevant petition${data.count !== 1 ? 's' : ''}`;
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    if (data.count === 0) {
        // No results found
        resultsContainer.innerHTML = `
            <div class="no-results">
                <p>No petitions found matching your search.</p>
                <p>Try different keywords or adjust your filters.</p>
            </div>
        `;
    } else {
        // Display each result
        data.results.forEach(petition => {
            const card = createPetitionCard(petition);
            resultsContainer.appendChild(card);
        });
    }
    
    // Show results section
    resultsSection.classList.remove('hidden');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Create a petition card element
 */
function createPetitionCard(petition) {
    const card = document.createElement('div');
    card.className = 'petition-card';
    
    // Format similarity score as percentage
    const similarityPercent = petition.similarity_score 
        ? Math.round(petition.similarity_score * 100) 
        : 0;
    
    // Format signatures count with commas
    const formattedSignatures = petition.signatures.toLocaleString();
    
    // Create the card HTML
    card.innerHTML = `
        <div class="petition-header">
            <h3 class="petition-title">${escapeHtml(petition.title)}</h3>
            ${petition.similarity_score ? `
                <span class="similarity-score" title="How closely this matches your search">
                    ${similarityPercent}% match
                </span>
            ` : ''}
        </div>
        
        <div class="petition-meta">
            <div class="meta-item">
                <span class="meta-label">Status:</span>
                <span class="status-badge status-${petition.state}">
                    ${petition.state}
                </span>
            </div>
            <div class="meta-item">
                <span class="meta-label">Signatures:</span>
                <span class="meta-value">${formattedSignatures}</span>
            </div>
            ${petition.rank ? `
                <div class="meta-item">
                    <span class="meta-label">Rank:</span>
                    <span class="meta-value">#${petition.rank}</span>
                </div>
            ` : ''}
        </div>
        
        <a href="${petition.url}" target="_blank" class="petition-link">
            View on Parliament Website →
        </a>
    `;
    
    return card;
}

/**
 * Show loading indicator
 */
function showLoading() {
    loadingIndicator.classList.remove('hidden');
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    loadingIndicator.classList.add('hidden');
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    
    // Auto-hide error after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.classList.add('hidden');
    errorMessage.textContent = '';
}

/**
 * Escape HTML to prevent XSS attacks
 * This is a security best practice when displaying user content
 */
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

/**
 * Debounce function to limit how often a function can run
 * Useful for search-as-you-type features (not implemented but good to have)
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Log when the script is loaded successfully
console.log('AI Petition Search frontend loaded successfully');
