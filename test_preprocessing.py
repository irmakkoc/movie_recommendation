"""
    This file is for testing the file filtered_movies.csv
    that was created by preprocessing the
    TMDB_movies.csv dataset

"""

import pandas as pd


df= pd.read_csv("filtered_movies.csv")
df_rows = df[df['genres'].isna() & df['keywords'].isna()]
    
print("-------------------------------------------")    
# Print the count of such rows
print(f"Number of rows with null values in 'keywords' and 'genres': {len(df_rows)}") #check null value rows number

num_duplicates = df.duplicated().sum() #check if there is still duplicate rows
    
print(f"Number of duplicate rows in df: {num_duplicates}")
#print(f"Number of rows in df: {len(df)}") #there were 1180936 lines
print(f"Number of rows in df: {len(df)}") #there is 351175 lines
    
print("Missing values per column:\n", df.isna().sum())

# Drop NaN values to avoid errors
df['genres'] = df['genres'].dropna()

# Split genres by comma and flatten the list
all_genres = df['genres'].str.split(',').explode().str.strip()

# Get unique genre names
unique_genres = all_genres.unique()
# Print unique genres
print("Unique genres:\n", unique_genres)
    
# Drop NaN values to avoid errors
df['keywords'] = df['keywords'].dropna()

# Split genres by comma and flatten the list
all_keywords = df['keywords'].str.split(',').explode().str.strip()

# Get unique genre names
unique_keywords = all_keywords.unique()

# Print unique keywords
print("Unique keywords:\n", unique_keywords)