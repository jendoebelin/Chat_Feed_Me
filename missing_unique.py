import pandas as pd

def remove_duplicates_from_csv(filename):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(filename)

    # Drop duplicates in the 'food' column and keep the first occurrence
    df = df.drop_duplicates(subset='food', keep='first')

    # Overwrite the original CSV file with the updated DataFrame
    df.to_csv(filename, index=False)

if __name__ == "__main__":
    remove_duplicates_from_csv("missing.csv")
