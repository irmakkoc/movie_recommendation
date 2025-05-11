import pandas as pd

# Global load
df = pd.read_csv("filtered_movies.csv")
df["genre_list"] = df["genres"].apply(lambda x: [g.strip() for g in str(x).split(",")])

# Optional: Normalize popularity
df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
df["popularity_score"] = df["popularity"].apply(lambda x: max(0.1, x))  # Avoid zeros

# Emotion mapping to broader categories
emotion_map = {
    'happy': ['joy', 'admiration', 'amusement', 'approval', 'caring', 'gratitude', 'love', 'optimism', 'pride', 'relief'],
    'sad': ['sadness', 'grief', 'remorse'],
    'angry': ['anger'],
    'fearful': ['fear', 'nervousness'],
    'surprised': ['surprise', 'confusion', 'curiosity', 'excitement'],
    'bad': ['disappointment', 'disapproval', 'annoyance', 'disgust'],
    'neutral': ['neutral']
}

# Reverse mapping for quick lookup
reverse_emotion_map = {}
for category, emotions in emotion_map.items():
    for emotion in emotions:
        reverse_emotion_map[emotion] = category

# Emotion to genre mapping (using broader categories)
emotion_to_genres = {
    "happy": ["Comedy", "Animation", "Music"],
    "sad": ["Romance", "Drama", "Comedy", "Family"],
    "angry": ["Action", "Crime"],
    "fearful": ["Horror", "Thriller"],
    "surprised": ["Mystery", "Fantasy", "Science Fiction"],
    "bad": ["Drama", "History", "War", "Comedy"],
    "neutral": ["Adventure", "Family", "TV Movie", "Documentary", "History", "Science Fiction","Comedy","Romance"]
}

def get_emotion_category(emotion):
    """Convert detailed emotion to its broader category"""
    return reverse_emotion_map.get(emotion.lower(), 'neutral')

def recommend_movies(emotion, count=4):
    # Convert detailed emotion to category
    emotion_category = get_emotion_category(emotion)
    print(f"Using emotion category: {emotion_category}")  # Debug print
    genres = emotion_to_genres.get(emotion_category.lower(), [])
    print(f"Looking for genres: {genres}")  # Debug print

    # Match genres only
    matches = df[df["genre_list"].apply(lambda gl: any(g in gl for g in genres))]

    if matches.empty:
        print("No matches found!")  # Debug print
        return []

    # Sample directly with popularity weighting
    selected = matches.sample(
        n=min(count, len(matches)),
        weights=matches["popularity_score"],
        replace=False
    )

    # Return full movie details
    movies = []
    for _, movie in selected.iterrows():
        movies.append({
            "title": movie["title"],
            "genres": movie["genre_list"],
            "runtime": int(movie["runtime"]) if pd.notnull(movie["runtime"]) else 0,
            "release_date": movie["release_date"][:4] if isinstance(movie["release_date"], str) else "",
            "original_language": str(movie["original_language"]).upper() if pd.notnull(movie["original_language"]) else "?",
            "imdb_id": movie["imdb_id"] if pd.notnull(movie["imdb_id"]) else None,
            "popularity": float(movie["popularity"]) if pd.notnull(movie["popularity"]) else 0
        })

    return movies
