// Update decoded text periodically
document.addEventListener('DOMContentLoaded', function() {
    // Update the decoded text every second
    setInterval(updateDecodedText, 1000);
    
    // Check camera status
    checkCameraStatus();

    // Add click handler for predicted word if element exists
    var predictedWordElement = document.getElementById('predicted-word');
    if (predictedWordElement) {
        predictedWordElement.addEventListener('click', handlePredictedWordClick);
    }
});

function updateDecodedText() {
    var decodedTextElement = document.getElementById('decoded-text');
    if (!decodedTextElement) {
        console.error('Decoded text element not found');
        return;
    }
    
    fetch('/get_decoded_text')
        .then(function(response) {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.text();
        })
        .then(function(text) {
            decodedTextElement.textContent = text;
            updateSuggestions(text);
            updatePredictedWord(text);
        })
        .catch(function(error) {
            console.error('Error updating decoded text:', error);
        });
}

function checkCameraStatus() {
    fetch('/camera_status')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            var statusElement = document.getElementById('camera-status');
            if (statusElement) {
                statusElement.className = data.active ? 
                    'status-indicator status-active' : 
                    'status-indicator status-inactive';
                
                var statusTextElement = document.getElementById('camera-status-text');
                if (statusTextElement) {
                    statusTextElement.textContent = data.active ? 'Active' : 'Inactive';
                }
            }
        })
        .catch(function(error) {
            console.error('Error checking camera status:', error);
        });
        
    setTimeout(checkCameraStatus, 5000);
}

function resetDecodedText() {
    if (confirm('Are you sure you want to clear the decoded text?')) {
        fetch('/reset_text', { method: 'POST' })
            .then(function(response) {
                return response.json();
            })
            .then(function(data) {
                if (data.success) {
                    var textElement = document.getElementById('decoded-text');
                    if (textElement) {
                        textElement.textContent = '';
                        updatePredictedWord('');
                        updateSuggestions('');
                    }
                }
            })
            .catch(function(error) {
                console.error('Error resetting text:', error);
            });
    }
}

function updatePredictedWord(text) {
    var predictedWordElement = document.getElementById('predicted-word');
    if (!predictedWordElement) return;

    if (!text || text.trim() === '') {
        predictedWordElement.textContent = '';
        predictedWordElement.className = 'predicted-word';
        return;
    }

    var words = text.trim().split(' ');
    var lastWord = words[words.length - 1];
    
    if (text.endsWith(' ')) {
        predictedWordElement.textContent = '';
        predictedWordElement.className = 'predicted-word';
        return;
    }

    fetch('/predict_word', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({partial_word: lastWord})
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        if (data.predicted_word) {
            predictedWordElement.textContent = data.predicted_word;
            predictedWordElement.className = 'predicted-word highlight';
        } else {
            predictedWordElement.textContent = 'No prediction available';
            predictedWordElement.className = 'predicted-word';
        }
    })
    .catch(function(error) {
        console.error('Error predicting word:', error);
    });
}

function updateSuggestions(text) {
    // Implementation for updating suggestions
    console.log("Updating suggestions based on:", text);
}

function handlePredictedWordClick() {
    var predictedWordElement = this;
    var predictedWord = predictedWordElement.textContent;
    var decodedTextElement = document.getElementById('decoded-text');
    
    if (!predictedWord || !decodedTextElement || predictedWord === 'No prediction available') {
        return;
    }

    var currentText = decodedTextElement.textContent || '';
    var words = currentText.trim().split(' ');
    words.pop();
    words.push(predictedWord);
    
    var newText = words.join(' ') + ' ';
    decodedTextElement.textContent = newText;
    predictedWordElement.textContent = '';
    predictedWordElement.className = 'predicted-word';
    
    fetch('/update_decoded_text', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({text: newText})
    });
}