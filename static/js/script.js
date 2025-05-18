document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('inputForm');
    const recommendationsDiv = document.getElementById('recommendations');
    const headerDiv = document.querySelector('.header');
    const headerTitle = headerDiv.querySelector('h1');
    const refreshButton = document.getElementById('refreshButton');
    const excludeAnimationCheckbox = document.getElementById('excludeAnimation');
    let lastInputText = null;  // Store the last input text instead of emotions

    // Set user-logged-in class on body based on authentication status
    if (window.USER_IS_AUTHENTICATED === true || window.USER_IS_AUTHENTICATED === 'true') {
        document.body.classList.add('user-logged-in');
    } else {
        document.body.classList.remove('user-logged-in');
    }

    // --- Input section movement logic ---
    function moveInputSectionToFloating() {
        const inputSection = document.getElementById('inputForm');
        const refreshButton = document.getElementById('refreshButton');
        if (inputSection && refreshButton) {
            inputSection.classList.add('input-section-floating');
            // Move inputSection after refreshButton
            refreshButton.parentNode.insertBefore(inputSection, refreshButton.nextSibling);
        }
    }

    function moveInputSectionToBottom() {
        const inputSection = document.getElementById('inputForm');
        inputSection.classList.remove('input-section-floating');
        // Move it to the end of the container (so it's at the bottom)
        const container = document.querySelector('.container');
        if (container) {
            container.parentNode.appendChild(inputSection);
        } else {
            document.body.appendChild(inputSection);
        }
    }

    // On page load, ensure input is at the bottom
    moveInputSectionToBottom();

    // --- Loading card logic ---
    function showMovionLoading() {
        let card = document.getElementById('movion-loading-card');
        if (!card) {
            card = document.createElement('div');
            card.id = 'movion-loading-card';
            card.innerHTML = `
                <div class="spinner"></div>
                <div>MoviOn is trying to understand your emotions...</div>
            `;
            // Append to the main container
            const container = document.querySelector('.container');
            if (container) {
                container.appendChild(card);
            } else {
                document.body.appendChild(card);
            }
        }
        card.style.display = 'flex';
    }

    function hideMovionLoading() {
        const card = document.getElementById('movion-loading-card');
        if (card) card.style.display = 'none';
    }

    // --- Error box logic ---
    function showMovionError(message) {
        let box = document.getElementById('movion-error-box');
        if (!box) {
            box = document.createElement('div');
            box.id = 'movion-error-box';
            document.body.appendChild(box);
        }
        box.innerHTML = `
            <span>${message}</span>
            <button class="close-btn" onclick="this.parentNode.style.display='none'">&times;</button>
        `;
        box.style.display = 'flex';
        setTimeout(() => { if (box) box.style.display = 'none'; }, 4000);
    }

    async function displayMovies(data) {
        // Clear previous recommendations
        recommendationsDiv.innerHTML = '';
        
        // Clear previous info container if it exists
        const previousInfoContainer = document.querySelector('.info-container');
        if (previousInfoContainer) {
            previousInfoContainer.remove();
        }
        
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

        // Create a container for spell correction and emotion prediction
        const infoContainer = document.createElement('div');
        infoContainer.className = 'info-container';
        
        // Show spell correction info if text was corrected
        if (data.spell_correction && data.spell_correction.was_corrected) {
            const correctionDiv = document.createElement('div');
            correctionDiv.className = 'spell-correction-info';
            correctionDiv.innerHTML = `
                <div class="correction-message">
                    <span>MoviOn corrected some spelling to better understand your emotions:</span>
                </div>
                <div class="correction-details">
                    <div class="original-text">Original: "${data.spell_correction.original_text}"</div>
                    <div class="corrected-text">Corrected: "${data.spell_correction.corrected_text}"</div>
                </div>
            `;
            infoContainer.appendChild(correctionDiv);
        }

        // Add predicted emotion text
        const emotionDiv = document.createElement('div');
        emotionDiv.classList.add('predicted-emotion');
        
        // Get the first emotion and its category
        const firstEmotion = data.predicted_emotion[0];
        const emotionCategory = data.emotion_category || firstEmotion;  // Use provided category or fallback to first emotion
        emotionDiv.textContent = `ML Model predicts you are feeling: ${emotionCategory}`;
        
        infoContainer.appendChild(emotionDiv);
        
        // Insert the info container after the recommendations
        recommendationsDiv.parentNode.insertBefore(infoContainer, recommendationsDiv.nextSibling);

        // Show refresh button
        refreshButton.style.display = 'flex';
        // Move input section under the refresh button
        moveInputSectionToFloating();
        // Hide loading overlay
        hideMovionLoading();
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

        // --- Add buttons under the tag ---
        const actionsDiv = document.createElement('div');
        actionsDiv.style.display = 'flex';
        actionsDiv.style.flexDirection = 'column';
        actionsDiv.style.alignItems = 'stretch';
        actionsDiv.style.gap = '8px';
        actionsDiv.style.marginTop = '12px';

        // Only show buttons if user is logged in
        if (window.USER_IS_AUTHENTICATED === true || window.USER_IS_AUTHENTICATED === 'true') {
            // Track state for this card
            let isWatched = false;
            let inWatchlist = false;

            // Mark as Watched button
            const watchedBtn = document.createElement('button');
            watchedBtn.className = 'recommend-action-btn';
            watchedBtn.innerHTML = '<i class="far fa-circle"></i> Mark as Watched';
            watchedBtn.onclick = async (e) => {
                e.stopPropagation();
                if (inWatchlist) {
                    showMovionError("Remove from Watch Later before marking as watched.");
                    return;
                }
                try {
                    const res = await fetch(`/toggle_watched/${encodeURIComponent(movie.title)}`, { method: 'POST' });
                    let data;
                    try {
                        data = await res.json();
                    } catch (err) {
                        data = {};
                    }
                    if (res.status === 400 && data.message) {
                        showMovionError(data.message);
                    } else if (data.success) {
                        isWatched = data.is_watched;
                        if (isWatched) {
                            watchedBtn.innerHTML = '<i class="fas fa-check"></i> Marked!';
                        } else {
                            watchedBtn.innerHTML = '<i class="far fa-circle"></i> Mark as Watched';
                        }
                    } else {
                        watchedBtn.innerHTML = 'Error';
                    }
                } catch (err) {
                    watchedBtn.innerHTML = 'Error';
                }
            };

            // Watch Later button
            const watchLaterBtn = document.createElement('button');
            watchLaterBtn.className = 'recommend-action-btn';
            watchLaterBtn.innerHTML = '<i class="far fa-bookmark"></i> Add to Watch Later';
            watchLaterBtn.onclick = async (e) => {
                e.stopPropagation();
                if (isWatched) {
                    showMovionError("Remove from Watched before adding to Watch Later.");
                    return;
                }
                try {
                    const res = await fetch(`/toggle_watchlist/${encodeURIComponent(movie.title)}`, { method: 'POST' });
                    let data;
                    try {
                        data = await res.json();
                    } catch (err) {
                        data = {};
                    }
                    if (res.status === 400 && data.message) {
                        showMovionError(data.message);
                    } else if (data.success) {
                        inWatchlist = data.in_watchlist || data.in_watchlist === true;
                        if (inWatchlist) {
                            watchLaterBtn.innerHTML = '<i class="fas fa-check"></i> Added!';
                        } else {
                            watchLaterBtn.innerHTML = '<i class="far fa-bookmark"></i> Add to Watch Later';
                        }
                    } else {
                        watchLaterBtn.innerHTML = 'Error';
                    }
                } catch (err) {
                    watchLaterBtn.innerHTML = 'Error';
                }
            };

            actionsDiv.appendChild(watchedBtn);
            actionsDiv.appendChild(watchLaterBtn);
        }
        // --- End buttons ---

        movieFront.appendChild(image);
        movieFront.appendChild(name);
        movieFront.appendChild(duration);
        movieFront.appendChild(therapyText);
        movieFront.appendChild(actionsDiv);
        
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

        // Show loading overlay
        showMovionLoading();

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
            // Hide loading overlay on error
            hideMovionLoading();
        } finally {
            // Re-enable input and button
            moodInput.disabled = false;
            submitButton.disabled = false;
            moodInput.value = '';
        }
    });

    // Auto-resize for the mood textarea
    const moodTextarea = document.getElementById('mood');
    if (moodTextarea) {
        moodTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
});
