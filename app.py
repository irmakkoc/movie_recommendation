from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from predict_emotion import predict  
from movie_recommender import recommend_movies as get_movie_recommendations, get_emotion_category
from tmdb_poster import fetch_movie_poster
import pandas as pd
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, WatchedMovie, WatchLaterMovie
from flask_migrate import Migrate
import os
import random
import string
from flask_mail import Mail, Message
from datetime import datetime
from functools import lru_cache
from movie_lists import movie_lists
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True  # Enable debug mode
app.config['PROPAGATE_EXCEPTIONS'] = True  # Ensure exceptions are propagated

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'movi.on2025@gmail.com'
app.config['MAIL_PASSWORD'] = 'gjac sdqn vyba sdag'
app.config['MAIL_DEFAULT_SENDER'] = ('MoviOn', 'movi.on2025@gmail.com')
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False
app.config['MAIL_DEBUG'] = True

# Initialize extensions
mail = Mail(app)  # Initialize mail first
db.init_app(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Register blueprints
app.register_blueprint(movie_lists)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create database tables
def init_db():
    with app.app_context():
        # Check if database tables exist
        inspector = db.inspect(db.engine)
        tables_exist = inspector.get_table_names()
        
        if not tables_exist:
            print("Initializing database...")
            db.create_all()
        
            # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username='admin',
                email='admin@moviemood.com',
                is_admin=True
            )
            admin.set_password('admin123')  # You should change this password
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Database already initialized.")

# Initialize the database only if it doesn't exist
init_db()

# Load pre-filtered CSV once
df = pd.read_csv("filtered_movies.csv")

def get_therapy_tag(emotion_category, genres):
    """Determine the appropriate therapy tag based on emotion category and genres"""
    if emotion_category == "happy":
        return "🌤️ To lift your spirits"
    elif emotion_category == "angry":
        return "😌 To feel calmer"
    elif emotion_category == "fearful":
        return "💪 To confront fear"
    elif emotion_category == "surprised":
        return "🎭 For a new perspective"  # New tag for surprised emotion
    elif emotion_category == "sad":
        # Check if the movie has comedy or family genres
        if any(genre in ["Comedy", "Family"] for genre in genres):
            return "🌤️ To lift your spirits"
        # For romance and drama
        elif any(genre in ["Romance", "Drama"] for genre in genres):
            return "💧 For catharsis"
        # Default for other genres
        return "💧 For catharsis"
    elif emotion_category == "bad":
        # Check if the movie has comedy genre
        if "Comedy" in genres:
            return "🌤️ To lift your spirits"
        # For drama, history, and war
        elif any(genre in ["Drama", "History", "War"] for genre in genres):
            return "💧 For catharsis"
        # Default for other genres
        return "💧 For catharsis"
    else:  # neutral
        return "🎬 For entertainment"

# Add poster URL cache
@lru_cache(maxsize=1000)
def get_cached_poster_url(title):
    return fetch_movie_poster(title) or "https://via.placeholder.com/300x450?text=No+Image"

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/recommend', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def get_emotion():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Invalid request. Provide 'text' in JSON format."}), 400

        text = data["text"]
        exclude_animation = data.get("excludeAnimation", False)
        
        # Get prediction result with spell correction info
        prediction_result = predict(text)
        predicted_emotions = prediction_result["predictions"]
        print("🎭 Predicted emotion:", predicted_emotions)

        # Use the first predicted emotion for movie recommendations
        primary_emotion = predicted_emotions[0][0] if predicted_emotions else "neutral"
        recommended_movies = recommend_movies(primary_emotion)
        
        # Filter out animation movies if requested
        if exclude_animation:
            recommended_movies = [movie for movie in recommended_movies if "Animation" not in movie["genres"]]
            
        print("🎬 Recommended movies:", [m["title"] for m in recommended_movies])

        movies_with_metadata = []
        for movie in recommended_movies:
            # Get emotion category
            emotion_category = get_emotion_category(primary_emotion)
            
            # Get therapy tag based on emotion category and genres
            tag = get_therapy_tag(emotion_category, movie["genres"])

            # Get poster URL
            poster_url = get_cached_poster_url(movie["title"])

            # Create IMDb URL if ID exists
            imdb_url = f"https://www.imdb.com/title/{movie['imdb_id']}" if movie["imdb_id"] else None

            # Get trailer URL
            trailer_url = get_movie_trailer(movie["title"])

            movies_with_metadata.append({
                "title": movie["title"],
                "poster_path": poster_url,
                "tag": tag,
                "release_date": movie["release_date"],
                "imdb_url": imdb_url,
                "runtime": movie["runtime"],
                "genres": movie["genres"],
                "language": movie["original_language"],
                "trailer_url": trailer_url
            })

        # Get the emotion category from movie_recommender
        emotion_category = get_emotion_category(primary_emotion)

        return jsonify({
            "predicted_emotion": [emotion[0] for emotion in predicted_emotions],
            "emotion_category": emotion_category,
            "movies": movies_with_metadata,
            "spell_correction": {
                "was_corrected": prediction_result["was_corrected"],
                "original_text": prediction_result["original_text"],
                "corrected_text": prediction_result["corrected_text"]
            }
        })

    except Exception as e:
        print("🛑 SERVER ERROR:", e)
        return jsonify({"error": str(e)}), 500

def get_movie_trailer(title):
    """
    Get the YouTube trailer embed URL for a movie using TMDB API.
    Returns None if not available.
    """
    tmdb_api_key = '9c91b18187d811058d6e72368a39bf12'
    search_url = f'https://api.themoviedb.org/3/search/movie?api_key={tmdb_api_key}&query={title}'
    try:
        search_resp = requests.get(search_url)
        search_resp.raise_for_status()
        search_data = search_resp.json()
        results = search_data.get('results', [])
        if not results:
            return None
        movie_id = results[0]['id']
        videos_url = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={tmdb_api_key}'
        videos_resp = requests.get(videos_url)
        videos_resp.raise_for_status()
        videos_data = videos_resp.json()
        for video in videos_data.get('results', []):
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                return f'https://www.youtube.com/embed/{video["key"]}'
        return None
    except Exception as e:
        print(f"Error fetching trailer for '{title}': {e}")
        return None

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validate input
        if not all([username, email, password, confirm_password]):
            flash('All fields are required')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('signup'))

        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/admin/users')
@login_required
def admin_users():
    # Check if user is admin (you might want to add an admin field to your User model)
    if not current_user.is_authenticated or current_user.username != 'admin':
        flash('Access denied')
        return redirect(url_for('home'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

def generate_reset_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def send_reset_email(user, reset_token):
    try:
        reset_url = url_for('reset_password', token=reset_token, email=user.email, _external=True)
        print(f"Generated reset URL: {reset_url}")
        
        msg = Message(
            subject='Reset Your MoviOn Password',
            sender=('MoviOn', 'movi.on2025@gmail.com'),
            recipients=[user.email]
        )
        
        # Plain text version
        msg.body = f'''Hi there,

You recently requested to reset your password for your MovieOn account. Click the link below to proceed:

{reset_url}

If you didn't request a password reset, you can safely ignore this email. Someone else might have typed your email address by mistake.

The password reset link is valid for 30 minutes.

Thanks,
The MoviOn Team

Note: This is an automated message, please don't reply to this email.
'''
        
        # HTML version with inline styles for better email client compatibility
        msg.html = f'''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333333; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: #007bff; margin: 0; font-size: 24px;">MoviOn Password Reset</h1>
        </div>
        
        <p style="margin-bottom: 15px;">Hi there,</p>
        
        <p style="margin-bottom: 15px;">You recently requested to reset your password for your MoviOn account. Use the button below to reset it.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" style="background-color: #007bff; color: #ffffff; text-decoration: none; padding: 12px 30px; border-radius: 5px; font-weight: bold; display: inline-block;">Reset Your Password</a>
        </div>
        
        <p style="margin-bottom: 15px;">If the button doesn't work, copy and paste this link into your browser:</p>
        <p style="background-color: #f8f9fa; padding: 12px; border-radius: 4px; font-size: 14px; word-break: break-all; margin-bottom: 15px;">
            {reset_url}
        </p>
        
        <p style="margin-bottom: 15px; color: #666666; font-size: 14px;">If you didn't request a password reset, you can safely ignore this email. Someone else might have typed your email address by mistake.</p>
        
        <p style="margin-bottom: 15px; color: #666666; font-size: 14px;">The password reset link is valid for 30 minutes.</p>
        
        <div style="margin-top: 30px; padding-top: 15px; border-top: 1px solid #eeeeee;">
            <p style="margin: 0; color: #666666; font-size: 14px;">Thanks,<br>The MoviOn Team</p>
        </div>
        
        <div style="margin-top: 20px; text-align: center; color: #999999; font-size: 12px;">
            <p style="margin: 0;">This is an automated message, please don't reply to this email.</p>
        </div>
    </div>
</body>
</html>
'''

        # Add headers to help prevent spam classification
        msg.extra_headers = {
            'List-Unsubscribe': f'<mailto:unsubscribe@moviemood.com>',
            'Precedence': 'bulk',
            'X-Auto-Response-Suppress': 'OOF, AutoReply',
            'Auto-Submitted': 'auto-generated'
        }
        
        print(f"Attempting to send email to {user.email}...")
        mail.send(msg)
        print("Email sent successfully!")
        return True
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        return False

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        print(f"Password reset requested for email: {email}")  # Debug line
        user = User.query.filter_by(email=email).first()
        
        if user:
            try:
                token = user.generate_reset_token()
                if send_reset_email(user, token):
                    flash('Password reset instructions have been sent to your email. Please check your spam folder if you don\'t see it in your inbox.')
            except Exception as e:
                print(f"Failed to send reset email: {str(e)}")  # Debug line
                flash('Error sending reset email. Please try again later.')
        else:
            print(f"No user found with email: {email}")  # Debug line
            # Still show the same message for security
            flash('If an account exists with that email, password reset instructions have been sent.')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    # Find user by email from form or query parameter
    email = request.form.get('email') or request.args.get('email')
    if not email:
        flash('Invalid reset link.')
        return redirect(url_for('login'))

    user = User.query.filter_by(email=email).first()
    if not user or not user.verify_reset_token(token):
        flash('Invalid or expired reset link.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('Please enter and confirm your new password.')
            return render_template('reset_password.html', token=token, email=email)
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('reset_password.html', token=token, email=email)
        
        user.set_password(password)
        user.clear_reset_token()
        db.session.commit()
        
        flash('Your password has been reset successfully. Please log in.')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token, email=email)

@app.route('/profile')
@login_required
def profile():
    try:
        # Get page number and search parameters
        page = request.args.get('page', 1, type=int)
        search_term = request.args.get('search', '').lower()
        selected_genres = request.args.get('genres', '').split(',') if request.args.get('genres') else []
        selected_genres = [g.strip() for g in selected_genres if g.strip()]  # Clean up genre list
        selected_language = request.args.get('language', '')
        runtime_min = request.args.get('runtime_min', type=int)
        runtime_max = request.args.get('runtime_max', type=int)
        year = request.args.get('year', type=int)
        year_min = request.args.get('year_min', type=int)
        year_max = request.args.get('year_max', type=int)
        per_page = 20  # Number of movies per page
        sort_by = request.args.get('sort_by', 'default')
        
        # Load the movies from CSV
        movies_df = pd.read_csv("filtered_movies.csv")
        
        # Apply search filter if provided
        if search_term:
            movies_df = movies_df[movies_df['title'].str.lower().str.contains(search_term, na=False)]
            
        # Helper function to parse genres
        def parse_genres(genres_str):
            if pd.isna(genres_str):
                return []
            try:
                # Remove brackets and split by comma
                genres_str = str(genres_str).strip('[]')
                # Split and clean each genre
                return [g.strip().strip('"\'') for g in genres_str.split(',') if g.strip()]
            except:
                return []

        # Convert genres column to list format
        movies_df['genres'] = movies_df['genres'].apply(parse_genres)
        
        # Apply genre filter if provided
        if selected_genres:
            # Filter movies that contain all selected genres
            movies_df = movies_df[movies_df['genres'].apply(
                lambda x: all(
                    any(genre.lower() in g.lower() for g in x)
                    for genre in selected_genres
                )
            )]
        
        # Apply language filter
        if selected_language:
            movies_df = movies_df[movies_df['original_language'] == selected_language]
        
        # Apply runtime filter
        if runtime_min is not None:
            movies_df = movies_df[movies_df['runtime'] >= runtime_min]
        if runtime_max is not None:
            movies_df = movies_df[movies_df['runtime'] <= runtime_max]
        
        # Extract year as a new column for robust filtering
        movies_df['year'] = pd.to_numeric(movies_df['release_date'].astype(str).str[:4], errors='coerce')
        movies_df = movies_df.dropna(subset=['year'])
        movies_df['year'] = movies_df['year'].astype(int)

        # Apply year range filter
        if year_min is not None:
            movies_df = movies_df[movies_df['year'] >= year_min]
        if year_max is not None:
            movies_df = movies_df[movies_df['year'] <= year_max]
        # Apply exact year filter (only if set and min/max are not set)
        if year is not None and not (year_min or year_max):
            movies_df = movies_df[movies_df['year'] == year]
        
        # Sorting logic
        if sort_by == 'release_date_asc':
            movies_df = movies_df.sort_values(by='release_date', ascending=True)
        elif sort_by == 'release_date_desc':
            movies_df = movies_df.sort_values(by='release_date', ascending=False)
        elif sort_by == 'runtime_asc':
            movies_df = movies_df.sort_values(by='runtime', ascending=True)
        elif sort_by == 'runtime_desc':
            movies_df = movies_df.sort_values(by='runtime', ascending=False)
        # else: default order (no sorting)
        
        total_movies = len(movies_df)
        
        # Calculate start and end indices for the current page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_movies)
        
        # Get the slice of movies for the current page
        current_page_df = movies_df.iloc[start_idx:end_idx]
        
        # Get user's watched movies and watchlist
        watched_movies = {movie.movie_title for movie in WatchedMovie.query.filter_by(user_id=current_user.id).all()}
        try:
            watchlist_movies = {movie.movie_title for movie in WatchLaterMovie.query.filter_by(user_id=current_user.id).all()}
        except Exception:
            watchlist_movies = set()
        
        # Get all unique genres
        all_genres = set()
        for genres in movies_df['genres']:
            all_genres.update(genres)
        all_genres = sorted(list(all_genres))
        
        # Get all unique languages
        all_languages = sorted(movies_df['original_language'].dropna().unique())
        
        # Get min/max year and runtime
        years = movies_df['year']
        available_years = sorted(years.unique())
        min_runtime = int(movies_df['runtime'].min()) if not movies_df['runtime'].isnull().all() else 0
        max_runtime = int(movies_df['runtime'].max()) if not movies_df['runtime'].isnull().all() else 300
        min_year = int(years.min()) if not years.empty else 1900
        max_year = int(years.max()) if not years.empty else 2024
        
        # Prepare movies data for template (for All Movies section)
        movies = []
        filtered_watched_count = 0  # Counter for watched movies in filtered results
        main_movie_titles = set()
        for _, movie in current_page_df.iterrows():
            poster_url = get_cached_poster_url(movie['title'])
            is_watched = movie['title'] in watched_movies
            in_watchlist = movie['title'] in watchlist_movies
            # Do NOT filter out movies that are in watched or watchlist
            if is_watched:
                filtered_watched_count += 1
            movies.append({
                'title': movie['title'],
                'poster_path': poster_url,
                'release_date': movie['release_date'],
                'runtime': movie.get('runtime', ''),
                'genres': movie['genres'],
                'is_watched': is_watched,
                'in_watchlist': in_watchlist
            })
            main_movie_titles.add(movie['title'])

        # Build watched_movies_full: all movies in user's WatchedMovie table
        watched_movies_db = WatchedMovie.query.filter_by(user_id=current_user.id).all()
        watched_movies_full = []
        for watched in watched_movies_db:
            # Try to find in dataset
            movie_row = movies_df[movies_df['title'] == watched.movie_title]
            if not movie_row.empty:
                movie = movie_row.iloc[0]
                watched_movies_full.append({
                    'title': movie['title'],
                    'poster_path': get_cached_poster_url(movie['title']),
                    'release_date': movie['release_date'],
                    'runtime': movie.get('runtime', ''),
                    'genres': movie['genres'],
                    'is_watched': True,
                    'in_watchlist': movie['title'] in watchlist_movies
                })
            else:
                # Not in dataset, show minimal info
                watched_movies_full.append({
                    'title': watched.movie_title,
                    'poster_path': get_cached_poster_url(watched.movie_title),
                    'release_date': '',
                    'runtime': '',
                    'genres': [],
                    'is_watched': True,
                    'in_watchlist': False
                })

        # Calculate total pages
        total_pages = max((total_movies + per_page - 1) // per_page, 1)  # Ensure at least 1 page
        
        # Calculate total watched movies in filtered results
        total_filtered_watched = len(set(movies_df['title']).intersection(watched_movies))
        
        return render_template(
            'profile.html',
            movies=movies,
            watched_movies_full=watched_movies_full,
            current_page=page,
            total_pages=total_pages,
            total_movies=total_movies,
            watched_count=len(watched_movies),
            filtered_watched_count=filtered_watched_count,  # Current page watched count
            total_filtered_watched=total_filtered_watched,  # Total filtered watched count
            all_genres=all_genres,
            all_languages=all_languages,
            available_years=available_years,
            min_runtime=min_runtime,
            max_runtime=max_runtime,
            search_term=search_term,
            selected_genres=selected_genres,  # Pass selected genres to template
            selected_language=selected_language,
            runtime_min=runtime_min,
            runtime_max=runtime_max,
            selected_year=year,
            min_year=min_year,
            max_year=max_year,
            year_min=year_min,
            year_max=year_max,
            has_filter=bool(search_term or selected_genres or selected_language or runtime_min is not None or runtime_max is not None or year is not None or year_min is not None or year_max is not None),  # Indicate if any filter is active
            sort_by=sort_by
        )
    except Exception as e:
        print(f"Error in profile route: {str(e)}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")  # Add this line for better error tracking
        # Instead of redirect, render the profile page with an error message
        return render_template(
            'profile.html',
            movies=[],
            watched_movies_full=[],
            current_page=1,
            total_pages=1,
            total_movies=0,
            watched_count=0,
            filtered_watched_count=0,
            total_filtered_watched=0,
            all_genres=[],
            all_languages=[],
            available_years=[],
            min_runtime=0,
            max_runtime=0,
            min_year=1900,
            max_year=2024,
            year_min=None,
            year_max=None,
            search_term='',
            selected_genres=[],
            selected_language='',
            runtime_min=None,
            runtime_max=None,
            selected_year=None,
            has_filter=True,
            error_message='No movies found or invalid filter. Please try different filters.'
        )

# Modify your existing recommend_movies function to exclude watched movies
def recommend_movies(emotion):
    # Get user's watched movies if user is logged in
    watched_titles = []
    if current_user.is_authenticated:
        watched_movies = WatchedMovie.query.filter_by(user_id=current_user.id).all()
        watched_titles = [movie.movie_title for movie in watched_movies]
    
    # Get recommendations using the imported function
    recommended = get_movie_recommendations(emotion)
    
    # Filter out watched movies
    if watched_titles:
        recommended = [movie for movie in recommended if movie['title'] not in watched_titles]
    
    return recommended

@app.route('/api/watched_movies', methods=['GET'])
@login_required
def api_watched_movies():
    # Load movies from CSV
    movies_df = pd.read_csv("filtered_movies.csv")
    watched_movies = WatchedMovie.query.filter_by(user_id=current_user.id).all()
    result = []
    for watched in watched_movies:
        movie_row = movies_df[movies_df['title'] == watched.movie_title]
        if not movie_row.empty:
            movie = movie_row.iloc[0]
            # Ensure all fields are standard Python types
            genres = movie['genres']
            if isinstance(genres, str):
                genres = [g.strip() for g in genres.split(',') if g.strip()]
            result.append({
                'title': str(movie['title']),
                'poster_path': str(get_cached_poster_url(movie['title'])),
                'release_date': str(movie['release_date']),
                'runtime': int(movie['runtime']) if pd.notnull(movie['runtime']) else '',
                'genres': [str(g) for g in genres],
                'is_watched': True,
                'in_watchlist': False
            })
        else:
            result.append({
                'title': str(watched.movie_title),
                'poster_path': str(get_cached_poster_url(watched.movie_title)),
                'release_date': '',
                'runtime': '',
                'genres': [],
                'is_watched': True,
                'in_watchlist': False
            })
    return jsonify(result)

@app.route('/api/watch_later_movies', methods=['GET'])
@login_required
def api_watch_later_movies():
    # Load movies from CSV
    movies_df = pd.read_csv("filtered_movies.csv")
    watch_later_movies = WatchLaterMovie.query.filter_by(user_id=current_user.id).all()
    result = []
    for watchlater in watch_later_movies:
        movie_row = movies_df[movies_df['title'] == watchlater.movie_title]
        if not movie_row.empty:
            movie = movie_row.iloc[0]
            genres = movie['genres']
            if isinstance(genres, str):
                genres = [g.strip() for g in genres.split(',') if g.strip()]
            result.append({
                'title': str(movie['title']),
                'poster_path': str(get_cached_poster_url(movie['title'])),
                'release_date': str(movie['release_date']),
                'runtime': int(movie['runtime']) if pd.notnull(movie['runtime']) else '',
                'genres': [str(g) for g in genres],
                'is_watched': False,
                'in_watchlist': True
            })
        else:
            result.append({
                'title': str(watchlater.movie_title),
                'poster_path': str(get_cached_poster_url(watchlater.movie_title)),
                'release_date': '',
                'runtime': '',
                'genres': [],
                'is_watched': False,
                'in_watchlist': True
            })
    return jsonify(result)

@app.route('/terms-of-use')
def terms_of_use():
    return render_template('terms_of_use.html')

if __name__ == '__main__':
    print("Starting MoviOn...")
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=True)
