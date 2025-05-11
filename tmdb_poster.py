# tmdb_poster.py

import requests

TMDB_API_KEY = "9c91b18187d811058d6e72368a39bf12"

def fetch_movie_poster(title):
    try:
        url = "https://api.themoviedb.org/3/search/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "query": title,
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data["results"]:
            poster_path = data["results"][0].get("poster_path")
            if poster_path:
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception as e:
        print(f"Error fetching poster for '{title}':", e)

    # fallback placeholder if not found
    return "https://via.placeholder.com/300x450?text=No+Image"
