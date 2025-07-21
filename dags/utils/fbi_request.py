import requests
import json
import pandas as pd

# --- API Request ---
response = requests.get('https://api.fbi.gov/wanted/v1/list', params={'page': 1})
data = json.loads(response.content)
items = data.get('items', [])
df = pd.DataFrame(items)

# --- Column Overview ---
print(" Columns in DataFrame:")
print(df.columns.tolist())
print("\n First 5 rows:")
print(df.head())

# --- Missing Values ---
print("\n Missing Values (Count and %):")
missing_info = pd.DataFrame({
    'missing_count': df.isnull().sum(),
    'missing_percent': (df.isnull().mean() * 100).round(2)
})
print(missing_info.sort_values(by='missing_count', ascending=False))

# --- Unique Values (Handle unhashable types like list/dict) ---
print("\n Unique Values per Column:")
for col in df.columns:
    try:
        unique_vals = df[col].nunique()
    except TypeError:
        # Handle unhashable types (list/dict)
        unique_vals = df[col].apply(lambda x: str(x)).nunique()
    print(f"• {col}: {unique_vals} unique values")

# --- Optional: Check datatypes ---
print("\n Data Types:")
print(df.dtypes)
print(df["images"][1])
