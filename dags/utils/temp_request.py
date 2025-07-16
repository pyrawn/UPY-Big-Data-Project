import requests
import pandas as pd

# API endpoint
url = "https://www.arbeitnow.com/api/job-board-api?search=&tags=&sort_by=newest&page=2"

# Send GET request
response = requests.get(url)

# Confirm response type
print(response.headers.get('Content-Type'))

# Load JSON data
data = response.json()

# OPTIONAL: Pretty print to inspect structure
from pprint import pprint
pprint(data)

# Convert to DataFrame (adjust path depending on JSON structure)
df = pd.json_normalize(data['data'])  # assuming the jobs are under 'data'


# Print DataFrame and columns
print(df)
print("\nColumns:")
print(df.columns)

print(df["slug"])
print(df["company_name"])
print(df["title"])
print(df["description"])
print(df["remote"])
print(df["url"])
print(df["tags"])
print(df["job_types"])
print(df["location"])
print(df["created_at"])