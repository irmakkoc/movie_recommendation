document.addEventListener('DOMContentLoaded', function() {
    // Mark as Watched
    document.querySelectorAll('.watch-toggle').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const movieTitle = this.getAttribute('data-movie-title');
            fetch(`/toggle_watched/${encodeURIComponent(movieTitle)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        });
    });

    // Add to Watch Later
    document.querySelectorAll('.watchlist-toggle').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const movieTitle = this.getAttribute('data-movie-title');
            fetch(`/toggle_watchlist/${encodeURIComponent(movieTitle)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
        });
    });
}); 