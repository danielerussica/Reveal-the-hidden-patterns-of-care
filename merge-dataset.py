import pandas as pd

base_filename = "data_css_challenge_"

df_list = [
    pd.read_csv(
        f"data/{base_filename}{i}.csv",
        dtype=str,           
        encoding="utf-8",    
        on_bad_lines='skip', # Corretto da False a 'skip'
        engine="python"      
    )
    for i in range(10)
]

merged_df = pd.concat(df_list, ignore_index=True)
merged_df.to_csv("data/data_css_challenge.csv", index=False)