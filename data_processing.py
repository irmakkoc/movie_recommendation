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

def preprocess_movies(input_file = 'TMDB_movies.csv', output_file='cleaned_movies.csv'):
    df = pd.read_csv(input_file)

    df['vote_average'] = pd.to_numeric(df['vote_average'], errors='coerce')
    df_filtered = df[df['vote_average'] >= 0.6] #leave only movies with rating more than 0.6 in the range of 0-1
    df_filtered.to_csv(output_file, index=False) #save the preprocessed dataframe into output_file

    
    print(f"Number of rows in df_filtered: {len(df)}") #there were 1180936 lines
    print(f"Number of rows in df_filtered: {len(df_filtered)}") #there is 351175 lines

preprocess_movies()
