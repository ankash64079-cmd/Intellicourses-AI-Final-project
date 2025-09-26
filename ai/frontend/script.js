document.addEventListener('DOMContentLoaded', () => {
    // 1. Get DOM elements
    const queryInput = document.getElementById('query-input');
    const submitButton = document.getElementById('submit-button');
    const responseOutput = document.getElementById('response-output');
    const loadingIndicator = document.getElementById('loading-indicator');
    const errorMessage = document.getElementById('error-message');
    
    // Set the API endpoint URL (FastAPI runs on port 8000 by default)
    const API_URL = 'http://127.0.0.1:8000/api/query';

    // 2. Event Listener
    submitButton.addEventListener('click', handleSubmit);
    queryInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault(); // Prevents a new line in the textarea
            handleSubmit();
        }
    });

    // 3. Main Handler Function
    async function handleSubmit() {
        const query = queryInput.value.trim();

        if (query === "") {
            alert("Please enter a question about the course catalog.");
            return;
        }

        // Clear previous state and update UI for loading
        errorMessage.style.display = 'none';
        responseOutput.innerHTML = '';
        loadingIndicator.style.display = 'block';
        submitButton.disabled = true;

        try {
            // Send POST request to the FastAPI endpoint
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_query: query })
            });

            // Check if the API call was successful
            if (!response.ok) {
                // Read the error message from the API response
                const errorData = await response.json();
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }

            // Parse the JSON response
            const data = await response.json();
            
            // Update the output box with the AI's answer
            responseOutput.textContent = data.answer;
            
        } catch (error) {
            // Handle network errors or API errors
            console.error('Fetch error:', error);
            errorMessage.textContent = `Error: Could not connect to the API or an internal error occurred. (Details: ${error.message}). Please ensure your Python FastAPI server is running.`;
            errorMessage.style.display = 'block';
            
            // Put a placeholder back if the request failed before getting data
            if (responseOutput.textContent === '') {
                responseOutput.innerHTML = '<p class="placeholder-text">Failed to retrieve response.</p>';
            }
            
        } finally {
            // Reset UI state
            loadingIndicator.style.display = 'none';
            submitButton.disabled = false;
        }
    }
});