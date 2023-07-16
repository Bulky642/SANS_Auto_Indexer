import pandas as pd

# Initializing empty dictionary
data = {}

# Iterating through all 5 files, adjust to number of books +1 if your course has more or less
for i in range(1, 6):
    # Loading CSV file
    df = pd.read_csv(f'GPCS_Index_Book_{i}.csv')

    # Iterating through each row
    for index, row in df.iterrows():
        term = row['Term']
        pages = row['Pages']
        definition = row['Definition']

        # If term is not already in dictionary
        if term not in data:
            data[term] = {"B1": "", "B2": "", "B3": "", "B4": "", "B5": "", "Definition": ""}

        # Adding page number and definition
        data[term][f"B{i}"] = pages
        data[term]['Definition'] += " " + definition

# Transforming dictionary to dataframe
final_df = pd.DataFrame.from_dict(data, orient='index')
final_df.reset_index(inplace=True)
final_df = final_df.rename(columns={'index':'Term'})

# Saving to composite CSV
final_df.to_csv('GPCS_Composite.csv', index=False)
