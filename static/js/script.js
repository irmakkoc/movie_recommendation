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
            const movieDiv = createMovieCard(movie);
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

    function createMovieCard(movie) {
        const movieElement = document.createElement('div');
        movieElement.className = 'movie';
        
        // Create the inner container for flip animation
        const movieInner = document.createElement('div');
        movieInner.className = 'movie-inner';
        
        // Create front side (movie info)
        const movieFront = document.createElement('div');
        movieFront.className = 'movie-front';
        
        const image = document.createElement('div');
        image.className = 'movie-image';
        image.style.backgroundImage = `url(${movie.poster_path})`;
        
        const name = document.createElement('div');
        name.className = 'movie-name';
        name.textContent = movie.title;
        
        const duration = document.createElement('div');
        duration.className = 'movie-duration';
        duration.textContent = `${movie.runtime} min`;
        
        const therapyText = document.createElement('div');
        therapyText.className = 'therapy-text';
        therapyText.textContent = movie.tag;

        // Add movie actions if user is logged in
        if (window.USER_IS_AUTHENTICATED === true || window.USER_IS_AUTHENTICATED === 'true') {
            const movieActions = document.createElement('div');
            movieActions.className = 'movie-actions';
            const watchToggle = document.createElement('button');
            watchToggle.className = 'watch-toggle';
            watchToggle.dataset.movieTitle = movie.title;
            watchToggle.innerHTML = '<i class="far fa-circle"></i> Mark as Watched';
            const watchlistToggle = document.createElement('button');
            watchlistToggle.className = 'watchlist-toggle';
            watchlistToggle.dataset.movieTitle = movie.title;
            watchlistToggle.innerHTML = '<i class="far fa-bookmark"></i> Add to Watch Later';
            movieActions.appendChild(watchToggle);
            movieActions.appendChild(watchlistToggle);
            movieFront.appendChild(movieActions);
            // Add event listeners for the action buttons
            watchToggle.addEventListener('click', async (e) => {
                e.stopPropagation();
                try {
                    const response = await fetch(`/toggle_watched/${encodeURIComponent(movie.title)}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });
                    const data = await response.json();
                    if (data.success) {
                        watchToggle.innerHTML = data.is_watched ? 
                            '<i class="fas fa-check-circle"></i> Watched' : 
                            '<i class="far fa-circle"></i> Mark as Watched';
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            });
            watchlistToggle.addEventListener('click', async (e) => {
                e.stopPropagation();
                try {
                    const response = await fetch(`/toggle_watchlist/${encodeURIComponent(movie.title)}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });
                    const data = await response.json();
                    if (data.success) {
                        watchlistToggle.innerHTML = data.in_watchlist ? 
                            '<i class="fas fa-bookmark"></i> In Watch Later' : 
                            '<i class="far fa-bookmark"></i> Add to Watch Later';
                    }
                } catch (error) {
                    console.error('Error:', error);
                }
            });
        }
        
        movieFront.appendChild(image);
        movieFront.appendChild(name);
        movieFront.appendChild(duration);
        movieFront.appendChild(therapyText);
        
        // Only add trailer back side and flip if trailer_url is present
        if (movie.trailer_url) {
            const movieBack = document.createElement('div');
            movieBack.className = 'movie-back';
            
            const closeButton = document.createElement('button');
            closeButton.className = 'close-trailer';
            closeButton.innerHTML = '×';
            closeButton.onclick = (e) => {
                e.stopPropagation();
                movieElement.classList.remove('flipped');
            };
            
            const trailerFrame = document.createElement('iframe');
            trailerFrame.src = movie.trailer_url;
            trailerFrame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
            trailerFrame.allowFullscreen = true;
            
            movieBack.appendChild(closeButton);
            movieBack.appendChild(trailerFrame);
            
            // Add click event for flipping
            movieElement.addEventListener('click', () => {
                movieElement.classList.toggle('flipped');
            });
            
            // Assemble the card
            movieInner.appendChild(movieFront);
            movieInner.appendChild(movieBack);
        } else {
            // Only show the front side, no flip
            movieInner.appendChild(movieFront);
        }
        movieElement.appendChild(movieInner);

        return movieElement;
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
