import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the page
url = "https://www.hdb.gov.sg/residential/selling-a-flat/overview/resale-statistics"

# Headers to mimic a real browser (optional, but helps)
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# Get the page
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "lxml")

# Look for tables
tables = soup.find_all("table")

# Check tables for the one with "Resale Price Index" or similar header
for i, table in enumerate(tables):
    if "% Change from Previous Quarter" in table.text:
        print(f"Found potential RPI table at index {i}")
        df = pd.read_html(str(table))[0]
        print(df.head())
        break
