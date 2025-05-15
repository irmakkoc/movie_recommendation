// --- Utility functions at top-level scope ---
function renderMoviesGrid(movies) {
    const grid = document.querySelector('.movies-grid');
    if (!grid) return;
    if (!movies || movies.length === 0) {
        grid.innerHTML = '<p style="color: #fff; text-align: center; width: 100%;">No movies found.</p>';
        return;
    }
    grid.innerHTML = movies.map(movie => `
        <div class="movie-card${movie.is_watched ? ' watched' : ''}${movie.in_watchlist ? ' watchlater' : ''}" 
             data-status="${movie.is_watched ? 'watched' : (movie.in_watchlist ? 'watchlater' : 'unwatched')}" 
             data-title="${movie.title.toLowerCase()}" 
             data-genres="${Array.isArray(movie.genres) ? movie.genres.join(',').toLowerCase() : ''}">
            <div class="movie-poster">
                <img src="${movie.poster_path}" alt="${movie.title} poster">
                <div class="movie-overlay">
                    <div class="movie-actions">
                        <button class="watch-toggle" data-movie-title="${movie.title}">
                            ${movie.is_watched ? '<i class=\'fas fa-check-circle\'></i> Watched' : '<i class=\'far fa-circle\'></i> Mark as Watched'}
                        </button>
                        <button class="watchlist-toggle" data-movie-title="${movie.title}">
                            ${movie.in_watchlist ? '<i class=\'fas fa-bookmark\'></i> In Watch Later' : '<i class=\'far fa-bookmark\'></i> Add to Watch Later'}
                        </button>
                    </div>
                </div>
            </div>
            <div class="movie-info">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <p class="release-date" style="margin: 0;">${movie.release_date || ''}</p>
                    <p class="release-date" style="margin: 0;">${movie.runtime ? movie.runtime + ' min' : ''}</p>
                </div>
                <h3>${movie.title}</h3>
                <div class="genres">
                    ${(Array.isArray(movie.genres) ? movie.genres : []).map(genre => `<span class=\'genre-tag\'>${genre}</span>`).join('')}
                </div>
            </div>
        </div>
    `).join('');
}

function attachMovieActionListeners() {
    document.querySelectorAll('.watch-toggle').forEach(function(btn) {
        btn.addEventListener('click', async function() {
            const movieTitle = this.getAttribute('data-movie-title');
            try {
                const res = await fetch(`/toggle_watched/${encodeURIComponent(movieTitle)}`, { method: 'POST' });
                let data;
                try {
                    data = await res.json();
                } catch (err) {
                    data = {};
                }
                if (res.status === 400 && data.message) {
                    showMovionError(data.message);
                } else if (data.success) {
                    // If on 'watched' filter, reload watched list, else reload page
                    const activeFilterBtn = document.querySelector('.movies-section .filters .filter-btn.active');
                    if (activeFilterBtn && activeFilterBtn.dataset.filter === 'watched') {
                        fetch('/api/watched_movies')
                            .then(response => response.json())
                            .then(movies => {
                                renderMoviesGrid(movies);
                                attachMovieActionListeners();
                            })
                            .catch(error => {
                                console.error('Error fetching movies:', error);
                            });
                    } else {
                        location.reload();
                    }
                }
            } catch (error) {
                showMovionError('An error occurred. Please try again.');
            }
        });
    });

    document.querySelectorAll('.watchlist-toggle').forEach(function(btn) {
        btn.addEventListener('click', async function() {
            const movieTitle = this.getAttribute('data-movie-title');
            try {
                const res = await fetch(`/toggle_watchlist/${encodeURIComponent(movieTitle)}`, { method: 'POST' });
                let data;
                try {
                    data = await res.json();
                } catch (err) {
                    data = {};
                }
                if (res.status === 400 && data.message) {
                    showMovionError(data.message);
                } else if (data.success) {
                    const activeFilterBtn = document.querySelector('.movies-section .filters .filter-btn.active');
                    if (activeFilterBtn && activeFilterBtn.dataset.filter === 'watchlater') {
                        fetch('/api/watch_later_movies')
                            .then(response => response.json())
                            .then(movies => {
                                renderMoviesGrid(movies);
                                attachMovieActionListeners();
                            })
                            .catch(error => {
                                console.error('Error fetching movies:', error);
                            });
                    } else {
                        location.reload();
                    }
                }
            } catch (error) {
                showMovionError('An error occurred. Please try again.');
            }
        });
    });
}

// --- Main logic ---
document.addEventListener('DOMContentLoaded', function() {
    // Mark as Watched
    document.querySelectorAll('.watch-toggle').forEach(function(btn) {
        btn.addEventListener('click', async function() {
            const movieTitle = this.getAttribute('data-movie-title');
            try {
                const res = await fetch(`/toggle_watched/${encodeURIComponent(movieTitle)}`, { method: 'POST' });
                let data;
                try {
                    data = await res.json();
                } catch (err) {
                    data = {};
                }
                if (res.status === 400 && data.message) {
                    showMovionError(data.message);
                } else if (data.success) {
                    // If on 'watched' filter, reload watched list, else reload page
                    const activeFilterBtn = document.querySelector('.movies-section .filters .filter-btn.active');
                    if (activeFilterBtn && activeFilterBtn.dataset.filter === 'watched') {
                        fetch('/api/watched_movies')
                            .then(response => response.json())
                            .then(movies => {
                                renderMoviesGrid(movies);
                                attachMovieActionListeners();
                            })
                            .catch(error => {
                                console.error('Error fetching movies:', error);
                            });
                    } else {
                        location.reload();
                    }
                }
            } catch (error) {
                showMovionError('An error occurred. Please try again.');
            }
        });
    });

    // Add to Watch Later
    document.querySelectorAll('.watchlist-toggle').forEach(function(btn) {
        btn.addEventListener('click', async function() {
            const movieTitle = this.getAttribute('data-movie-title');
            try {
                const res = await fetch(`/toggle_watchlist/${encodeURIComponent(movieTitle)}`, { method: 'POST' });
                let data;
                try {
                    data = await res.json();
                } catch (err) {
                    data = {};
                }
                if (res.status === 400 && data.message) {
                    showMovionError(data.message);
                } else if (data.success) {
                    const activeFilterBtn = document.querySelector('.movies-section .filters .filter-btn.active');
                    if (activeFilterBtn && activeFilterBtn.dataset.filter === 'watchlater') {
                        fetch('/api/watch_later_movies')
                            .then(response => response.json())
                            .then(movies => {
                                renderMoviesGrid(movies);
                                attachMovieActionListeners();
                            })
                            .catch(error => {
                                console.error('Error fetching movies:', error);
                            });
                    } else {
                        location.reload();
                    }
                }
            } catch (error) {
                showMovionError('An error occurred. Please try again.');
            }
        });
    });

    // Search functionality
    const searchButton = document.getElementById('search-btn');
    const searchInput = document.getElementById('movie-search');
    const sortSelect = document.getElementById('sort-by');

    function updateQueryAndReload() {
        const currentUrl = new URL(window.location.href);
        const searchTerm = searchInput.value.trim();
        const sortBy = sortSelect.value;

        if (searchTerm) {
            currentUrl.searchParams.set('search', searchTerm);
        } else {
            currentUrl.searchParams.delete('search');
        }

        if (sortBy && sortBy !== 'default') {
            currentUrl.searchParams.set('sort_by', sortBy);
        } else {
            currentUrl.searchParams.delete('sort_by');
        }
        
        // Always go to page 1 when search or sort changes
        currentUrl.searchParams.set('page', '1'); 

        window.location.href = currentUrl.toString();
    }

    if (searchButton && searchInput) {
        searchButton.addEventListener('click', function() {
            updateQueryAndReload();
        });

        searchInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevent form submission if it's part of a form
                updateQueryAndReload();
            }
        });
    }

    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            updateQueryAndReload();
        });
    }

    // Attach to filter buttons
    document.querySelectorAll('.movies-section .filters .filter-btn').forEach(button => {
        button.addEventListener('click', function() {
            const previouslyActiveButton = document.querySelector('.movies-section .filters .filter-btn.active');
            if (previouslyActiveButton) {
                previouslyActiveButton.classList.remove('active');
            }
            button.classList.add('active');
            const filterType = button.dataset.filter;
            if (filterType === 'all') {
                // Reload the page to show all movies (default paginated view)
                window.location.href = window.location.pathname;
            } else if (filterType === 'watched' || filterType === 'watchlater') {
                // Fetch and render movies from the API
                let apiUrl = filterType === 'watched' ? '/api/watched_movies' : '/api/watch_later_movies';
                fetch(apiUrl)
                    .then(response => response.json())
                    .then(movies => {
                        renderMoviesGrid(movies);
                        attachMovieActionListeners();
                    })
                    .catch(error => {
                        console.error('Error fetching movies:', error);
                    });
            }
        });
    });

    // Clear All Filters functionality
    var clearFiltersBtn = document.getElementById('clear-filters-btn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            // Clear Select2 genres if jQuery and Select2 are available
            if (typeof $ !== 'undefined' && $.fn.select2) {
                $('#genre-filter').val(null).trigger('change');
            } else {
                var genreFilter = document.getElementById('genre-filter');
                if (genreFilter) genreFilter.value = '';
            }
            // Clear other filter fields
            var searchInput = document.getElementById('movie-search');
            if (searchInput) searchInput.value = '';
            var sortBy = document.getElementById('sort-by');
            if (sortBy) sortBy.selectedIndex = 0;
            var yearMin = document.getElementById('year-min');
            if (yearMin) yearMin.value = '';
            var yearMax = document.getElementById('year-max');
            if (yearMax) yearMax.value = '';
            var runtimeMin = document.getElementById('runtime-min');
            if (runtimeMin) runtimeMin.value = '';
            var runtimeMax = document.getElementById('runtime-max');
            if (runtimeMax) runtimeMax.value = '';
            var languageFilter = document.getElementById('language-filter');
            if (languageFilter) languageFilter.selectedIndex = 0;
            // Redirect to default profile page (no filters)
            window.location.href = window.location.pathname;
        });
    }
});

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