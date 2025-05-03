import pandas as pd

# Global load
df = pd.read_csv("filtered_movies_cleaned.csv")
df["genre_list"] = df["genres"].apply(lambda x: [g.strip() for g in str(x).split(",")])

# Optional: Normalize popularity
df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
df["popularity_score"] = df["popularity"].apply(lambda x: max(0.1, x))  # Avoid zeros

# Emotion to genre mapping
emotion_to_genres = {
    "angry": ["Action", "Crime"],
    "bad": ["Drama", "History", "War"],
    "fearful": ["Horror", "Thriller"],
    "happy": ["Comedy", "Animation", "Music"],
    "neutral": ["Adventure", "Family", "TV Movie"],
    "sad": ["Romance", "Drama", "Comedy", "Family"],
    "surprised": ["Mystery", "Fantasy", "Science Fiction"]
}

def recommend_movies(emotion, count=4):
    genres = emotion_to_genres.get(emotion.lower(), [])

    # Match genres only
    matches = df[df["genre_list"].apply(lambda gl: any(g in gl for g in genres))]

    if matches.empty:
        return []

    # Sample directly with popularity weighting
    selected = matches.sample(
        n=min(count, len(matches)),
        weights=matches["popularity_score"],
        replace=False
    )

    print(selected[["title", "popularity", "popularity_score"]])
    return selected["title"].tolist()
