import pandas as pd

"""""
df = pd.read_csv('TMDB_movies.csv')

print("Vote Average Column Stats:")
print(df['vote_average'].describe())  # Shows min, max, mean, etc.
print(f"Data type before conversion: {df['vote_average'].dtype}")
df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')


count_above_6000 = len(df[df['vote_average'] >= 0.6])
print(f"Number of movies with vote_average >= 0,6: {count_above_6000}")
"""""

def preprocess_movies(input_file = 'TMDB_movies.csv', output_file='filtered_movies.csv'):
    df = pd.read_csv(input_file)

    df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
    df_filtered = df[df['vote_average'] > 0]
    df_filtered = df[df['vote_average'] >= 6.0]
    
    #df_filtered = df[df['vote_average'] >= 0.6] #leave only movies with rating more than 0.6 in the range of 0-1
    df_filtered.to_csv(output_file, index=False) #save the preprocessed dataframe into output_file
    df_filtered = df_filtered.drop_duplicates() #drops the duplicate rows from the dataset

    
    
    df_filtered = df_filtered.dropna(subset=['genres', 'keywords'], how='all') #drop rows if both genres and keywords columns are empty

    df_filtered.to_csv(output_file, index=False)
    return df_filtered
    
    
#preprocess_movies()
"""
df=pd.read_csv('filtered_movies.csv')
# Drop rows with NaN genres (optional, if any exist)
df = df.dropna(subset=['genres'])

# Split by comma, strip whitespace, flatten the list
all_genres = df['genres'].str.split(',').explode().str.strip()

# Get unique genres
unique_genres = sorted(all_genres.unique())

# Print the result
print(unique_genres)
"""
# Load the CSV file
movies_df = pd.read_csv('filtered_movies.csv')

# Exclude rows where the 'adult' column is True (as string or boolean)
filtered_df = movies_df[movies_df['adult'].astype(str).str.lower() != 'true']

# Save the filtered DataFrame back to the CSV file
filtered_df.to_csv('filtered_movies.csv', index=False)




