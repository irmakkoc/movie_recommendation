from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, WatchedMovie, WatchLaterMovie

movie_lists = Blueprint('movie_lists', __name__)

@movie_lists.route('/toggle_watched/<path:movie_title>', methods=['POST'])
@login_required
def toggle_watched(movie_title):
    # Check if movie is already watched
    watched_movie = WatchedMovie.query.filter_by(
        user_id=current_user.id,
        movie_title=movie_title
    ).first()
    
    if watched_movie:
        # If movie is watched, remove it
        db.session.delete(watched_movie)
        is_watched = False
    else:
        # Check if movie is in watchlist and remove it
        watchlist_movie = WatchLaterMovie.query.filter_by(
            user_id=current_user.id,
            movie_title=movie_title
        ).first()
        
        if watchlist_movie:
            db.session.delete(watchlist_movie)
        
        # Add to watched list
        watched_movie = WatchedMovie(
            user_id=current_user.id,
            movie_title=movie_title
        )
        db.session.add(watched_movie)
        is_watched = True
    
    db.session.commit()
    return jsonify({'success': True, 'is_watched': is_watched})

@movie_lists.route('/toggle_watchlist/<path:movie_title>', methods=['POST'])
@login_required
def toggle_watchlist(movie_title):
    # First check if movie is in watched list
    watched_movie = WatchedMovie.query.filter_by(
        user_id=current_user.id,
        movie_title=movie_title
    ).first()
    
    if watched_movie:
        return jsonify({
            'success': False, 
            'message': 'You have to remove this movie from your watched list first'
        }), 400
    
    # Check if movie is already in watchlist
    watchlist_movie = WatchLaterMovie.query.filter_by(
        user_id=current_user.id,
        movie_title=movie_title
    ).first()
    
    if watchlist_movie:
        # If movie is in watchlist, remove it
        db.session.delete(watchlist_movie)
        in_watchlist = False
    else:
        # If movie is not in watchlist, add it
        watchlist_movie = WatchLaterMovie(
            user_id=current_user.id,
            movie_title=movie_title
        )
        db.session.add(watchlist_movie)
        in_watchlist = True
    
    db.session.commit()
    return jsonify({'success': True, 'in_watchlist': in_watchlist}) 