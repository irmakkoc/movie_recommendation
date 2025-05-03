from flask import Flask, request, jsonify, render_template
from predict_emotion import predict  
from movie_recommender import recommend_movies
from tmdb_poster import fetch_movie_poster
import pandas as pd

app = Flask(__name__)

# Load pre-filtered CSV once
df = pd.read_csv("filtered_movies_cleaned.csv")

# Therapy tags for frontend display
genre_to_therapy = {
    "Drama": "💧 For catharsis",
    "Romance": "💧 For catharsis",
    "Comedy": "🌤️ To lift your spirits",
    "Animation": "🌤️ To lift your spirits",
    "Family": "🌤️ To lift your spirits",
    "Action": "💥 To release tension",
    "Crime": "💥 To release tension",
    "Fantasy": "🧠 For escape",
    "Science Fiction": "🧠 For escape",
    "Mystery": "🧠 For escape",
    "Thriller": "🧠 For escape",
    "Horror": "💥 To confront fear",
    "History": "🛡️ For reflection",
    "War": "🛡️ For reflection",
    "TV Movie": "🛡️ For comfort",
    "Adventure": "🧠 For escape",
    "Music": "🌤️ To lift your spirits"
}

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def get_emotion():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Invalid request. Provide 'text' in JSON format."}), 400

        text = data["text"]
        emotion = predict(text)
        print("🎭 Predicted emotion:", emotion)

        movie_titles = recommend_movies(emotion)
        print("🎬 Recommended movie list:", movie_titles)

        movies_with_metadata = []

        for title in movie_titles:
            row = df[df['title'] == title]
            if row.empty:
                continue

            row = row.iloc[0]
            genre_str = row['genres']

            # Use TMDb poster or fallback
            poster_url = fetch_movie_poster(title) or "https://via.placeholder.com/300x450?text=No+Image"

            # IMDb link
            imdb_url = f"https://www.imdb.com/title/{row['imdb_id']}" if pd.notnull(row['imdb_id']) else None

            # Year (already clean from your CSV)
            release_year = row['release_date'][:4] if isinstance(row['release_date'], str) and len(row['release_date']) >= 4 else "Unknown"

            # Other info
            runtime = int(row['runtime']) if pd.notnull(row['runtime']) else "?"
            language = str(row['original_language']).upper() if pd.notnull(row['original_language']) else "?"
            genres = [g.strip() for g in genre_str.split(',')] if genre_str else []

            # Therapy tag
            tag = "🎬 For your mood"
            for g in genre_to_therapy:
                if g in genre_str:
                    tag = genre_to_therapy[g]
                    break

            movies_with_metadata.append({
                "title": str(title),
                "poster": poster_url,
                "tag": tag,
                "release_date": release_year,
                "imdb_url": imdb_url,
                "runtime": runtime,
                "genres": genres,
                "language": language
            })

        return jsonify({"emotion": emotion, "movies": movies_with_metadata})

    except Exception as e:
        print("🛑 SERVER ERROR:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
