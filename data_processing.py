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
    df_filtered = df[df['vote_average'] >= 0.6] #leave only movies with rating more than 0.6 in the range of 0-1
    df_filtered.to_csv(output_file, index=False) #save the preprocessed dataframe into output_file
    df_filtered = df_filtered.drop_duplicates() #drops the duplicate rows from the dataset

    
    
    df_filtered = df_filtered.dropna(subset=['genres', 'keywords'], how='all') #drop rows if both genres and keywords columns are empty

    df_filtered.to_csv(output_file, index=False)
    return df_filtered
    
    
preprocess_movies()




