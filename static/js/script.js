document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('inputForm');
    const recommendationsDiv = document.getElementById('recommendations');
    const headerDiv = document.querySelector('.header');
    const headerTitle = headerDiv.querySelector('h1');
    const refreshButton = document.getElementById('refreshButton');
    const excludeAnimationCheckbox = document.getElementById('excludeAnimation');
    let lastInputText = null;  // Store the last input text instead of emotions

    async function displayMovies(data) {
        // Clear previous recommendations
        recommendationsDiv.innerHTML = '';
        
        // Create and display movie cards
        data.movies.forEach((movie, index) => {
            const movieDiv = document.createElement('div');
            movieDiv.classList.add('movie');
            
            const movieImage = document.createElement('div');
            movieImage.classList.add('movie-image');
            movieImage.style.backgroundImage = `url(${movie.poster_path})`;
            
            const movieName = document.createElement('p');
            movieName.classList.add('movie-name');
            movieName.textContent = movie.title;

            const movieDuration = document.createElement('p');
            movieDuration.classList.add('movie-duration');
            movieDuration.textContent = `${movie.runtime} minutes`;

            // Add therapy text from the API response
            const therapyText = document.createElement('p');
            therapyText.classList.add('therapy-text');
            therapyText.textContent = movie.tag;  // Use the tag directly from the API response
            
            movieDiv.appendChild(movieImage);
            movieDiv.appendChild(movieName);
            movieDiv.appendChild(movieDuration);
            movieDiv.appendChild(therapyText);
            recommendationsDiv.appendChild(movieDiv);
            
            // Animation for each movie card
            setTimeout(() => {
                movieDiv.style.opacity = '1';
                movieDiv.style.transform = 'translateY(0)';
            }, index * 300);
        });

        // Show recommendations with animation
        recommendationsDiv.style.display = 'flex';
        recommendationsDiv.style.opacity = '1';

        // Update or add predicted emotion text
        let emotionDiv = document.querySelector('.predicted-emotion');
        if (!emotionDiv) {
            emotionDiv = document.createElement('div');
            emotionDiv.classList.add('predicted-emotion');
            recommendationsDiv.parentNode.insertBefore(emotionDiv, recommendationsDiv.nextSibling);
        }

        // Get the first emotion and its category
        const firstEmotion = data.predicted_emotion[0];
        const emotionCategory = data.emotion_category || firstEmotion;  // Use provided category or fallback to first emotion
        emotionDiv.textContent = `ML Model predicts your mood is: ${emotionCategory}`;

        // Show refresh button
        refreshButton.style.display = 'flex';
    }

    async function getNewRecommendations(text) {
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: text,
                    excludeAnimation: excludeAnimationCheckbox.checked 
                }),
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            await displayMovies(data);

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while refreshing recommendations. Please try again.');
        }
    }

    refreshButton.addEventListener('click', async () => {
        if (lastInputText) {
            refreshButton.disabled = true;
            refreshButton.classList.add('loading');
            
            try {
                await getNewRecommendations(lastInputText);
            } finally {
                refreshButton.disabled = false;
                refreshButton.classList.remove('loading');
            }
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const moodInput = document.getElementById('mood');
        const submitButton = document.getElementById('submit');

        // Disable input and button while processing
        moodInput.disabled = true;
        submitButton.disabled = true;

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: moodInput.value,
                    excludeAnimation: excludeAnimationCheckbox.checked 
                }),
            });

            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Store the input text for refresh button
            lastInputText = moodInput.value;

            // Adjust header to show only title
            headerDiv.style.minHeight = 'auto';
            headerDiv.style.padding = '20px 0';
            headerTitle.style.fontSize = '2.5rem';
            headerTitle.style.marginBottom = '30px';

            await displayMovies(data);

        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while getting recommendations. Please try again.');
            // Reset header to original state
            headerDiv.style.minHeight = 'calc(100vh - 300px)';
            headerDiv.style.padding = '0';
            headerTitle.style.fontSize = '3.5rem';
            headerTitle.style.marginBottom = '15px';
        } finally {
            // Re-enable input and button
            moodInput.disabled = false;
            submitButton.disabled = false;
            moodInput.value = '';
        }
    });
});
