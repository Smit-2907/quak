import pandas as pd
try:
    df = pd.read_excel('dataset.xlsx')
    print("ALL_COLUMNS_START")
    for col in df.columns:
        print(col)
    print("ALL_COLUMNS_END")
    
    # Print first row to see data samples
    print("FIRST_ROW_START")
    print(df.iloc[0])
    print("FIRST_ROW_END")
except Exception as e:
    print("Error reading excel:", e)
