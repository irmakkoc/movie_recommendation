document.addEventListener('DOMContentLoaded', function() {
    // Create error notification element
    const errorNotification = document.createElement('div');
    errorNotification.className = 'error-notification';
    errorNotification.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <p class="message"></p>
        <button class="close-btn">
            <i class="fas fa-times"></i>
        </button>
    `;
    document.body.appendChild(errorNotification);

    // Function to show error notification
    function showError(message) {
        const messageElement = errorNotification.querySelector('.message');
        messageElement.textContent = message;
        errorNotification.classList.add('show');

        // Auto hide after 5 seconds
        setTimeout(() => {
            errorNotification.classList.remove('show');
        }, 5000);
    }

    // Close button functionality
    errorNotification.querySelector('.close-btn').addEventListener('click', () => {
        errorNotification.classList.remove('show');
    });

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
            .then(res => {
                if (!res.ok) {
                    return res.json().then(data => {
                        throw new Error(data.message || 'Failed to add to watchlist');
                    });
                }
                return res.json();
            })
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            })
            .catch(error => {
                showError(error.message);
            });
        });
    });
}); 