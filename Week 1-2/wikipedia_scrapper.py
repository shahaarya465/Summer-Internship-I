import requests
import pandas as pd
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import seaborn as sns

# scrape and get all the tables 
def get_tables_from_url(url):
    print(f"\nScraping URL: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    tables = pd.read_html(response.text)
    print(f"Found {len(tables)} table(s).")

    return tables

# select the table to view
def select_table(tables):
    print("\nTable Previews:")
    for i, table in enumerate(tables):
        print(f"\nTable {i}:")
        print(table.head(3))

    index = int(input(f"\nEnter the table number (0 to {len(tables)-1}): "))
    return tables[index]

# general business analysis
def business_analysis(df):
    print("\nSummary Statistics:")
    print(df.describe(include='all'))

    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        plt.figure(figsize=(6, 4))
        sns.histplot(df[col], kde=True)
        plt.title(f"Distribution of {col}")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

# run
def run_agent():
    url = input("Enter the URL to analyze: ").strip()
    try:
        tables = get_tables_from_url(url)
        df = select_table(tables)

        print("\nSelected table preview:")
        print(df.head())

        business_analysis(df)

        df.to_csv("wikipedia_analysis.csv", index=False)
        print("\nSaved as 'wikipedia_analysis.csv'.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_agent()