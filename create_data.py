import pandas as pd
import os
def combine_csv(folder_path, output_file):
    dataframes = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        df = pd.read_csv(file_path)
        dataframes.append(df)
    combined_data = pd.concat(dataframes, ignore_index=True)  # Combine dataframes
    combined_data.to_csv(output_file, index=False, encoding="utf-8")  # Save to CSV
if __name__ == '__main__':
    df = pd.read_csv("data.csv")
    print(df.columns)
