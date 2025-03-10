import requests
import pandas as pd
from typing import List


PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def fetch_pubmed_ids(query: str, max_results: int = 20) -> List[str]:
    params = {
        'db': 'pubmed',
        'term': query,
        'retmax': max_results,
        'usehistory': 'y',
        'retmode': 'xml'
    }
    response = requests.get(PUBMED_SEARCH_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching PubMed IDs: {response.text}")
    
    pubmed_ids = []
    from xml.etree import ElementTree
    root = ElementTree.fromstring(response.content)
    for id_elem in root.findall(".//Id"):
        pubmed_ids.append(id_elem.text)
    return pubmed_ids


def fetch_paper_details(pubmed_ids: List[str]) -> List[dict]:
    details = []
    ids_str = ",".join(pubmed_ids)
    params = {
        'db': 'pubmed',
        'id': ids_str,
        'retmode': 'xml',
        'tool': 'get-papers-list',
        'email': 'your-email@example.com'
    }
    response = requests.get(PUBMED_FETCH_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"Error fetching paper details: {response.text}")
    
    from xml.etree import ElementTree
    root = ElementTree.fromstring(response.content)
    for docsum in root.findall(".//DocSum"):
        paper = {}
        for item in docsum.findall(".//Item"):
            name = item.get('Name')
            value = item.text
            if name == 'Title':
                paper['Title'] = value
            elif name == 'Source':
                paper['Publication Date'] = value
            elif name == 'Author':
                paper['Authors'] = value
            elif name == 'Email':
                paper['Corresponding Author Email'] = value
        details.append(paper)
    
    return details


def filter_papers_with_company_affiliation(papers: List[dict], companies: List[str]) -> List[dict]:
    filtered_papers = []
    for paper in papers:
        authors = paper.get('Authors', '')
        for company in companies:
            if company.lower() in authors.lower():
                paper['Company Affiliation(s)'] = company
                filtered_papers.append(paper)
                break
    return filtered_papers


def save_papers_to_csv(papers: List[dict], filename: str):
    df = pd.DataFrame(papers)
    df.to_csv(filename, index=False)


def fetch_and_process_papers(query: str, companies: List[str], max_results: int = 20, output_file: str = None):
    pubmed_ids = fetch_pubmed_ids(query, max_results)
    papers = fetch_paper_details(pubmed_ids)
    filtered_papers = filter_papers_with_company_affiliation(papers, companies)
    
    if output_file:
        save_papers_to_csv(filtered_papers, output_file)
    else:
        print(pd.DataFrame(filtered_papers))
