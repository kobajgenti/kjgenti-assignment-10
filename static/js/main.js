// Form visibility management
function updateFormVisibility() {
    const queryType = document.getElementById('queryType').value;
    const imageSection = document.getElementById('imageQuerySection');
    const textSection = document.getElementById('textQuerySection');
    const hybridSection = document.getElementById('hybridWeightSection');
    
    // Reset all to hidden
    imageSection.style.display = 'none';
    textSection.style.display = 'none';
    hybridSection.style.display = 'none';
    
    // Show relevant sections based on query type
    switch(queryType) {
        case 'image':
            imageSection.style.display = 'block';
            break;
        case 'text':
            textSection.style.display = 'block';
            break;
        case 'hybrid':
            imageSection.style.display = 'block';
            textSection.style.display = 'block';
            hybridSection.style.display = 'block';
            break;
    }
}

// Initialize form visibility
document.getElementById('queryType').addEventListener('change', updateFormVisibility);
updateFormVisibility();

// File upload handling
document.getElementById('imageInput').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (file) {
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const data = await response.json();
                document.getElementById('selectedImage').textContent = data.filename;
            } else {
                console.error('Upload failed');
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
});

// Search functionality
document.getElementById('searchButton').addEventListener('click', async () => {
    const queryType = document.getElementById('queryType').value;
    const textQuery = document.getElementById('textInput').value;
    const selectedImage = document.getElementById('selectedImage').textContent;
    const lambda = document.getElementById('lambdaInput').value;
    
    // Validate input based on query type
    if (queryType === 'text' && !textQuery) {
        alert('Please enter a text query');
        return;
    }
    
    // Show loading indicator
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultsSection = document.getElementById('results');
    const searchButton = document.getElementById('searchButton');
    const errorElement = document.getElementById('searchError');
    
    loadingIndicator.style.display = 'block';
    resultsSection.classList.add('loading');
    searchButton.disabled = true;
    errorElement.style.display = 'none';

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                queryType,
                textQuery,
                imagePath: selectedImage,
                lambda
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            errorElement.textContent = data.error || 'An error occurred during search';
            errorElement.style.display = 'block';
        } else {
            displayResults(data);
        }
    } catch (error) {
        console.error('Error:', error);
        errorElement.textContent = 'An error occurred during search';
        errorElement.style.display = 'block';
    } finally {
        // Hide loading indicator
        loadingIndicator.style.display = 'none';
        resultsSection.classList.remove('loading');
        searchButton.disabled = false;
    }
});

function displayResults(results) {
    const resultsDiv = document.getElementById('resultImages');
    resultsDiv.innerHTML = '';
    
    results.forEach(result => {
        const div = document.createElement('div');
        div.className = 'result-item';
        
        const img = document.createElement('img');
        img.src = `/images/${result.image_path}`;
        img.loading = 'lazy'; // Add lazy loading for images
        
        const similarity = document.createElement('p');
        similarity.className = 'similarity';
        similarity.textContent = `Similarity: ${result.similarity.toFixed(3)}`;
        
        div.appendChild(img);
        div.appendChild(similarity);
        resultsDiv.appendChild(div);
    });
}