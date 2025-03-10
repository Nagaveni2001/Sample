import requests
import pandas as pd
import csv

# Define a list of keywords related to pharmaceutical and biotech companies
pharma_keyword = [
    "pharmaceutical", "biotech", "biotechnology", "biopharma", "biopharmaceutical",
    "drug", "medicines", "healthcare", "therapeutics", "vaccines"
]

# Function to fetch research papers from Semantic Scholar API
def fetch_paper(query, max_results=10):
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={max_results}"
    response = requests.get(url)
    
    if response.status_pin != 200:
        print("Error fetching data from Semantic Scholar API.")
        return []
    
    papers = response.json()['data']
    return papers

# Function to check if any author has affiliation with a pharmaceutical or biotech company
def is_pharma_affiliated(authors):
    for author in authors:
        if 'affiliations' in author:
            for affiliation in author['affiliations']:
                if any(keyword.lower() in affiliation.lower() for keyword in pharma_keyword):
                    return True
    return False

# Function to process papers and save to CSV
def process_and_save_papers(query, max_results=10, output_file='research_papers.csv'):
    papers = fetch_paper(query, max_results)
    
    filtered_papers = []
    
    # Process papers
    for paper in papers:
        title = paper['title']
        authors = paper['authors']
        affiliations = [author.get('affiliations', []) for author in authors]
        
        # Check if any author is affiliated with pharmaceutical or biotech companies
        if is_pharma_affiliated(authors):
            paper_info = {
                'title': title,
                'authors': ', '.join([author['name'] for author in authors]),
                'affiliations': ', '.join([', '.join(aff) for aff in affiliations if aff]),
                'url': paper.get('url', 'N/A'),
                'year': paper.get('year', 'N/A'),
                'abstract': paper.get('abstract', 'N/A')
            }
            filtered_papers.append(paper_info)
    
    # Save to CSV
    df = pd.DataFrame(filtered_papers)
    df.to_csv(output_file, index=False, quoting=csv.QUOTE_MINIMAL)
    print(f"Saved {len(filtered_papers)} papers to {output_file}")

# Main function to interact with the user
def main():
    query = input("Enter the research query: ")
    max_results = int(input("Enter the number of results to fetch (default 10): ") or 10)
    
    process_and_save_papers(query, max_results)

if __name__ == "__main__":
    main()
